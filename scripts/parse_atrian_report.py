"""Parse ATRiAN ethics evaluation JSON report and optionally render HTML."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from statistics import mean
import csv
import yaml
from typing import List, Dict, Any

# Path to the strategic document
INCIDENT_AVOIDANCE_PROOF_PATH = "file:///C:/EGOS/ATRIAN/docs/INCIDENT_AVOIDANCE_PROOF.md"

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ATRiAN Ethics Evaluation Report</title>
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
<style>
body {{font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding-top: 20px;}}
.container {{ max-width: 1200px; }}
h1, h2, h3 {{ color: #333; }}
.metric-description p {{ margin-bottom: 0.5rem; }}
.table th {{ background-color: #f8f9fa; }}
.footer-links a {{ margin-right: 15px; }}
.score-green {{ background-color: #d4edda; color: #155724; }}
.score-yellow {{ background-color: #fff3cd; color: #856404; }}
.score-red {{ background-color: #f8d7da; color: #721c24; }}
</style>
</head>
<body>
<div class="container">
    <header class="text-center mb-4">
        <h1>ATRiAN Ethics Evaluation Report</h1>
        <p class="lead">Automated Triage & Remediation for AI Incidents and Negative Signals</p>
    </header>

    <section class="summary mb-4">
        <h2>Report Overview</h2>
        <p>This report summarizes the ethics evaluation of {count} incidents analyzed by ATRiAN. ATRiAN provides a proactive approach to identifying and mitigating ethical risks in AI systems. For a deeper understanding of ATRiAN's incident avoidance capabilities and methodology, please refer to the <a href="{incident_avoidance_proof_doc_path}" target="_blank">ATRiAN Incident Avoidance Proof Document</a>.</p>
    </section>

    <section class="metrics-explained mb-4">
        <h3>Understanding the Metrics</h3>
        <div class="row metric-description">
            <div class="col-md-4">
                <p><strong>BiasScore:</strong> Measures the level of bias detected. Lower scores are better, indicating less bias.</p>
            </div>
            <div class="col-md-4">
                <p><strong>SafetyScore:</strong> Assesses the safety implications. Higher scores are better, indicating greater safety.</p>
            </div>
            <div class="col-md-4">
                <p><strong>PrivacyLeakProb:</strong> Estimates the probability of a privacy leak. Lower probabilities are better.</p>
            </div>
        </div>
    </section>

    <section class="results-table mb-4">
        <h2>Detailed Incident Analysis</h2>
        <div class="table-responsive">
            <table class="table table-striped table-hover table-bordered">
                <thead class="table-light">
                    <tr>
                        <th>ID</th>
                        <th>BiasScore</th>
                        <th>SafetyScore</th>
                        <th>PrivacyLeakProb</th>
                        <th>Description</th>
                        <th>Severity</th>
                        <th>Potential Financial Impact</th>
                        <th>AIID Link</th>
                    </tr>
                </thead>
                <tbody>
                    {rows}
                </tbody>
            </table>
        </div>
    </section>

    <section class="averages mb-4">
        <h3>Overall Averages</h3>
        <div class="row">
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Average BiasScore</h5>
                        <p class="card-text fs-4 {{avg_bias_color}}">{avg_bias:.3f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Average SafetyScore</h5>
                        <p class="card-text fs-4 {{avg_safety_color}}">{avg_safety:.3f}</p>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card text-center">
                    <div class="card-body">
                        <h5 class="card-title">Average PrivacyLeakProb</h5>
                        <p class="card-text fs-4 {{avg_privacy_color}}">{avg_privacy:.3f}</p>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <footer class="text-center mt-5 pt-3 border-top footer-links">
        <p>&copy; {current_year} EGOS Project - ATRiAN Module</p>
    </footer>
</div>
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

def get_score_color_class(score: float, score_type: str) -> str:
    """Determines the CSS class for score color-coding."""
    if score_type == "bias":  # Lower is better
        if score < 0.3: return "score-green"
        if score <= 0.7: return "score-yellow"
        return "score-red"
    elif score_type == "safety":  # Higher is better
        if score > 0.7: return "score-green"
        if score >= 0.3: return "score-yellow"
        return "score-red"
    elif score_type == "privacy":  # Lower is better
        if score < 0.05: return "score-green"
        if score <= 0.1: return "score-yellow"
        return "score-red"
    return "" # Default no color

def load_costs(csv_path: Path) -> Dict[str, float]:
    """Load cost per incident_id from a reports.csv (assumes headers id,cost_usd)."""
    if not csv_path.exists():
        return {}
    costs: Dict[str, float] = {}
    with csv_path.open(newline='', encoding='utf-8') as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            inc_id = row.get('incident_id') or row.get('id')
            if inc_id:
                try:
                    costs[str(inc_id)] = float(row.get('cost_usd', row.get('cost', 0)))
                except ValueError:
                    continue
    return costs


def load_roi_model(yaml_path: Path) -> Dict[str, Any]:
    """Return ROI model parameters; default values if file missing."""
    defaults = {
        'value_drivers': {'risk_mitigation_perc': 0.15},
        'cost_components': {'atrian_subscription_annual': 50000}
    }
    if not yaml_path.exists():
        return defaults
    try:
        with yaml_path.open("r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
            return data or defaults
    except Exception:
        return defaults


def load_records(path: Path, costs: Dict[str, float], roi_model: Dict[str, Any]) -> List[Dict[str, Any]]:
    records = json.loads(path.read_text(encoding="utf-8"))
    for record in records:
        record['cost'] = costs.get(record['incident_id'], 0)
        record['roi'] = calculate_roi(record, roi_model)
    return records

def calculate_roi(record: Dict[str, Any], roi_model: Dict[str, Any]) -> float:
    # Calculate ROI based on the provided model
    risk_mitigation_perc = roi_model['value_drivers']['risk_mitigation_perc']
    atrian_subscription_annual = roi_model['cost_components']['atrian_subscription_annual']
    cost = record['cost']
    bias_score = record['BiasScore']
    safety_score = record['SafetyScore']
    privacy_leak_prob = record['PrivacyLeakProb']
    # Example ROI calculation, replace with actual logic
    roi = (bias_score * 0.2 + safety_score * 0.3 + privacy_leak_prob * 0.5) * risk_mitigation_perc * atrian_subscription_annual - cost
    return roi

def write_html(records: List[Dict[str, Any]], out_html: Path):
    if not records:
        rows_html = "<tr><td colspan='10' class='text-center'>No incident data available.</td></tr>"
        avg_bias, avg_safety, avg_privacy = 0.0, 0.0, 0.0
    else:
        rows_html_list = []
        for r in records:
            bias_color = get_score_color_class(r.get('BiasScore', 0), 'bias')
            safety_color = get_score_color_class(r.get('SafetyScore', 0), 'safety')
            privacy_color = get_score_color_class(r.get('PrivacyLeakProb', 0), 'privacy')
            rows_html_list.append(
                f"<tr>"
                f"<td>{r.get('incident_id', 'N/A')}</td>"
                f"<td class='{bias_color}'>{r.get('BiasScore', 'N/A')}</td>"
                f"<td class='{safety_color}'>{r.get('SafetyScore', 'N/A')}</td>"
                f"<td class='{privacy_color}'>{r.get('PrivacyLeakProb', 'N/A')}</td>"
                f"<td>{r.get('description', '')}</td>"
                f"<td>{r.get('severity', '')}</td>"
                f"<td>{r.get('financial_impact', '')}</td>"
                f"<td>{r.get('aiid_link', '')}</td>"
                f"</tr>"
            )
        rows_html = "".join(rows_html_list)
        avg_bias = mean(r.get("BiasScore", 0) for r in records)
        avg_safety = mean(r.get("SafetyScore", 0) for r in records)
        avg_privacy = mean(r.get("PrivacyLeakProb", 0) for r in records)

    # Ensure target directory exists
    out_html.parent.mkdir(parents=True, exist_ok=True)

    from datetime import datetime
    current_year = datetime.now().year

    avg_bias_color = get_score_color_class(avg_bias, 'bias')
    avg_safety_color = get_score_color_class(avg_safety, 'safety')
    avg_privacy_color = get_score_color_class(avg_privacy, 'privacy')

    html = HTML_TEMPLATE.format(
        count=len(records),
        rows=rows_html,
        avg_bias=avg_bias,
        avg_safety=avg_safety,
        avg_privacy=avg_privacy,
        avg_bias_color=avg_bias_color,
        avg_safety_color=avg_safety_color,
        avg_privacy_color=avg_privacy_color,
        incident_avoidance_proof_doc_path=INCIDENT_AVOIDANCE_PROOF_PATH,
        current_year=current_year
    )
    out_html.write_text(html, encoding="utf-8")
    print(f"HTML report generated at: {out_html.resolve()}")

def main():
    parser = argparse.ArgumentParser(description="Parse ATRiAN report JSON and optionally render HTML.")
    parser.add_argument("report_json", type=Path, help="Path to report.json")
    parser.add_argument("--html", type=Path, help="Optional path to output HTML report", default=None)

    args = parser.parse_args()

    report_path = Path(args.report_json)
    if not report_path.exists():
        raise FileNotFoundError(report_path)

    # Try to locate costs CSV in same dir as report or fallback to project root
cost_csv_candidate = report_path.parent / "reports.csv"
if not cost_csv_candidate.exists():
    cost_csv_candidate = Path("C:/EGOS/reports.csv")
costs_map = load_costs(cost_csv_candidate)

roi_model_path = Path("C:/EGOS/roi_model.yaml")
roi_model = load_roi_model(roi_model_path)

records = load_records(report_path, costs_map, roi_model)
    print(f"Parsed {len(records)} records.")

    if args.html:
        out_html = Path(args.html)
        write_html(records, out_html)
        print(f"HTML report written to {out_html}")


if __name__ == "__main__":
    main()