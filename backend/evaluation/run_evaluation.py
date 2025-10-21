from __future__ import annotations

import json
import sys
from datetime import date, datetime
from pathlib import Path
from statistics import mean
from typing import Any

import requests

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


def load_ground_truth(ground_truth_path: Path) -> dict[str, list[dict[str, Any]]]:
    with ground_truth_path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return {k: v for k, v in sorted(data.items())}


def parse_iso_date(raw_date: str | None) -> date | None:
    if not raw_date:
        return None
    try:
        return datetime.fromisoformat(raw_date).date()
    except ValueError:
        return None


def compute_metrics(
    expected_alerts: list[dict[str, Any]], predicted_alerts: list[dict[str, Any]]
) -> dict[str, Any]:
    matches: list[tuple[dict[str, Any], dict[str, Any] | None]] = []
    for expected in expected_alerts:
        match = next(
            (
                candidate
                for candidate in predicted_alerts
                if expected["type"] == candidate["type"]["id"]
                and expected["date"] == candidate["date"]
            ),
            None,
        )

        matches.append((expected, match))

    matched = [pair for pair in matches if pair[1] is not None]
    date_deltas = []
    for expected, predicted in matched:
        expected_date = parse_iso_date(str(expected.get("date")))
        predicted_date = parse_iso_date(str(predicted.get("date")))
        if expected_date and predicted_date:
            date_deltas.append(abs((predicted_date - expected_date).days))

    accuracy = len(matched) / len(matches)
    average_date_delta = mean(date_deltas) if date_deltas else None

    return {
        "accuracy": accuracy,
        "average_date_delta_days": average_date_delta,
        "expected": expected_alerts,
        "predicted": predicted_alerts,
    }


def _fetch_alerts_via_api(pdf_path: Path) -> list[dict[str, Any]]:
    url = "http://localhost:8000/medical-records"

    with pdf_path.open("rb") as file_obj:
        response = requests.post(
            url,
            files={"file": (pdf_path.name, file_obj, "application/pdf")},
        )

    response.raise_for_status()
    return response.json().get("events", [])


def run_evaluation(data_dir: Path, ground_truth_path: Path) -> dict[str, Any]:
    ground_truth = load_ground_truth(ground_truth_path)

    results: dict[str, Any] = {}
    aggregate_accuracy: list[float] = []
    aggregate_date_deltas: list[float] = []

    # ground_truth = {k: v for k, v in ground_truth.items() if k == "ocr_noisy_record.pdf"}

    for pdf_name, expected_alerts in ground_truth.items():
        pdf_path = data_dir / pdf_name
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        predicted_alerts = _fetch_alerts_via_api(pdf_path)

        metrics = compute_metrics(expected_alerts, predicted_alerts)
        results[pdf_name] = metrics

        aggregate_accuracy.append(metrics["accuracy"])
        if metrics["average_date_delta_days"] is not None:
            aggregate_date_deltas.append(metrics["average_date_delta_days"])

    summary = {
        "accuracy": mean(aggregate_accuracy) if aggregate_accuracy else 1.0,
        "mean_date_delta_days": mean(aggregate_date_deltas)
        if aggregate_date_deltas
        else None,
    }

    return {"per_document": results, "summary": summary}


def main() -> None:
    BASE_DIR = Path(__file__).resolve().parents[1]
    DATA_DIR = BASE_DIR / "evaluation" / "data"
    GROUND_TRUTH_PATH = (
        BASE_DIR / "evaluation" / "data" / "ground_truth" / "alerts.json"
    )
    OUTPUT_PATH = BASE_DIR / "evaluation" / "results.json"

    evaluation = run_evaluation(DATA_DIR, GROUND_TRUTH_PATH)

    print(json.dumps(evaluation, indent=2))
    with OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(evaluation, f, indent=2)


if __name__ == "__main__":
    main()
