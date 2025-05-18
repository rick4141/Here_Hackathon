import argparse
import os
import sys
import datetime
from src.utils.logger import get_logger
from src.data_loader.data_loader import load_pois, load_streets
from src.preprocessing.normalizer import normalize_pois, normalize_streets
from src.preprocessing.geocode import geocode_pois
from src.validation.validator import validate_pois
from src.validation.fixer import fix_pois
from src.analysis.report import generate_report

def main(
    pois_dir,
    streets_dir,
    output_dir,
    test_mode=False,
    test_file=None,
    base_logdir="logs"
):
    """
    Main pipeline for POI Data Processing. Handles all stages.
    If KeyboardInterrupt or error occurs in a stage, logs and proceeds.
    """

    # Prepare timestamped log/output paths
    now = datetime.datetime.now()
    date_str = now.strftime("%Y%m%d")
    hour_str = now.strftime("%H%M%S")
    logs_path = os.path.join(base_logdir, date_str)   # logs/YYYYMMDD
    os.makedirs(logs_path, exist_ok=True)
    log_file = os.path.join(logs_path, f"main_{date_str}_{hour_str}.log")

    logger = get_logger("main", log_file=log_file)
    logger.info(f"Logs will be saved in {log_file}")

    # All output in output/YYYYMMDD/
    report_dir = os.path.join(output_dir, date_str)
    os.makedirs(report_dir, exist_ok=True)
    pdf_path = os.path.join(report_dir, f"report_ex_{date_str}_{hour_str}.pdf")
    html_path = os.path.join(report_dir, f"report_ex_{date_str}_{hour_str}.html")

    pois_df = None
    streets_gdf = None
    pois_geo = None
    validation_results = None
    pois_fixed = None

    # 1. Load POIs
    try:
        if test_mode and test_file:
            logger.info(f"Loading test POIs from {test_file}")
            import pandas as pd
            pois_df = pd.read_csv(test_file)
        else:
            logger.info(f"Loading POIs from {pois_dir}")
            pois_df = load_pois(pois_dir)
        logger.info(f"Raw POIs loaded: {len(pois_df)} records")
    except Exception as e:
        logger.exception("Error loading POIs.")
        return

    # 2. Normalize POIs
    try:
        pois_df = normalize_pois(pois_df, logger)
        logger.info(f"Normalized POIs: {len(pois_df)}")
    except Exception as e:
        logger.exception("Error normalizing POIs.")
        return

    # 3. Load and normalize streets
    try:
        logger.info(f"Loading streets from {streets_dir}")
        streets_gdf = load_streets(streets_dir)
        logger.info(f"Raw street segments loaded: {len(streets_gdf)}")
        streets_gdf = normalize_streets(streets_gdf, logger)
        logger.info(f"Normalized street segments: {len(streets_gdf)}")
    except Exception as e:
        logger.exception("Error loading or normalizing streets.")
        return

    # 4. (Optional) Limit POIs for test
    if test_mode and not test_file:
        logger.info("Test mode enabled: Limiting to first 1001 POIs")
        pois_df = pois_df.iloc[:1001].copy()

    # 5. Geocoding POIs
    try:
        pois_geo = geocode_pois(pois_df, streets_gdf, logger)
        logger.info(f"Geocoded POIs: {pois_geo.geometry.notnull().sum()} out of {len(pois_geo)}")
    except KeyboardInterrupt:
        logger.warning("Geocoding interrupted by user (Ctrl+C). Proceeding to validation stage.")
    except Exception as e:
        logger.exception("Error during geocoding POIs.")

    # 6. Validation
    try:
        validation_results = validate_pois(pois_geo, streets_gdf, logger)
        logger.info(f"Validation finished for {len(pois_geo)} POIs.")
    except KeyboardInterrupt:
        logger.warning("Validation interrupted by user (Ctrl+C). Proceeding to fixing stage.")
    except Exception as e:
        logger.exception("Error during validation.")

    # 7. Auto-fixing
    try:
        pois_fixed = fix_pois(validation_results, pois_geo, streets_gdf, logger)
        logger.info(f"Auto-fix applied. Final POIs: {len(pois_fixed)}")
    except KeyboardInterrupt:
        logger.warning("Fixing interrupted by user (Ctrl+C). Proceeding to report stage.")
    except Exception as e:
        logger.exception("Error during auto-fixing.")

    # 8. Generate reports (PDF, HTML, etc)
    try:
        # Your generate_report can handle pdf_path and/or html_path
        generate_report(
            pois_fixed,
            validation_results,
            output_dir=report_dir,
            logger=logger,
            pdf_path=pdf_path,     # If implemented in your function
            html_path=html_path    # If implemented in your function
        )
        logger.info(f"Detailed reports generated: {pdf_path}, {html_path}")
    except Exception as e:
        logger.exception("Error during report generation.")

    logger.info("Pipeline finished.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="POI Data Processing Pipeline")
    parser.add_argument("--pois_dir", type=str, default="data/POIs", help="Directory containing POI CSV files.")
    parser.add_argument("--streets_dir", type=str, default="data/STREETS_NAMING_ADDRESSING", help="Directory with street GeoJSONs.")
    parser.add_argument("--output_dir", type=str, default="output", help="Output directory.")
    parser.add_argument("--test_mode", action="store_true", help="Enable test mode (limits to first 1001 POIs unless test_file is specified).")
    parser.add_argument("--test_file", type=str, default=None, help="Optional: Path to scenario/test CSV for test mode.")
    parser.add_argument("--base_logdir", type=str, default="logs", help="Base name for log directory.")

    args = parser.parse_args()

    main(
        pois_dir=args.pois_dir,
        streets_dir=args.streets_dir,
        output_dir=args.output_dir,
        test_mode=args.test_mode,
        test_file=args.test_file,
        base_logdir=args.base_logdir,
    )
