"""Evaluation script for the medical alert extraction pipeline."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, Iterable, Tuple


Alert = Dict[str, str]


@dataclass
class EvaluationResult:
    total_expected: int
    total_generated: int
    matched: int
    type_mismatches: int
    date_delta_sum: int

    @property
    def precision(self) -> float:
        return self.matched / self.total_generated if self.total_generated else 0.0

    @property
    def recall(self) -> float:
        return self.matched / self.total_expected if self.total_expected else 0.0

    @property
    def mean_date_delta(self) -> float:
        return self.date_delta_sum / self.matched if self.matched else 0.0


DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d %b %Y"]


def parse_date(value: str) -> datetime:
    for fmt in DATE_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


def normalize_alert(alert: Alert) -> Tuple[str, str, datetime]:
    title = alert.get("title", "").strip().lower()
    alert_type = alert.get("alert_type", "").strip().upper()
    due_date_raw = alert.get("due_date")
    if not due_date_raw:
        raise ValueError("Alert is missing due_date")
    due_date = parse_date(due_date_raw)
    return title, alert_type, due_date


def score_alerts(expected: Iterable[Alert], generated: Iterable[Alert]) -> EvaluationResult:
    expected_list = list(expected)
    generated_list = list(generated)
    matched = 0
    type_mismatches = 0
    date_delta_sum = 0

    unmatched_generated = generated_list.copy()

    for exp in expected_list:
        exp_title, exp_type, exp_date = normalize_alert(exp)
        best_match = None
        best_delta = None
        for gen in unmatched_generated:
            gen_title, gen_type, gen_date = normalize_alert(gen)
            if gen_title == exp_title:
                delta = abs((gen_date - exp_date).days)
                if best_match is None or delta < best_delta:
                    best_match = (gen, gen_type == exp_type, delta)
                    best_delta = delta
        if best_match:
            unmatched_generated.remove(best_match[0])
            matched += 1
            if not best_match[1]:
                type_mismatches += 1
            date_delta_sum += best_match[2]

    return EvaluationResult(
        total_expected=len(expected_list),
        total_generated=len(generated_list),
        matched=matched,
        type_mismatches=type_mismatches,
        date_delta_sum=date_delta_sum,
    )


def load_alerts(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def evaluate(expected_path: Path, generated_path: Path) -> EvaluationResult:
    expected_data = load_alerts(expected_path)
    generated_data = load_alerts(generated_path)
    return score_alerts(expected_data.get("alerts", []), generated_data.get("alerts", []))


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate generated medical alerts against ground truth")
    parser.add_argument("expected", type=Path, help="Path to the ground truth alert JSON")
    parser.add_argument("generated", type=Path, help="Path to the generated alert JSON")
    args = parser.parse_args()

    result = evaluate(args.expected, args.generated)

    print("Total expected alerts:", result.total_expected)
    print("Total generated alerts:", result.total_generated)
    print("Matched alerts:", result.matched)
    print("Type mismatches:", result.type_mismatches)
    print("Precision:", f"{result.precision:.2%}")
    print("Recall:", f"{result.recall:.2%}")
    print("Mean date delta (days):", f"{result.mean_date_delta:.1f}")


if __name__ == "__main__":
    main()
