# Early Warning Signals: Detecting Hidden Coordination and Goal Drift in AI Agent Swarms

A small research prototype that evaluates rule-based warning signals for four behaviours in a simulated multi-agent workflow:

- Hidden coordination
- Goal drift
- Supervisor bypass
- Concealment (hiding)

The prototype compares a lexical baseline (V1), an extended rule-based detector (V2), and a revised rule-based detector (V2.1). It evaluates both a full audit log and a restricted supervisor-visible log.

> **Scope:** This is a research prototype using manually authored synthetic scenarios. It is not a production security monitor, does not understand agent intent, and must not be used for autonomous enforcement or punitive decisions.

## Repository layout

```text
.
├── detector.py
├── detector_v2.py
├── detector_v2_1.py
├── evaluate_dataset.py
├── evaluate_independent_dataset.py
├── evaluate_independent_dataset_v2_1.py
├── experiment.py
├── generate_dataset.py
├── generate_independent_dataset.py
├── tests/
│   └── test_detector_v2_1.py
├── docs/
│   └── research_report.md
└── results/
    ├── dataset/
    └── independent_dataset/
```

Generated JSONL logs and evaluation summaries are included so that the reported experiments can be inspected without first regenerating the data.

## Requirements

- Python 3.10 or newer
- Python standard library only; no third-party packages are required

## Quick start

Run commands from the repository root.

### 0. Run the initial simulated environment

```bash
python experiment.py
python detector.py
```

This creates the five initial scenario logs in `results/` and runs the earliest baseline detector.

### 1. Reproduce the original development dataset

```bash
python generate_dataset.py
python detector_v2.py
```

The dataset contains 50 scenarios: 10 normal scenarios and 10 for each threat category. Each scenario has a full audit log and a supervisor-visible log.

### 2. Generate and evaluate the separate challenge dataset

```bash
python generate_independent_dataset.py
python evaluate_independent_dataset.py
python evaluate_independent_dataset_v2_1.py
```

The challenge generator writes 50 scenarios and keeps ground-truth labels in `evaluation_metadata.json`, separate from the event logs. The V2.1 evaluator reports V1, V2, and V2.1 results side by side.

### 3. Run unit tests

```bash
python -m unittest discover -s tests -v
```

### 4. Check syntax

```bash
python -m compileall -q .
```

## Results

### Original development dataset

| Log view | Detector | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Full audit | V1 | 14 | 0 | 26 | 10 | 1.000 | 0.350 | 0.519 |
| Full audit | V2 | 40 | 0 | 0 | 10 | 1.000 | 1.000 | 1.000 |
| Supervisor-visible | V1 | 12 | 0 | 28 | 10 | 1.000 | 0.300 | 0.462 |
| Supervisor-visible | V2 | 20 | 0 | 20 | 10 | 1.000 | 0.500 | 0.667 |

V2 was developed after inspecting the original development scenarios. Its perfect full-audit score is therefore a development-set result, not evidence of generalization.

### Separate challenge dataset: V1 vs V2 vs V2.1

| Log view | Detector | TP | FP | FN | TN | Precision | Recall | F1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Full audit | V1 | 13 | 0 | 27 | 10 | 1.000 | 0.325 | 0.491 |
| Full audit | V2 | 20 | 0 | 20 | 10 | 1.000 | 0.500 | 0.667 |
| Full audit | V2.1 | 31 | 0 | 9 | 10 | 1.000 | 0.775 | 0.873 |
| Supervisor-visible | V1 | 12 | 0 | 28 | 10 | 1.000 | 0.300 | 0.462 |
| Supervisor-visible | V2 | 13 | 0 | 27 | 10 | 1.000 | 0.325 | 0.491 |
| Supervisor-visible | V2.1 | 19 | 0 | 21 | 10 | 1.000 | 0.475 | 0.644 |

These V2.1 results are **development/tuning results on the separate challenge dataset**: the V2.1 phrase rules were revised after examining V2's misses on this dataset. The challenge dataset is synthetic, manually authored, small, and template-based. It is not an untouched final test set or an external benchmark. The 0 false positives observed among 10 normal cases do not establish a low real-world false-positive rate.

## Interpretation and limitations

- V2.1 improves recall on this challenge set while preserving zero false positives in its 10 normal scenarios. The sample is too small to infer real-world precision.
- Supervisor-visible logs in this generator intentionally omit the hidden events in Hidden Coordination and Hiding scenarios. The supervisor-only misses in those categories demonstrate this specific observability constraint; they do not prove that such threats are universally undetectable from supervisor-visible data.
- Goal drift and concealment detection depend on phrase patterns and can miss paraphrases, implicit intent, multilingual messages, or context-dependent meaning.
- V2.1 scores are heuristic indicators, not calibrated probabilities.
- The dataset is deterministic and manually authored. The seed constant does not make the examples statistically representative or randomly sampled.
- No real LLM agents, live tools, production workflows, or adversarially optimized agents were evaluated.
- Use human review, access controls, data minimization, and safeguards against false accusations in any future deployment.

## Versioning

- `detector.py` and `detector_v2.py` preserve the earlier project versions.
- `detector_v2_1.py` is a separate revised detector; it does not overwrite V2.
- `evaluate_independent_dataset.py` preserves the V1/V2 comparison.
- `evaluate_independent_dataset_v2_1.py` compares V1, V2, and V2.1.

## License

No license has been assigned yet. Do not assume the repository is open for reuse until a license is selected by the author.
