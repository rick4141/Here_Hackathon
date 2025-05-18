# api/pipeline.py

import os
import datetime
from src.utils.logger import get_logger
from src.data_loader.data_loader import load_pois, load_streets
from src.preprocessing.normalizer import normalize_pois, normalize_streets
from src.preprocessing.geocode import geocode_pois
from src.validation.validator import validate_pois
from src.validation.fixer import fix_pois
from src.analysis.report import generate_report

from .state import pipeline_status, pipeline_logs, append_log

def run_pipeline_html(
    pois_dir,
    streets_dir,
    output_dir,
    test_mode=False,
    test_file=None,
    base_logdir="logs",
    logger_callback=None,
):
    # Reset status/logs
    pipeline_status["running"] = True
    pipeline_status["emergency_stop"] = False
    pipeline_status["last_report"] = None
    pipeline_logs.clear()

    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    hour_str = now.strftime("%H%M%S")
    logs_path = os.path.join(base_logdir, date_str)
    os.makedirs(logs_path, exist_ok=True)
    log_file = os.path.join(logs_path, f"api_{date_str}_{hour_str}.log")
    report_dir = os.path.join(output_dir, date_str)
    os.makedirs(report_dir, exist_ok=True)
    html_path = os.path.join(report_dir, f"report_ex_{date_str}_{hour_str}.html")
    pdf_path = os.path.join(report_dir, f"report_ex_{date_str}_{hour_str}.pdf")

    logger = get_logger("api", log_file=log_file)

    def log(msg):
        line = f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {msg}"
        append_log(line)
        logger.info(msg)
        if logger_callback:
            logger_callback(msg)

    try:
        # 1. Load POIs
        if test_mode and test_file:
            log(f"Loading test POIs from {test_file}")
            import pandas as pd
            pois_df = pd.read_csv(test_file)
        else:
            log(f"Loading POIs from {pois_dir}")
            pois_df = load_pois(pois_dir)
        log(f"Raw POIs loaded: {len(pois_df)} records")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after loading POIs.")
            pipeline_status["running"] = False
            return None

        # 2. Normalize POIs
        pois_df = normalize_pois(pois_df, logger)
        log(f"Normalized POIs: {len(pois_df)}")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after normalizing POIs.")
            pipeline_status["running"] = False
            return None

        # 3. Load and normalize streets
        log(f"Loading streets from {streets_dir}")
        streets_gdf = load_streets(streets_dir)
        log(f"Raw street segments loaded: {len(streets_gdf)}")
        streets_gdf = normalize_streets(streets_gdf, logger)
        log(f"Normalized street segments: {len(streets_gdf)}")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after loading streets.")
            pipeline_status["running"] = False
            return None

        # 4. Optional: Limit POIs for test
        if test_mode and not test_file:
            log("Test mode enabled: Limiting to first 1001 POIs")
            pois_df = pois_df.iloc[:1001].copy()
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after limiting POIs.")
            pipeline_status["running"] = False
            return None

        # 5. Geocoding
        pois_geo = geocode_pois(pois_df, streets_gdf, logger)
        log(f"Geocoded POIs: {pois_geo.geometry.notnull().sum()} out of {len(pois_geo)}")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after geocoding.")
            pipeline_status["running"] = False
            return None

        # 6. Validation
        validation_results = validate_pois(pois_geo, streets_gdf, logger)
        log(f"Validation finished for {len(pois_geo)} POIs.")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after validation.")
            pipeline_status["running"] = False
            return None

        # 7. Auto-fixing
        pois_fixed = fix_pois(validation_results, pois_geo, streets_gdf, logger)
        log(f"Auto-fix applied. Final POIs: {len(pois_fixed)}")
        if pipeline_status["emergency_stop"]:
            log("EMERGENCY STOP! Pipeline terminated after fixing.")
            pipeline_status["running"] = False
            return None

        # 8. Generate reports
        generate_report(
            pois_fixed,
            validation_results,
            output_dir=report_dir,
            logger=logger,
            pdf_path=pdf_path,
            html_path=html_path,
        )
        log(f"Detailed reports generated: {pdf_path}, {html_path}")
        pipeline_status["last_report"] = html_path

    except Exception as e:
        log(f"Pipeline error: {e}")
        pipeline_status["running"] = False
        return None

    log("Pipeline finished successfully.")
    pipeline_status["running"] = False
    return html_path

# Helper functions for history endpoints
def get_report_history():
    history = []
    for root, dirs, files in os.walk("output"):
        for f in files:
            if f.endswith(".html") or f.endswith(".pdf"):
                history.append(os.path.join(root, f))
    return sorted(history, reverse=True)

def get_log_history():
    history = []
    for root, dirs, files in os.walk("logs"):
        for f in files:
            if f.endswith(".log"):
                history.append(os.path.join(root, f))
    return sorted(history, reverse=True)
