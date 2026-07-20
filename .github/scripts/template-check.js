module.exports = async ({ github, context, core }) => {
    const invalid = "status: invalid";
    const pr = context.payload.pull_request;
    const prNumber = pr.number;
    const target = {
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
    };

    if (pr.locked) {
        core.info(
            `The PR #${prNumber} is locked, skipping template enforcement.`,
        );
        return;
    }

    if (pr.draft) {
        core.info(
            `The PR #${prNumber} is a draft, skipping template enforcement.`,
        );
        return;
    }

    for (const label of pr.labels) {
        if (label.name === invalid) {
            core.info(
                `The PR #${prNumber} is flagged as invalid, skipping template enforcement.`,
            );
            return;
        }
    }

    const prContent = (pr.body || "").trim();
    if (prContent.length === 0) {
        core.setFailed("There is no PR description.");
        return;
    }

    const problems = [];
    const requiredHeadings = [
        "## Summary",
        "## Type of change",
        "## Checklist",
        "### Code & Review",
        "### Documentation & Compatibility",
        "### Validation",
    ];

    for (const heading of requiredHeadings) {
        const escaped = heading.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
        const regex = new RegExp(`^${escaped}\\s*$`, "m");
        if (!regex.test(prContent)) {
            problems.push(`Missing required section "${heading}".`);
        }
    }

    const typeSection = prContent.match(
        /^## Type of change([\s\S]*?)(?=^## )/im,
    );

    if (typeSection && !/^-\s*\[[xX]\]/m.test(typeSection[1])) {
        problems.push('No checkbox selected under "## Type of change".');
    }

    if (problems.length === 0) {
        core.info(`PR #${prNumber} follows the template.`);
        if (pr.labels.find((l) => l.name === invalid)) {
            await github.rest.issues
                .removeLabel({ ...target, name: invalid })
                .catch((err) => {
                    if (err.status !== 404) {
                        core.warning(
                            `Failed to remove ${invalid}: ${err.message}`,
                        );
                    }
                });
        }
        return;
    }

    await github.rest.issues.addLabels({ ...target, labels: [invalid] });
    const fmt = problems.join("\n");
    await github.rest.issues.createComment({
        ...target,
        body: [
            "This PR does not follow the template provided by the repository.",
            "",
            "Please make sure you use & fill our pull request template with all required sections provided.",
            "(You can go to [.github/pull_request_template.md](https://github.com/SonoLink/sonolink/blob/main/.github/pull_request_template.md) for more information on how this template is built.)",
            "",
            "The problems detected were:",
            "",
            "```",
            fmt,
            "```",
        ].join("\n"),
    });
    core.setFailed(`PR #${prNumber} does not follow the template.`);
};
