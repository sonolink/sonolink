// Escapes regex special characters so a plain string can be dropped into a `new RegExp(...)`.
function escapeRegExp(str) {
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

// Shape that github.rest.issues.* calls expect (owner/repo/issue_number).
function buildTarget(context, prNumber) {
    return {
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
    };
}

/** Returns the trimmed PR body, or null if it's empty. */
function getPrBody(pr) {
    const body = (pr.body || "").trim();
    return body.length > 0 ? body : null;
}

/**
 * Extracts the body of a "## Heading" section, up to the next "## " heading
 * or the end of the document — whichever comes first.
 *
 * Normalizes CRLF to LF before matching so the regex doesn't have to care
 * about line endings (PR bodies can go either way).
 */
function extractSection(content, heading) {
    const normalized = content.replace(/\r\n/g, "\n");
    const regex = new RegExp(
        `^${escapeRegExp(heading)}([\\s\\S]*?)(?=^## |$(?![\\s\\S]))`,
        "im",
    );
    const match = normalized.match(regex);
    return match ? match[1] : null;
}

/**
 * Finds a previous bot comment on the PR by looking for a hidden marker
 * (an html comment, invisible when rendered) embedded in its body.
 */
async function findMarkedComment(github, target, marker) {
    const comments = await github.paginate(
        github.rest.issues.listComments,
        target,
    );
    return comments.find((c) => c.body.includes(marker)) ?? null;
}

/** Removes a label, treating "label not present" (404) as success rather than an error. */
async function removeLabelSafe(
    github,
    target,
    labelName,
    core,
    { severity = "warning" } = {},
) {
    try {
        await github.rest.issues.removeLabel({ ...target, name: labelName });
    } catch (err) {
        if (err.status !== 404) {
            core[severity](`Failed to remove ${labelName}: ${err.message}`);
        }
    }
}

module.exports = {
    escapeRegExp,
    buildTarget,
    getPrBody,
    extractSection,
    findMarkedComment,
    removeLabelSafe,
};
