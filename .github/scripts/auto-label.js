const {
    buildTarget,
    getPrBody,
    extractSection,
    escapeRegExp,
    removeLabelSafe,
} = require("./utils.js");

// Checkbox text in the template -> label to apply when it's checked
const TAGS = {
    "Bug fix": "type: bugfix",
    "New feature": "idea: new feature",
    "Breaking change": "status: breaking change",
    "Refactor": "type: refactor",
    "CI / dependency update": "area: dependencies",
    "Documentation update": "type: documentation",
};

const AUTO_LABELS = new Set(Object.values(TAGS));

/** Returns the list of labels implied by checked boxes in the section */
function labelsFromSection(section) {
    return Object.entries(TAGS)
        .filter(([text]) => {
            const regex = new RegExp(
                `^-\\s*\\[[xX]\\]\\s*${escapeRegExp(text)}`,
                "im",
            );
            return regex.test(section);
        })
        .map(([, label]) => label);
}

/** Removes any auto-label that's no longer implied by the checked boxes */
async function removeStaleLabels(
    github,
    target,
    currentLabels,
    labelsToApply,
    core,
) {
    const stale = currentLabels.filter(
        (name) => AUTO_LABELS.has(name) && !labelsToApply.includes(name),
    );
    await Promise.all(
        stale.map((labelName) => {
            core.info(`Removing label: ${labelName}`);
            return removeLabelSafe(github, target, labelName, core, {
                severity: "error",
            });
        }),
    );
}

/** Adds whichever implied labels aren't already on the PR */
async function addNewLabels(
    github,
    target,
    currentLabels,
    labelsToApply,
    core,
) {
    const toAdd = labelsToApply.filter((l) => !currentLabels.includes(l));
    if (toAdd.length === 0) {
        core.info("No new labels to add.");
        return;
    }
    core.info(`Adding labels: ${toAdd.join(", ")}`);
    await github.rest.issues.addLabels({ ...target, labels: toAdd });
}

module.exports = async ({ github, context, core }) => {
    const pr = context.payload.pull_request;
    const prNumber = pr.number;
    const target = buildTarget(context, prNumber);
    const currentLabels = (pr.labels ?? []).map((l) => l.name);

    if (pr.locked) {
        core.info(`The PR #${prNumber} is locked, skipping autotag apply.`);
        return;
    }

    const prContent = getPrBody(pr);
    if (prContent === null) {
        core.setFailed("There is no PR description.");
        return;
    }

    const section = extractSection(prContent, "## Type of change");
    // Shouldn't happen in practice, because this job only runs once template-check has
    // passed (or been skipped), which already guarantees the section exists
    if (section === null) {
        core.info(
            "The Type of change section is not found. Ensure the PR follows the template.",
        );
        return;
    }

    const labelsToApply = labelsFromSection(section);

    // Independent operations on disjoint label sets; no need to serialize them
    await Promise.all([
        removeStaleLabels(github, target, currentLabels, labelsToApply, core),
        addNewLabels(github, target, currentLabels, labelsToApply, core),
    ]);
};
