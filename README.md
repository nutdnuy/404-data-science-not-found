# Data Science Skills

**Your model's best feature might be cheating.**

12 composable agent skills for taking a business question through data exploration,
cleaning, modeling, inference, and an evidence-backed report.

[ภาษาไทย](README.th.md) · [Pick a skill](#pick-a-skill) · [Run the demo](#run-the-demo) · [Contribute](CONTRIBUTING.md)

```bash
npx skills add nutdnuy/data-science-skills
```

Start with a question your agent should ask before celebrating a score:

```text
Use ds-leakage-audit to review this churn model. For each feature,
show whether it actually exists at prediction time. Save the evidence.
```

## Why use these?

A notebook can run successfully while answering the wrong question. These skills
ask your agent to make the decisions that a score alone cannot justify:

- Define the business decision, observation unit, target, and prediction time.
- Protect a final holdout before target-aware exploration and model selection.
- Compare a candidate against a simple baseline, including a rule when relevant.
- Trace reported numbers to executed code, artifacts, and data versions.
- Keep preprocessing consistent between training and inference.

They are readable Markdown instructions. Use one inside an existing project or
compose a workflow. They do not require a hosted service or a project framework.
They guide an agent; they do not mechanically guarantee correct analysis.

## Install and use

The [open skills CLI](https://github.com/vercel-labs/skills) installs this format
for Codex, Claude Code, Cursor, and other supported agents. Node.js is needed for
the installer; Python 3.10+ is only needed for the reference demo.

```bash
# Inspect available skills first
npx skills add nutdnuy/data-science-skills --list

# Install just the leakage review into your project
npx skills add nutdnuy/data-science-skills --skill ds-leakage-audit

# Or choose skills and agents interactively
npx skills add nutdnuy/data-science-skills
```

Then ask your agent in ordinary language to use the skill by name. Some clients
also offer slash commands or `$skill-name` shortcuts; invocation differs by client.
Restart or refresh the client if its skill list has not updated.

For manual installation, copy one complete folder from `skills/` to your client's
documented project skill directory. Each skill is self-contained. You can also
read its `SKILL.md` and explicitly ask your agent to follow it for your current task.

## Pick a skill

| When you need to… | Skill | Default evidence |
| --- | --- | --- |
| Turn a vague request into a measurable decision | [ds-requirements](skills/ds-requirements/SKILL.md) | `requirement.md` |
| Decide whether rules, analysis, or ML are appropriate | [ds-solution-design](skills/ds-solution-design/SKILL.md) | `req_analysis.md` |
| Explore data without contaminating evaluation | [ds-eda](skills/ds-eda/SKILL.md) | `eda_analysis.py`, `eda_analysis.md` |
| Clean data with an auditable change trail | [ds-data-cleaning](skills/ds-data-cleaning/SKILL.md) | `cleaning.py`, `data_quality.md` |
| Turn patterns into qualified business insights | [ds-insight](skills/ds-insight/SKILL.md) | `insight.md` |
| Build features available at prediction time | [ds-feature-engineering](skills/ds-feature-engineering/SKILL.md) | `features.py`, `feature_dictionary.md` |
| Split, establish baselines, select, and tune a model | [ds-model-development](skills/ds-model-development/SKILL.md) | `train.py`, `experiment_log.md` |
| Evaluate a frozen candidate and explain limits | [ds-model-evaluation](skills/ds-model-evaluation/SKILL.md) | `evaluation.md`, `model_card.md` |
| Make repeatable predictions with a schema contract | [ds-inference](skills/ds-inference/SKILL.md) | `predict.py`, `inference_contract.md` |
| Write a report whose claims match the evidence | [ds-report](skills/ds-report/SKILL.md) | `report.md` |
| Challenge suspiciously good results | [ds-leakage-audit](skills/ds-leakage-audit/SKILL.md) | `leakage_audit.md` |
| Coordinate a complete project or resume an existing one | [ds-pipeline](skills/ds-pipeline/SKILL.md) | `ds_project.md` and scoped stage outputs |

These filenames are defaults. Skills preserve existing project conventions and
skip stages that do not serve your question. A descriptive analysis does not
need a trained model.

## Three ways to start

**A business question**

```text
Use ds-requirements. We want to reduce subscription cancellations.
Help define what decision we can take, when we take it, and how we will
measure whether it helps. Use the information already in this project.
```

**An existing notebook**

```text
Use ds-leakage-audit on notebooks/churn.ipynb and its feature query.
Check timestamps, repeated customers, preprocessing, and holdout reuse.
Create leakage_audit.md with evidence and the smallest fixes.
```

**A complete workflow**

```text
Use ds-pipeline on the synthetic subscription-retention example.
Start from the business requirement, check the split and leakage risks,
run the analysis, and write a report based on the generated artifacts.
```

## Run the demo

The [subscription-retention example](examples/subscription-retention/README.md)
creates its own synthetic data, including a deliberately invalid feature from
after the outcome. It runs locally with no API key or dataset download.

```bash
git clone https://github.com/nutdnuy/data-science-skills.git
cd data-science-skills
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r examples/subscription-retention/requirements.txt
python examples/subscription-retention/run.py --output-dir outputs/demo
```

On Windows, activate with `.venv\Scripts\activate`.

Open `outputs/demo/report.md` to see the actual run. The
[checked-in sample](examples/subscription-retention/sample-output/report.md)
lets you inspect a report before installing anything. This is an executable
reference implementation, not evidence that an agent follows every skill.
Synthetic results establish no expected performance on real customer data.

## What is verified?

CI checks skill metadata, local documentation links, package completeness, and
the reference demo's statistical and inference invariants. The
[behavioral scenarios](docs/evaluation-scenarios.md) are a separate human/agent
evaluation protocol; a passing code test is not a skill quality benchmark.
See [validation status](docs/validation.md) for the checks actually performed.

## Contributing

Bring a failure case: a feature created after the outcome, a repeated entity
crossing splits, or a report claim that its artifacts cannot support. Small,
testable improvements are especially useful. Read [CONTRIBUTING.md](CONTRIBUTING.md)
and the [roadmap](docs/roadmap.md).

## Inspiration and license

Inspired by [Matt Pocock's skills](https://github.com/mattpocock/skills) and their
small, composable approach. This repository contains original Data Science
workflows and is independently maintained; it is not affiliated with or endorsed
by Matt Pocock. Skills use the [Agent Skills format](https://agentskills.io/specification).

[MIT](LICENSE) · Maintained by [nutdnuy](https://github.com/nutdnuy)
