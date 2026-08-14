const fs = require("fs");
const { readFile, writeFile } = require("./utils.js");
const { execSync } = require("child_process");

const VERSION_FILE = "sonolink/_version.py";
const CHANGELOG_FILE = "docs/changelog.rst";

// The changelog header
const INTRO_RE = new RegExp(
    String.raw`\.\. currentmodule:: [^\n]*\n\n?\.\. _whats_new:\n\n` +
        String.raw`Changelog\n=+\n\n` +
        String.raw`This page keeps a detailed human friendly rendering of what's new and changed\n` +
        String.raw`in specific versions\.\n\n`,
);

// Inserted when the changelog is missing its header
const INTRO =
    [
        ".. currentmodule:: sonolink",
        ".. _whats_new:",
        "",
        "Changelog",
        "=".repeat("Changelog".length),
        "",
        "This page keeps a detailed human friendly rendering of what's new and changed",
        "in specific versions.",
    ].join("\n") + "\n\n";

// Unreleased link and section
const UNRELEASED_LINK_RE = /\.\. _unreleased: https:\/\/[^\n]+/;
const UNRELEASED_SECTION_RE =
    /(`Unreleased`_\n-+\n\n[\s\S]*?)(?=\n\.\. _vp|\n\.\. _unreleased:|$)/;

// First release marker (anchor, link, Unreleased title, or version heading)
// Used to discard a broken header when inserting a fresh one
const BODY_START_RE =
    /(?=\.\. _vp|\.\. _unreleased:|v\d+\.\d+\.\d+ - |`Unreleased`_)/;

// Changelog categories
const CHANGELOG_CATEGORIES = [
    "Added",
    "Changed",
    "Fixed",
    "Removed",
    "Deprecated",
    "Miscellaneous",
];

// "Unreleased" section
const UNRELEASED_SECTION = [
    "`Unreleased`_",
    "-------------",
    "",
    ...CHANGELOG_CATEGORIES.flatMap((name) => [
        `**${name}**`,
        "~".repeat(name.length + 4),
        "",
    ]),
]
    .join("\n")
    .trimEnd();

// The version_info line in _version.py.
const VERSION_INFO_RE =
    /version_info = VersionInfo\(major=(\d+),\s*minor=(\d+),\s*patch=(\d+),\s*release_level="([^"]+)"\)/;

// Matches VersionInfo.as_str() in _version.py: alpha/beta/candidate get an
// "a0"/"b0"/"rc0" suffix, final gets none
const SUFFIXES = { alpha: "a0", beta: "b0", candidate: "rc0" };

// "1.4.0" without any release suffix
const versionNumber = (version) =>
    `${version.major}.${version.minor}.${version.patch}`;

let info = console.log;
let warn = console.warn;

function readVersion() {
    const { content } = readFile(VERSION_FILE);
    const match = content.match(VERSION_INFO_RE);
    if (!match) {
        throw new Error(`Could not find 'version_info' in ${VERSION_FILE}`);
    }
    const [, major, minor, patch, releaseLevel] = match;
    return {
        major: Number(major),
        minor: Number(minor),
        patch: Number(patch),
        releaseLevel,
    };
}

function versionString(version) {
    return `${versionNumber(version)}${SUFFIXES[version.releaseLevel] ?? ""}`;
}

function writeVersion(version) {
    const { content, eol } = readFile(VERSION_FILE);
    const match = content.match(VERSION_INFO_RE);

    // Bump the minor, reset the patch, and restart development on an alpha
    const bumped = {
        ...version,
        minor: version.minor + 1,
        patch: 0,
        releaseLevel: "alpha",
    };
    const line =
        `version_info = VersionInfo(major=${bumped.major}, ` +
        `minor=${bumped.minor}, patch=${bumped.patch}, ` +
        `release_level="${bumped.releaseLevel}")`;

    writeFile(VERSION_FILE, content.replace(match[0], line), eol);
    return bumped;
}

// A category header is "**Name**" immediately followed by a "~~~" underline
function isCategoryHeader(line, nextLine) {
    const name = line.replace(/\*+/g, "");
    return CHANGELOG_CATEGORIES.includes(name) && /^~+$/.test(nextLine ?? "");
}

// Splits the Unreleased section into its per-category blocks
function extractReleaseBody(section) {
    const lines = section.split("\n");
    const blocks = [];
    let title = null;
    let body = [];

    const flush = () => {
        const text = body.join("\n").trim();
        if (title && text) {
            blocks.push(`${title}\n${"~".repeat(title.length)}\n\n${text}`);
        }
        title = null;
        body = [];
    };

    let i = 0;
    while (i < lines.length) {
        if (isCategoryHeader(lines[i], lines[i + 1])) {
            flush();
            title = lines[i];
            i += 2;
            while (lines[i] === "") i += 1; // skip the blank line after the header
            continue;
        }
        body.push(lines[i]);
        i += 1;
    }
    flush();

    return blocks.join("\n\n").trimEnd();
}

function versionHeading(version) {
    const heading = `v${versionNumber(version)} - ${new Date().toISOString().slice(0, 10)}`;
    return `${heading}\n${"-".repeat(heading.length)}`;
}

// Builds the `.. _unreleased:` compare link, taking the repo owner/name from
// the workflow context (or the git remote when running locally)
function unreleasedLink(version, context) {
    let owner = context?.repo?.owner;
    let repo = context?.repo?.repo;

    if (!owner || !repo) {
        try {
            const match = execSync("git remote get-url origin", {
                encoding: "utf8",
            }).match(/(?:github\.com[:/])([^/]+)\/([^/.]+?)(?:\.git)?$/);
            if (match) {
                owner = match[1];
                repo = match[2];
            }
        } catch {
            // No git remote available (e.g. a local test)
        }
    }

    if (!owner || !repo) {
        throw new Error(
            `Could not determine repository owner/name to build the Unreleased link in ${CHANGELOG_FILE}`,
        );
    }
    return `.. _unreleased: https://github.com/${owner}/${repo}/compare/v${versionNumber(version)}..HEAD`;
}

// Updates the existing link's version (or creates one)
function buildTail(rest, version, context) {
    const linkMatch = rest.match(UNRELEASED_LINK_RE);
    const sections = rest.replace(UNRELEASED_LINK_RE, "").replace(/^\s+/, "");

    const link = linkMatch
        ? linkMatch[0].replace(
              /compare\/v[\d.]+\.\.HEAD/,
              `compare/v${versionNumber(version)}..HEAD`,
          )
        : unreleasedLink(version, context);

    return `${link}\n\n${sections}`;
}

function bumpChangelog(version, context) {
    // A missing changelog is treated as empty, so a fresh repo still works
    const { content, eol } = fs.existsSync(CHANGELOG_FILE)
        ? readFile(CHANGELOG_FILE)
        : { content: "", eol: "\n" };
    const introMatch = content.match(INTRO_RE);

    // Without a header, prepend the standard one and keep going
    let head;
    let body;
    if (introMatch) {
        head = content.slice(0, introMatch.index + introMatch[0].length);
        body = content.slice(introMatch.index + introMatch[0].length);
    } else {
        info(`Inserted the changelog header in ${CHANGELOG_FILE}`);
        head = INTRO;
        // A broken header leaves stray lines above the first release section;
        // skip them so they don't end up under the fresh header
        body = content.slice(content.match(BODY_START_RE)?.index ?? 0);
    }

    const anchor = `.. _vp${version.major}p${version.minor}p${version.patch}:`;
    const unreleased = body.match(UNRELEASED_SECTION_RE);

    // Guard against running twice for the same release (e.g. a re-publish)
    if (unreleased && body.includes(anchor)) {
        warn(
            `Release section for v${versionNumber(version)} already exists in ${CHANGELOG_FILE}, skipping changelog update`,
        );
        return;
    }

    // The Unreleased notes become the new release section
    const releaseSection = unreleased
        ? `${anchor}\n\n${versionHeading(version)}\n\n${extractReleaseBody(unreleased[1])}\n\n`
        : "";

    // Everything up to the Unreleased section (or just the intro) stays verbatim
    const [headEnd, tailStart] = unreleased
        ? [unreleased.index, unreleased.index + unreleased[0].length]
        : [0, 0];
    const kept = `${head}${body.slice(0, headEnd)}`;
    const tail = buildTail(body.slice(tailStart), version, context);

    writeFile(
        CHANGELOG_FILE,
        `${kept}${UNRELEASED_SECTION}\n\n${releaseSection}${tail}`,
        eol,
    );
    info(
        unreleased
            ? `Moved Unreleased changes into the v${versionNumber(version)} section of ${CHANGELOG_FILE}`
            : `Introduced an Unreleased section in ${CHANGELOG_FILE}`,
    );
}

module.exports = async ({ core, context } = {}) => {
    if (core) {
        info = core.info.bind(core);
        warn = core.warning.bind(core);
    }

    const currentVersion = readVersion();
    info(`Current version: ${versionString(currentVersion)}`);

    bumpChangelog(currentVersion, context);

    const bumped = writeVersion(currentVersion);
    const newVersion = versionString(bumped);
    info(`Bumped version to: ${newVersion}`);

    if (core) {
        core.exportVariable("NEW_VERSION", newVersion);
    }
};
