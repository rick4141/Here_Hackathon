# src/analysis/report.py
import pandas as pd
from datetime import datetime

def generate_report(pois_fixed, validation_results, output_dir, logger=None, html_path=None, **kwargs):
    """
    Generates a Bootstrap-styled HTML report for the POI pipeline.
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d %H:%M:%S")
    summary = validation_results["violation_code"].value_counts().to_dict()

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <title>POI Pipeline Report</title>
      <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
      <style>
        body {{ background: #f9fafb; }}
        .container {{ margin-top: 40px; }}
        .table-responsive {{ font-size: 0.98rem; }}
        .card {{ margin-bottom: 24px; }}
      </style>
    </head>
    <body>
    <div class="container">
      <div class="card shadow-sm">
        <div class="card-body">
          <h2 class="card-title text-primary mb-3">POI Pipeline Report</h2>
          <div class="mb-2 text-muted">Generated: {date_str}</div>
          <div><b>Total POIs Processed:</b> {len(pois_fixed)}</div>
        </div>
      </div>
      <div class="card shadow-sm">
        <div class="card-body">
          <h4 class="card-title">Validation Summary</h4>
          <ul>
            {"".join([f"<li><b>{k}:</b> {v}</li>" for k, v in summary.items()])}
          </ul>
        </div>
      </div>
      <div class="card shadow-sm">
        <div class="card-body">
          <h4 class="card-title">Sample of Corrected POIs</h4>
          <div class="table-responsive">
            {pois_fixed.head(10).to_html(classes="table table-bordered table-sm", index=False, border=0)}
          </div>
        </div>
      </div>
      <div class="card shadow-sm">
        <div class="card-body">
          <h4 class="card-title">Sample of Validation Results</h4>
          <div class="table-responsive">
            {validation_results.head(10).to_html(classes="table table-bordered table-sm", index=False, border=0)}
          </div>
        </div>
      </div>
      <div class="text-center text-secondary mb-4">End of Report</div>
    </div>
    </body>
    </html>
    """

    # Save as HTML file if requested
    if html_path:
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
        if logger:
            logger.info(f"HTML report saved at {html_path}")

    return html
