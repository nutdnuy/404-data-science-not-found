# Validation status

This page distinguishes package checks, reference-code checks, and actual agent
behavior. A passing demo is not proof that a skill will guide every agent correctly.

## Package

- Twelve skill folders use the portable Agent Skills frontmatter and independent
  instruction bodies. There are no runtime dependencies between skill folders.
- `scripts/validate.py` checks names, descriptions, catalog membership, portable
  metadata, resource containment, and local documentation links.
- The official `skills` CLI **1.5.25** discovered all twelve skills in a list-only
  run. A copy installation of `ds-leakage-audit` into an isolated Codex project
  also succeeded and matched the source byte for byte. This does not establish
  every client's invocation behavior.

## Reference implementation

The [synthetic subscription-retention demo](../examples/subscription-retention/README.md)
was executed on Python **3.12.14**. Its checked-in sample includes exact dependency
versions and SHA-256 hashes for data, source code, model, and generated artifacts.

The executable tests check temporal separation and label maturity, excluded
leakage features, train-only learned transformations, unchanged fitted state when
final-test labels change, JSON model parity, invalid inference inputs,
deterministic reruns, report/metric agreement, and standalone entrypoints.

Run the maintained checks from the repository root:

```bash
python -m pip install -r requirements-dev.txt
python scripts/validate.py
python -m unittest discover -s tests -v
python examples/subscription-retention/run.py --output-dir outputs/check
```

The GitHub workflow runs these checks on Python 3.11 and 3.12. Its status is the
source of truth for remote execution; a local run is not a remote CI result.

## Agent behavior

One [independent leakage-review exercise](../evals/leakage-review/README.md) was
executed with fictional code and metadata. The complete inputs and observed output
are included, along with the limitations of the evaluation record.

The eight cases in [evaluation-scenarios.md](evaluation-scenarios.md) remain a
proposed suite. They have not been run as a controlled benchmark across named
model snapshots. No comparative quality, reliability percentage, or real-world
model-performance claim is made.
