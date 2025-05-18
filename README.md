# HERE-style POI Data Pipeline: Full Architecture & Documentation

## Overview

This repository implements a robust POI (Point-of-Interest) data processing pipeline inspired by the design, visual style, and automation principles of HERE Technologies. The system integrates:

* Python-based ETL pipeline
* Web dashboard (FastAPI + Bootstrap, HERE-style)
* Real-time logs and historical report viewer
* Emergency stop & status indicator
* Jenkins automation (CI/CD simulation)

---

## Project Structure

```
Here_Hackathon/
├── api/
│   ├── app.py           # FastAPI server: endpoints & dashboard
│   ├── pipeline.py      # Runs the ETL pipeline and logging hooks
│   ├── state.py         # Shared state: logs, status, report paths
│   ├── static/          # JS/CSS assets (main.js)
│   └── templates/       # index.html (dashboard UI)
├── data/                # POI & street raw input files
├── logs/                # Log files by date
├── output/              # Generated HTML/PDF reports by date
├── src/
│   ├── utils/logger.py  # Logger config for main & API
│   ├── data_loader/     # load_pois, load_streets
│   ├── preprocessing/   # normalizer, geocode
│   ├── validation/      # validator, fixer
│   ├── analysis/        # report (HTML, PDF)
├── main.py              # CLI pipeline entrypoint
├── Jenkinsfile          # Jenkins pipeline (CI/CD)
├── README.md            # This documentation
```

---

## 1. Web Dashboard (FastAPI + Bootstrap)

* **File:** `api/app.py`

* **Purpose:** Exposes REST endpoints and serves the modern dashboard UI.

* **Key Functions:**

  * `index(request)`: Renders the main dashboard (`index.html`).
  * `/run_pipeline`: Triggers the pipeline as a background thread (so logs stream in real-time).
  * `/logs`: Returns live logs, status, and last report info as JSON (AJAX polled by frontend).
  * `/report`: Serves last HTML report inline (for iframe embedding).
  * `/history/reports` & `/history/logs`: Return report and log file lists (for the dashboard history sidebar).
  * `/download_report`, `/logfile`: Download endpoints.
  * `/stop_pipeline`: Emergency stop signal.

* **Static & Template Structure:**

  * `static/main.js`: Handles all AJAX, UI status, and log streaming in browser.
  * `templates/index.html`: Responsive dashboard with HERE branding, log panel, launch/stop buttons, and history sidebar.

**How Real-Time Logs Work:**

* When you launch the pipeline, logs are appended to a shared `pipeline_logs` list in `api/state.py`, polled by `/logs`.
* The frontend calls `/logs` every \~1s and streams new logs to the UI log panel, updating the status light.

---

## 2. Pipeline Core (Python ETL)

* **File:** `api/pipeline.py`

* **Purpose:** Implements the data pipeline and logging.

* **Key Function:**

  * `run_pipeline_html(...)`:

    1. Loads POI and street data.
    2. Normalizes and geocodes POIs.
    3. Validates and auto-fixes POIs.
    4. Generates HTML and PDF reports.
    5. Logs each step via callback for live UI.
    6. Checks for emergency stop (from dashboard).

* **Other Utilities:**

  * `get_report_history()`: Finds all HTML/PDF reports by date for the dashboard history.
  * `get_log_history()`: Finds all log files by date for the dashboard history.
  * `pipeline_status`: Dict shared with `app.py` to track running/stop/last\_report.
  * `pipeline_logs`: In-memory log list for UI streaming.

**Note:** All long-running steps periodically check for `pipeline_status["emergency_stop"]` to allow safe early stopping.

---

## 3. Data Loaders & Processing (src/)

### 3.1. Data Loading

* **`src/data_loader/data_loader.py`**

  * `load_pois(dir)`: Loads and merges all POI CSV files from a directory.
  * `load_streets(dir)`: Loads all street GeoJSON files.

### 3.2. Preprocessing

* **`src/preprocessing/normalizer.py`**

  * `normalize_pois(df, logger)`: Cleans and standardizes POI data.
  * `normalize_streets(gdf, logger)`: Standardizes street geometry and names.
* **`src/preprocessing/geocode.py`**

  * `geocode_pois(pois, streets, logger)`: Assigns coordinates/address to POIs.

### 3.3. Validation & Fixing

* **`src/validation/validator.py`**

  * `validate_pois(pois, streets, logger)`: Checks POI fields/positions.
* **`src/validation/fixer.py`**

  * `fix_pois(validation, pois, streets, logger)`: Attempts to auto-correct issues.

### 3.4. Analysis/Reporting

* **`src/analysis/report.py`**

  * `generate_report(...)`: Builds visual HTML & PDF report from final POIs and validation.
  * Uses HTML template in `src/analysis/templates/report_template.html`.

---

## 4. Shared State (api/state.py)

* `pipeline_status`: Dict, tracks whether pipeline is running, stopped, emergency, and last report.
* `pipeline_logs`: List, contains live logs (populated by callback from `run_pipeline_html`).

---

## 5. CLI Entrypoint (main.py)

* Standard command-line interface for batch processing and debugging.
* Usage:

  ```bash
  python main.py --pois_dir data/POIs --streets_dir data/STREETS_NAMING_ADDRESSING --output_dir output --test_mode
  ```
* Outputs logs and reports just like the web pipeline.

---

## 6. Jenkins Integration (Jenkinsfile)

* Example Jenkins pipeline for CI/CD automation.
* Steps:

  1. **Checkout**: Clone or pull latest code.
  2. **Install**: Create venv, install dependencies (`requirements.txt`).
  3. **Run Tests** (optional): Execute any available unit/integration tests.
  4. **Pipeline Run**: Run main.py with production args.
  5. **Archive Artifacts**: Store logs and reports.

---

## Example Jenkinsfile

```groovy
pipeline {
  agent any
  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }
    stage('Setup Python') {
      steps {
        sh 'python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt'
      }
    }
    stage('Run Pipeline') {
      steps {
        sh '. .venv/bin/activate && python main.py --pois_dir data/POIs --streets_dir data/STREETS_NAMING_ADDRESSING --output_dir output --test_mode'
      }
    }
    stage('Archive Reports & Logs') {
      steps {
        archiveArtifacts artifacts: 'output/**/*.html,output/**/*.pdf,logs/**/*.log', allowEmptyArchive: true
      }
    }
  }
}
```

---

## 7. Visual: Example Dashboard UI Layout

```text
 -----------------------------------------------------------
|   POI Data Pipeline Dashboard (HERE branding & colors)   |
 -----------------------------------------------------------
| Pipeline Config |  [Launch Pipeline]  [EMERGENCY STOP]   |
|-----------------|----------------------------------------|
| POIs Dir        | Streets Dir     | Output Dir           |
|-----------------|----------------------------------------|
|     Real-time Logs Panel (auto-scrolls)                  |
|----------------------------------------------------------|
|   Last Report (HTML in iframe)     | History: Reports    |
|------------------------------------|---------------------|
|                                    | History: Logs       |
 -----------------------------------------------------------
```

---

## 8. Running the Project

### Development (Web Dashboard)

```bash
uvicorn api.app:app --reload
# Then open: http://127.0.0.1:8000/
```

### Command-Line (Batch)

```bash
python main.py --pois_dir data/POIs --streets_dir data/STREETS_NAMING_ADDRESSING --output_dir output --test_mode
```

---

## 9. Branding & Credits

* **Color palette**: #00AFAA (HERE teal), #242A3B (HERE dark), #FFFFFF (white), #E9EDEF (light gray)
* **Design inspiration:** [HERE Technologies](https://www.here.com/)
* **Developed by:** Ricardo Gutiérrez (GuadalaHacks 2025)

---

## 10. File/Function Reference

### `api/app.py`

* FastAPI server setup
* Mounts `/static` and `/templates`
* Key endpoints: `/`, `/run_pipeline`, `/logs`, `/report`, `/history/reports`, `/history/logs`, `/download_report`, `/logfile`, `/stop_pipeline`

### `api/pipeline.py`

* Main function: `run_pipeline_html(...)`

  * Params: data dirs, output, test, logger callback
  * Steps: loading, normalization, geocoding, validation, fixing, reporting
  * Appends logs to `pipeline_logs` via callback
  * Checks for emergency stop with `pipeline_status["emergency_stop"]`
* Utility: `get_report_history`, `get_log_history` (scans output/logs folders)

### `api/state.py`

* Defines `pipeline_status` (dict) and `pipeline_logs` (list)
* Used for UI and API status sharing

### `src/utils/logger.py`

* Function: `get_logger(name, log_file)` — configures file+console logger for each pipeline run

### `src/data_loader/data_loader.py`

* `load_pois(dir)` — reads and concatenates all POI CSVs in a directory
* `load_streets(dir)` — loads all street segment GeoJSONs

### `src/preprocessing/normalizer.py`

* `normalize_pois(df, logger)` — normalizes, cleans POI DataFrame
* `normalize_streets(gdf, logger)` — normalizes street names, geometry

### `src/preprocessing/geocode.py`

* `geocode_pois(pois, streets, logger)` — attaches coords/addresses

### `src/validation/validator.py`

* `validate_pois(pois, streets, logger)` — validates data consistency

### `src/validation/fixer.py`

* `fix_pois(validation, pois, streets, logger)` — fixes POIs with errors

### `src/analysis/report.py`

* `generate_report(pois_fixed, validation, output_dir, logger, pdf_path, html_path)`
* Creates PDF & HTML visual report (styled)

### `main.py`

* CLI entrypoint — uses the same pipeline core, logs to `logs/` and outputs to `output/`

---

## 11. Extending/Customizing

* Add new data checks or processing steps in `src/`
* Update report template in `src/analysis/templates/`
* Change dashboard appearance via `templates/index.html` and `static/main.js`
* Integrate with cloud storage, databases, etc.

---

## License

MIT
