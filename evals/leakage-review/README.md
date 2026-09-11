# Recorded leakage-review exercise

One independent agent exercise was executed on 2026-09-11 in Codex, using
`ds-leakage-audit`. This is a qualitative development check, not a comparative
benchmark or a reproducible claim about every model or client. The exact model
snapshot and sampling configuration were not exposed by the runtime and were not
recorded; outputs from another run can differ.

## Request supplied to the evaluator

> Review this subscription model before we trust the reported 0.99 ROC AUC.
> Check the provided project artifacts and produce leakage_audit.md with evidence
> and practical next steps.

The evaluator received the skill and only the four [input artifacts](input/).
It did not receive an answer key or the author's suspected findings. All inputs
are fictional. The score is a claim in the fictional brief, not an executed result.
There is deliberately no training dataset or experiment history. Do not run the
fixture's `train.py`; it is the flawed code being reviewed.

## Observed outcome

Read the [complete audit](observed-audit.md). Its file references and hashes point
to the unchanged inputs. Only the temporary directory name was replaced by the
portable `input/` label when exporting the audit.

The supervising reviewer checked the output against the supplied code and found:

- It identified imputation and category construction before the split.
- It explained why a random split does not evaluate the future-period use case.
- It identified missing point-in-time controls in the cancellation join while
  distinguishing actual code evidence from unknown field availability.
- It treated repeated existing customers as a temporal-design question, without
  automatically imposing an unseen-customer evaluation objective.
- It kept the score, missing data, selection history, and corrected performance
  explicitly unverified. It did not fabricate a training run.

These observations support this one leakage-review handoff. They do not validate
the other eleven skills or the full [proposed scenario suite](../../docs/evaluation-scenarios.md).

## Repeat the exercise

Give an independent agent the current
[ds-leakage-audit](../../skills/ds-leakage-audit/SKILL.md), the input directory, and
the request above. Do not include the observed audit. Record client/model/version,
skill revision, prompt, output, and unexpected behavior. Compare evidence handling
and practical conclusions, rather than requiring identical wording.
