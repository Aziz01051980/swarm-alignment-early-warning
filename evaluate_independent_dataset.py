"""
Evaluate detector V1 and V2 on the held-out independent challenge dataset.

Run from the project root:
    python generate_independent_dataset.py
    python evaluate_independent_dataset.py

The script imports the detector functions from detector_v2.py, normalizes the
independent dataset's field names to the detector's expected schema, and keeps
ground-truth labels in evaluation_metadata.json (never in detector inputs).
"""

import csv
import json
from pathlib import Path

from detector_v2 import (
    THREATS,
    v1_detect,
    v2_detect,
    calculate_metrics,
)

DATASET_DIR = Path("results") / "independent_dataset"
OUTPUT_DIR = DATASET_DIR / "evaluation"
EXPECTED_CLASSES = {
    "NORMAL",
    "HIDDEN_COORDINATION",
    "GOAL_DRIFT",
    "SUPERVISOR_BYPASS",
    "HIDING",
}
THREAT_TO_CLASS = {
    "hidden_coordination": "HIDDEN_COORDINATION",
    "goal_drift": "GOAL_DRIFT",
    "supervisor_bypass": "SUPERVISOR_BYPASS",
    "hiding": "HIDING",
}


def read_jsonl(path):
    """Read a JSONL log and return its event objects."""
    events = []
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON in {path}, line {line_number}: {exc}"
                ) from exc
            if not isinstance(event, dict):
                raise ValueError(
                    f"Expected a JSON object in {path}, line {line_number}."
                )
            events.append(event)
    return events


def normalize_events(raw_events):
    """
    Map independent-dataset aliases to detector_v2's expected field names.

    The original events are copied; source files are never modified.
    """
    normalized = []
    for raw in raw_events:
        event = dict(raw)
        event["message"] = str(
            raw.get("message", raw.get("content", ""))
        )
        event["sender_id"] = str(
            raw.get("sender_id", raw.get("sender", "unknown"))
        )
        event["receiver_id"] = str(
            raw.get("receiver_id", raw.get("receiver", raw.get("recipient", "")))
        )
        event["event_type"] = str(
            raw.get("event_type", raw.get("type", "message"))
        )
        event["event_id"] = str(raw.get("event_id", "unknown"))
        event["authorization"] = str(
            raw.get("authorization", "")
        ).lower()
        normalized.append(event)
    return normalized


def validate_metadata(metadata):
    if not isinstance(metadata, list) or not metadata:
        raise ValueError("evaluation_metadata.json must contain a non-empty list.")

    seen = set()
    for index, record in enumerate(metadata, start=1):
        required = {
            "run_id", "audit_file", "supervisor_file",
            "ground_truth", "is_threat",
        }
        missing = required - set(record)
        if missing:
            raise ValueError(
                f"Metadata record {index} is missing fields: {sorted(missing)}"
            )
        if record["run_id"] in seen:
            raise ValueError(f"Duplicate run_id in metadata: {record['run_id']}")
        seen.add(record["run_id"])
        if record["ground_truth"] not in EXPECTED_CLASSES:
            raise ValueError(
                f"Unknown ground_truth for {record['run_id']}: "
                f"{record['ground_truth']}"
            )
        expected_is_threat = record["ground_truth"] != "NORMAL"
        if bool(record["is_threat"]) != expected_is_threat:
            raise ValueError(
                f"Inconsistent is_threat label for {record['run_id']}."
            )
    return metadata


def summarize_mode(rows, mode):
    mode_rows = [row for row in rows if row["mode"] == mode]
    summaries = []

    for version in ("v1", "v2"):
        y_true = [row["true_anomaly"] for row in mode_rows]
        y_pred = [row[f"{version}_predicted_anomaly"] for row in mode_rows]

        threat_metrics = {}
        for threat in THREATS:
            class_name = THREAT_TO_CLASS[threat]
            class_true = [
                row["ground_truth"] == class_name for row in mode_rows
            ]
            class_pred = [
                row[f"{version}_{threat}_alert"] for row in mode_rows
            ]
            threat_metrics[threat] = calculate_metrics(class_true, class_pred)

        summaries.append({
            "mode": mode,
            "detector": version.upper(),
            "overall": calculate_metrics(y_true, y_pred),
            "threats": threat_metrics,
        })
    return summaries


def main():
    metadata_path = DATASET_DIR / "evaluation_metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(
            f"Cannot find {metadata_path}. First run "
            "'python generate_independent_dataset.py' from the project root."
        )

    with metadata_path.open("r", encoding="utf-8") as handle:
        metadata = validate_metadata(json.load(handle))

    rows = []
    for mode, file_key in (
        ("audit", "audit_file"),
        ("supervisor", "supervisor_file"),
    ):
        for record in metadata:
            log_path = DATASET_DIR / record[file_key]
            if not log_path.exists():
                raise FileNotFoundError(
                    f"Missing log for {record['run_id']}: {log_path}"
                )

            # Ground truth is read from metadata only after the log is loaded.
            events = normalize_events(read_jsonl(log_path))
            v1_counts, v1_alerts = v1_detect(events)
            v2_evidence, v2_alerts, v2_scores = v2_detect(events)

            row = {
                "mode": mode,
                "run_id": record["run_id"],
                "ground_truth": record["ground_truth"],
                "true_anomaly": bool(record["is_threat"]),
                "event_count": len(events),
                "v1_predicted_anomaly": any(v1_alerts.values()),
                "v2_predicted_anomaly": any(v2_alerts.values()),
                "v1_predicted_threats": ";".join(
                    threat for threat, alert in v1_alerts.items() if alert
                ),
                "v2_predicted_threats": ";".join(
                    threat for threat, alert in v2_alerts.items() if alert
                ),
            }

            for threat in THREATS:
                row[f"v1_{threat}_count"] = v1_counts[threat]
                row[f"v1_{threat}_alert"] = v1_alerts[threat]
                row[f"v2_{threat}_alert"] = v2_alerts[threat]
                row[f"v2_{threat}_score"] = round(v2_scores[threat], 3)
                row[f"v2_{threat}_evidence"] = " | ".join(
                    v2_evidence[threat]
                )
            rows.append(row)

    summaries = []
    summaries.extend(summarize_mode(rows, "audit"))
    summaries.extend(summarize_mode(rows, "supervisor"))

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = OUTPUT_DIR / "independent_detailed_results.csv"
    json_path = OUTPUT_DIR / "independent_metrics_v1_vs_v2.json"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

    report = {
        "dataset": str(DATASET_DIR),
        "number_of_scenarios": len(metadata),
        "class_counts": {
            class_name: sum(
                record["ground_truth"] == class_name for record in metadata
            )
            for class_name in sorted(EXPECTED_CLASSES)
        },
        "evaluation_note": (
            "Held-out challenge-set evaluation. V1/V2 rules were not changed "
            "by this script. Results are specific to this simulated dataset "
            "and are not evidence of real-world generalization."
        ),
        "summaries": summaries,
    }
    with json_path.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print("\n====== INDEPENDENT DATASET: V1 vs V2 ======")
    print(f"Scenarios: {len(metadata)}")
    for summary in summaries:
        print(
            f"\nMode: {summary['mode']} | "
            f"Detector: {summary['detector']}"
        )
        print("Overall:", summary["overall"])
        print("Threat F1:", {
            threat: metrics["F1"]
            for threat, metrics in summary["threats"].items()
        })

    print("\nSaved:", csv_path)
    print("Saved:", json_path)
    print(
        "\nNOTE: This is an independent challenge-set evaluation of the "
        "current heuristic rules, not validation on real-world agent systems."
    )


if __name__ == "__main__":
    main()
