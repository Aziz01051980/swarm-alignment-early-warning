"""Compare V1, V2, and V2.1 on the independent challenge dataset.

Run from the project root after generating the independent dataset:
    python generate_independent_dataset.py
    python evaluate_independent_dataset_v2_1.py
"""
import csv
import json
from pathlib import Path

from detector_v2 import THREATS, calculate_metrics, v1_detect, v2_detect
from detector_v2_1 import normalize_events, v2_1_detect

DATASET_DIR = Path("results") / "independent_dataset"
OUTPUT_DIR = DATASET_DIR / "evaluation_v2_1"
EXPECTED_CLASSES = {"NORMAL", "HIDDEN_COORDINATION", "GOAL_DRIFT", "SUPERVISOR_BYPASS", "HIDING"}
THREAT_TO_CLASS = {
    "hidden_coordination": "HIDDEN_COORDINATION",
    "goal_drift": "GOAL_DRIFT",
    "supervisor_bypass": "SUPERVISOR_BYPASS",
    "hiding": "HIDING",
}


def read_jsonl(path):
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path}, line {line_no}: {exc}") from exc
            if not isinstance(event, dict):
                raise ValueError(f"Expected JSON object in {path}, line {line_no}")
            events.append(event)
    return events


def validate_metadata(metadata):
    if not isinstance(metadata, list) or len(metadata) != 50:
        raise ValueError("Expected exactly 50 metadata records in the challenge dataset")
    seen = set()
    for i, record in enumerate(metadata, 1):
        required = {"run_id", "audit_file", "supervisor_file", "ground_truth", "is_threat"}
        missing = required - set(record)
        if missing:
            raise ValueError(f"Metadata record {i} missing: {sorted(missing)}")
        if record["run_id"] in seen:
            raise ValueError(f"Duplicate run_id: {record['run_id']}")
        seen.add(record["run_id"])
        if record["ground_truth"] not in EXPECTED_CLASSES:
            raise ValueError(f"Unknown class: {record['ground_truth']}")
        if bool(record["is_threat"]) != (record["ground_truth"] != "NORMAL"):
            raise ValueError(f"Inconsistent label for {record['run_id']}")
    return metadata


def metric_summary(rows, mode, version):
    selected = [r for r in rows if r["mode"] == mode]
    pred_key = f"{version}_predicted_anomaly"
    y_true = [r["true_anomaly"] for r in selected]
    y_pred = [r[pred_key] for r in selected]
    threats = {}
    for threat, class_name in THREAT_TO_CLASS.items():
        class_true = [r["ground_truth"] == class_name for r in selected]
        class_pred = [r[f"{version}_{threat}_alert"] for r in selected]
        threats[threat] = calculate_metrics(class_true, class_pred)
    return {"mode": mode, "detector": version.upper(), "overall": calculate_metrics(y_true, y_pred), "threats": threats}


def main():
    metadata_path = DATASET_DIR / "evaluation_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Missing {metadata_path}; run generate_independent_dataset.py first")
    metadata = validate_metadata(json.loads(metadata_path.read_text(encoding="utf-8")))
    rows = []
    for mode, key in (("audit", "audit_file"), ("supervisor", "supervisor_file")):
        for record in metadata:
            path = DATASET_DIR / record[key]
            if not path.exists():
                raise FileNotFoundError(path)
            events = read_jsonl(path)
            v1_counts, v1_alerts = v1_detect(events)
            v2_evidence, v2_alerts, v2_scores = v2_detect(normalize_events(events))
            v21_evidence, v21_alerts, v21_scores = v2_1_detect(events)
            row = {
                "mode": mode, "run_id": record["run_id"],
                "ground_truth": record["ground_truth"],
                "true_anomaly": bool(record["is_threat"]), "event_count": len(events),
            }
            for version, alerts in (("v1", v1_alerts), ("v2", v2_alerts), ("v2_1", v21_alerts)):
                row[f"{version}_predicted_anomaly"] = any(alerts.values())
                row[f"{version}_predicted_threats"] = ";".join(t for t, a in alerts.items() if a)
                for threat, alert in alerts.items():
                    row[f"{version}_{threat}_alert"] = alert
            for threat in THREATS:
                row[f"v1_{threat}_count"] = v1_counts[threat]
                row[f"v2_{threat}_score"] = round(v2_scores[threat], 3)
                row[f"v2_{threat}_evidence"] = " | ".join(v2_evidence[threat])
                row[f"v2_1_{threat}_score"] = round(v21_scores[threat], 3)
                row[f"v2_1_{threat}_evidence"] = " | ".join(v21_evidence[threat])
            rows.append(row)

    summaries = [metric_summary(rows, mode, version) for mode in ("audit", "supervisor") for version in ("v1", "v2", "v2_1")]
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "independent_detailed_results_v1_v2_v2_1.csv"
    json_path = OUTPUT_DIR / "independent_metrics_v1_v2_v2_1.json"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    report = {
        "dataset": str(DATASET_DIR), "number_of_scenarios": len(metadata),
        "class_counts": {c: sum(r["ground_truth"] == c for r in metadata) for c in sorted(EXPECTED_CLASSES)},
        "evaluation_note": "V2.1 was iteratively developed after reviewing V2 errors on this challenge set. These results are tuning/development results, not a fresh untouched holdout and not evidence of real-world generalization.",
        "summaries": summaries,
    }
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n====== INDEPENDENT CHALLENGE DATASET: V1 vs V2 vs V2.1 ======")
    print(f"Scenarios: {len(metadata)}")
    for s in summaries:
        print(f"\nMode: {s['mode']} | Detector: {s['detector']}")
        print("Overall:", s["overall"])
        print("Threat F1:", {k: v["F1"] for k, v in s["threats"].items()})
    print("\nSaved:", csv_path)
    print("Saved:", json_path)

if __name__ == "__main__":
    main()
