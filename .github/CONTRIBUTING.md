# Contributing to SonoLink

Thank you for your interest in improving SonoLink. This document covers how
to set up your environment, the conventions we use, and what to expect from
the review process. Please also read our
[Code of Conduct](https://github.com/sonolink/sonolink/blob/main/.github/CODE_OF_CONDUCT.md)
and [AI Contribution Policy](https://github.com/sonolink/sonolink/blob/main/.github/AI_POLICY.md)
before opening an issue or pull request. All contributions are held to both.

## Before you start

- For small fixes (typos, broken links, minor bugs), feel free to open a pull
  request directly.
- For anything larger, like new features, breaking changes, or architectural
  changes — please open an issue first to discuss the approach. This avoids
  wasted effort if the direction doesn't fit the project.
- Check existing issues and pull requests to avoid duplicating work already
  in progress.
- Fill out the pull request template. At minimum, all template sections
  must be present, at least one box under `Type of change` must be checked, and every box under
  `Checklist` must be checked before your PR can be merged. CI will flag
  the PR and block it otherwise.

## Commit and branch conventions

- Use descriptive branch names, e.g. `fix/reconnect-timeout` or
  `feat/expose-history`.
- Commit messages must follow the
  [Conventional Commits](https://www.conventionalcommits.org/) format, e.g.
  `fix(node): resolve reconnect timeout` or `feat(queue): expose history property`.
- Your **pull request title** must also follow Conventional Commits format,
  independently of your individual commit messages — this is checked
  automatically and is required for the PR to pass CI.
- Use `feat:` for new functionality, `fix:` for bug fixes, and other standard
  types (`docs:`, `refactor:`, `test:`, `chore:`, etc.) where appropriate.
- Mark breaking changes with a `!` after the type/scope (e.g. `feat!:`) or a
  `BREAKING CHANGE:` footer, as per the Conventional Commits spec.
- Keep commits focused; unrelated changes should be split into separate
  commits or pull requests.

## Issue reports

- Use the appropriate issue template (bug report or feature request).
- Include enough detail for a maintainer to understand and, where
  applicable, reproduce the problem: expected behavior, actual behavior, and
  steps to reproduce.
- One issue per report. Don't bundle multiple unrelated problems or
  requests into a single issue.

## Usage of AI

AI tools may be used when preparing contributions, but contributors are fully responsible 
for the work they submit and must be able to explain and justify it themselves. All use of 
AI must comply with the [AI Contribution Policy](https://github.com/sonolink/sonolink/blob/main/.github/AI_POLICY.md).

## Code review

- Reviews focus on correctness, maintainability, and fit with the project's
  existing design. Feedback is intended to improve the contribution, not to
  discourage the contributor.
- Maintainers may request changes, ask clarifying questions, or close
  contributions that don't meet the standards described in this document or
  in the [AI Contribution Policy](https://github.com/sonolink/sonolink/blob/main/.github/AI_POLICY.md).
- Please engage with feedback in good faith, per our
  [Code of Conduct](https://github.com/sonolink/sonolink/blob/main/.github/CODE_OF_CONDUCT.md).

## Security issues

Do not report security vulnerabilities through public issues or pull
requests. See [SECURITY.md](https://github.com/sonolink/sonolink/blob/main/.github/SECURITY.md)
for how to report them privately.

## Questions

If anything in this document is unclear, or you're unsure whether a change
is a good fit, ask in an issue or on our
[Discord server](https://discord.gg/tPHVWBPedt) before investing significant
time.
