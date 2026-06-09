module.exports = async ({ github, context, core }) => {
    const invalid = "status: invalid";
    const pr = context.payload.pull_request;
    const prNumber = pr.number;

    if (pr.locked) {
        core.info(
            `The PR #${prNumber} is locked, skipping template enforcement.`,
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
        if (!prContent.includes(heading)) {
            problems.push(`Missing required section "${heading}".`);
        }
    }

    if (problems.length === 0) {
        core.info(`PR #${prNumber} follows the template.`);

        if (pr.labels.find((l) => l.name === invalid)) {
            await github.rest.issues
                .removeLabel({
                    owner: context.repo.owner,
                    repo: context.repo.repo,
                    issue_number: prNumber,
                    name: invalid,
                })
                .catch(() => {});
        }
        return;
    }

    await github.rest.issues.addLabels({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
        labels: [invalid],
    });

    const fmt = problems.join("\n");
    await github.rest.issues.createComment({
        owner: context.repo.owner,
        repo: context.repo.repo,
        issue_number: prNumber,
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
