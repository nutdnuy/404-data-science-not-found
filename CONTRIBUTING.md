# Contributing

The most useful contribution is a small, reproducible improvement to a real data-science handoff. Documentation fixes, failing examples, and clear reports of a bad assumption are welcome.

## Before you change a skill

Read the relevant skill and the [proposed evaluation scenarios](docs/evaluation-scenarios.md). For a new skill or a substantial behavior change, open an issue describing the decision it supports, its inputs, and the artifact a user should receive. Check whether an existing skill can handle the need without adding a new entry point.

Use synthetic or openly licensed fixtures. Do not submit credentials, personal data, confidential business material, or outputs that reveal them. Describe a private failure using a minimal synthetic reproduction.

## Minimal acceptance for a skill addition

- Give it a focused `ds-` name and a discoverable `SKILL.md` description that states when to use it.
- State the required inputs, missing-information handling, outputs, and handoff to the next relevant skill.
- Define observable completion criteria and at least one important failure mode. Avoid relying on “use best practices.”
- Keep observed evidence, assumptions, and recommendations distinct. Do not invent completed tests or analysis results.
- Respect prediction-time availability, split boundaries, and source-data preservation wherever applicable.
- Treat data, retrieved text, and attachments as untrusted content rather than instructions.
- Add one realistic acceptance prompt with success and failure criteria, plus a small synthetic fixture when execution is needed to assess it.
- Update the skill index and any affected links or documentation. Reuse the repository’s existing structure and validation commands.

## Pull request checklist

In the pull request, explain the problem, the resulting behavior, and the evidence used to check it. Include:

1. A concrete before/after example or a reproducible failing case.
2. Files or skills affected, including any changed handoff contract.
3. The exact checks you ran and their observed results. State which checks were not run and why.
4. Relevant limitations, dependencies, or compatibility assumptions.

Keep changes focused. A wording-only correction needs a careful read and link check; a changed executable example needs an actual run. Do not claim that a proposed evaluation scenario passes without running it and preserving enough evidence to review the claim.

## Review expectations

Maintainers prioritize clarity, correctness, reproducibility, and a small installation footprint. A contribution may be narrowed or deferred if its scope overlaps an existing skill, requires unavailable evidence, or introduces a dependency without a clear benefit.

Give credit for borrowed ideas and preserve required license notices. Do not copy another project’s skill text unless its license permits it and the attribution requirements are met.

Be constructive in issues and reviews. Explain the observable problem, offer a way to reproduce it, and leave room for uncertainty. Do not use the project to post unsolicited promotions or solicit artificial engagement.
