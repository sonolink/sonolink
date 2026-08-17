const {
    buildTarget,
    getPrBody,
    extractSection,
    escapeRegExp,
    findMarkedComment,
    removeLabelSafe,
} = require("./utils.js");

const INVALID_LABEL = "status: invalid";
const REQUIRED_HEADINGS = ["## Summary", "## Type of change", "## Checklist"];
const TEMPLATE_URL =
    "https://github.com/SonoLink/sonolink/blob/main/.github/pull_request_template.md";

// Hidden in the comment body so later runs can find and edit it instead of
// posting a new one every time. Never shown to the user (HTML comments don't render)
const COMMENT_MARKER = "<!-- template-validator-comment -->";

/** Returns a reason string if enforcement should be skipped, otherwise null. */
function skipReason(pr) {
    if (pr.locked) return "is locked";
    if (pr.draft) return "is a draft";
    return null;
}

/** Checks that every required "## Heading" is present, on its own line */
function findMissingHeadings(content) {
    return REQUIRED_HEADINGS.filter((heading) => {
        const regex = new RegExp(`^${escapeRegExp(heading)}\\s*$`, "m");
        return !regex.test(content);
    }).map((heading) => `Missing required section "${heading}".`);
}

/** "Type of change" only makes sense if at least one box under it is checked */
function findUncheckedType(content) {
    const section = extractSection(content, "## Type of change");
    if (section !== null && !/^-\s*\[[xX]\]/m.test(section)) {
        return 'No checkbox selected under "## Type of change".';
    }
    return null;
}

/** Returns one problem string per unchecked box under "## Checklist" (all required) */
function findUncheckedChecklistItems(content) {
    const section = extractSection(content, "## Checklist");
    if (section === null) return [];

    // Accept both "-" and "*" bullets since gh's checkbox UI can rewrite either way
    const itemRegex = /^[-*]\s*\[([ xX])\]\s*(.+)$/gm;
    const problems = [];
    let match;
    while ((match = itemRegex.exec(section)) !== null) {
        const [, box, text] = match;
        if (box === " ") {
            problems.push(`Checklist item not completed: "${text.trim()}".`);
        }
    }
    return problems;
}

function validateTemplate(content) {
    const problems = findMissingHeadings(content);
    const uncheckedType = findUncheckedType(content);
    if (uncheckedType) problems.push(uncheckedType);
    problems.push(...findUncheckedChecklistItems(content));
    return problems;
}

function buildProblemComment(problems) {
    return [
        COMMENT_MARKER,
        "This PR does not follow the template provided by the repository.",
        "",
        "Please make sure you use and fill our pull request template with all required sections provided.",
        `(You can visit [.github/pull_request_template.md](${TEMPLATE_URL}) too see the template.)`,
        "",
        "The problems detected were:",
        "",
        "```",
        problems.join("\n"),
        "```",
    ].join("\n");
}

function buildResolvedComment() {
    return [
        COMMENT_MARKER,
        "Thanks, this PR now follows the template. Nothing else needed here.",
    ].join("\n");
}

module.exports = async ({ github, context, core }) => {
    const pr = context.payload.pull_request;
    const prNumber = pr.number;
    const target = buildTarget(context, prNumber);

    const skip = skipReason(pr);
    if (skip) {
        core.info(
            `The PR #${prNumber} ${skip}, skipping template enforcement.`,
        );
        return;
    }

    const prContent = getPrBody(pr);
    if (prContent === null) {
        core.setFailed("There is no PR description.");
        return;
    }

    const problems = validateTemplate(prContent);
    core.debug(
        `Checklist section extracted: ${JSON.stringify(extractSection(prContent, "## Checklist"))}`,
    );
    const existingComment = await findMarkedComment(
        github,
        target,
        COMMENT_MARKER,
    );

    // Valid PR
    if (problems.length === 0) {
        core.info(`PR #${prNumber} follows the template.`);
        if (pr.labels.some((l) => l.name === INVALID_LABEL)) {
            await removeLabelSafe(github, target, INVALID_LABEL, core);
        }
        if (existingComment) {
            await github.rest.issues.updateComment({
                ...target,
                comment_id: existingComment.id,
                body: buildResolvedComment(),
            });
        }
        return;
    }

    // Invalid PR
    await github.rest.issues.addLabels({ ...target, labels: [INVALID_LABEL] });
    const body = buildProblemComment(problems);
    if (existingComment) {
        await github.rest.issues.updateComment({
            ...target,
            comment_id: existingComment.id,
            body,
        });
    } else {
        await github.rest.issues.createComment({ ...target, body });
    }
    core.setFailed(`PR #${prNumber} does not follow the template.`);
};
