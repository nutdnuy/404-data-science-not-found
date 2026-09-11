# Roadmap

This is a proposed development sequence. Items are not promises of compatibility, evaluated agent behavior, model performance, or delivery dates.

## v0.1 — A reviewable path through a data project

Initial scope:

- Twelve composable skills: `ds-requirements`, `ds-solution-design`, `ds-eda`, `ds-data-cleaning`, `ds-insight`, `ds-feature-engineering`, `ds-model-development`, `ds-model-evaluation`, `ds-inference`, `ds-report`, `ds-leakage-audit`, and `ds-pipeline`.
- Explicit input, output, and handoff expectations, including an analytics-only route.
- A runnable synthetic subscription-retention reference example with reproducible artifacts and stated limitations.
- Proposed evaluation scenarios for leakage, splitting, causal claims, holdout reuse, missing data, inference contracts, untrusted data instructions, and descriptive analysis.
- Installation instructions, contribution guidance, and reproducible issue templates.

Release evidence should include a clean quickstart run, validation of skill structure and references, and checks of the reference example. Keep evaluation scenarios labeled proposed until they have been executed and their records published. A working example does not validate model outcomes on real business data.

## Next — Evaluate the handoffs

- Run the proposed scenarios on explicitly recorded agent and model versions.
- Publish prompts, synthetic fixtures, inspectable output references, and failures alongside successful runs.
- Test installation and discovery on additional agent clients before naming them as supported.
- Improve one weak handoff at a time based on reproducible reports.

Exit condition: another contributor can reproduce the recorded scenario outcomes with the documented environment, or can identify and explain differences.

## Later — Add depth where users demonstrate a need

- A time-series example with realistic label availability and rolling evaluation.
- A documented path for experiment analysis that separates association from causal identification.
- Larger-data patterns and clearer storage boundaries, without requiring a cloud vendor.
- Domain-specific extensions only when maintainers can supply a small public or synthetic example and meaningful acceptance scenarios.

Prioritize correctness, first-run success, and useful artifacts over the number of skills. Production deployment, regulatory validation, and domain-specific decisions need their own requirements and evidence; this roadmap does not imply they are covered.
