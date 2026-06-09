module.exports = async ({ github, context, core }) => {
    const tags = {
        "Bug fix": "type: bugfix",
        "New feature": "idea: new feature",
        "Breaking change": "status: breaking change",
        "Refactor / internal cleanup": "type: refactor",
        "CI / dependency update": "area: dependencies",
        "Documentation update": "type: documentation",
    };
    const autoLabels = new Set(Object.values(tags));
    const pr = context.payload.pull_request;
    const prNumber = pr.number;
    const currentLabels = (pr.labels ?? []).map((l) => l.name);

    if (pr.locked) {
        core.info(`The PR #${prNumber} is locked, skipping autotag apply.`);
        return;
    }

    const prContent = (pr.body || "").trim();
    if (prContent.length === 0) {
        core.setFailed("There is no PR description.");
        return;
    }

    const match = prContent.match(/## Type of change([\s\S]*?)## Checklist/i);

    // This should not happpen as this job waits for the template vaildator
    // to return successfully.
    if (!match) {
        core.info(
            "The Type of change section is not found. Ensure the PR follows the template.",
        );
        return;
    }

    const section = match[1].replace(/\r\n/g, "\n");
    const labelsToApply = [];

    for (const [text, label] of Object.entries(tags)) {
        const regex = new RegExp(`^-\\s*\\[[xX]\\]\\s*${text}`, "im");
        if (regex.test(section)) {
            labelsToApply.push(label);
        }
    }

    for (const labelName of currentLabels) {
        if (autoLabels.has(labelName) && !labelsToApply.includes(labelName)) {
            core.info(`Removing label: ${labelName}`);
            await github.rest.issues
                .removeLabel({
                    owner: context.repo.owner,
                    repo: context.repo.repo,
                    issue_number: prNumber,
                    name: labelName,
                })
                .catch((err) =>
                    core.error(`Failed to remove ${labelName}: ${err.message}`),
                );
        }
    }

    const newLabelsToAdd = labelsToApply.filter(
        (l) => !currentLabels.includes(l),
    );

    if (newLabelsToAdd.length > 0) {
        core.info(`Adding labels: ${newLabelsToAdd.join(", ")}`);
        await github.rest.issues.addLabels({
            owner: context.repo.owner,
            repo: context.repo.repo,
            issue_number: prNumber,
            labels: newLabelsToAdd,
        });
    } else {
        core.info("No new labels to add.");
    }
};
