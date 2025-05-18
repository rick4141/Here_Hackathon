import os
import threading
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from .pipeline import run_pipeline_html, get_report_history, get_log_history, pipeline_status, pipeline_logs

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

app = FastAPI()

# Serve index.html directly on "/"
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Launch the pipeline as a background thread
@app.post("/run_pipeline")
async def run_pipeline_api(request: Request):
    params = await request.json()
    pipeline_logs.clear()
    pipeline_status["running"] = True
    pipeline_status["emergency_stop"] = False

    def log_callback(msg):
        pipeline_logs.append(msg)
    
    def pipeline_thread():
        html_path = run_pipeline_html(
            pois_dir=params.get("pois_dir", "data/POIs"),
            streets_dir=params.get("streets_dir", "data/STREETS_NAMING_ADDRESSING"),
            output_dir=params.get("output_dir", "output"),
            test_mode=params.get("test_mode", True),
            test_file=params.get("test_file"),
            base_logdir="logs",
            logger_callback=log_callback
        )
        pipeline_status["running"] = False
        if html_path:
            pipeline_status["last_report"] = html_path

    threading.Thread(target=pipeline_thread, daemon=True).start()
    return {"status": "started"}

# Real-time logs/status
@app.get("/logs")
def get_logs():
    return {
        "logs": list(pipeline_logs),
        "running": pipeline_status.get("running", False),
        "last_report": pipeline_status.get("last_report"),
    }

# Serve the last report inline (iframe)
@app.get("/report")
def show_last_report():
    last_html = pipeline_status.get("last_report")
    if last_html and os.path.exists(last_html):
        return FileResponse(last_html, media_type="text/html")
    return JSONResponse({"error": "No report found"}, status_code=404)

# Report History
@app.get("/history/reports")
def report_history():
    return get_report_history()

# Logs History
@app.get("/history/logs")
def log_history():
    return get_log_history()

# Download files
@app.get("/logfile")
def download_logfile(path: str):
    if os.path.exists(path):
        return FileResponse(path, media_type="text/plain")
    return JSONResponse({"error": "Log not found"}, status_code=404)

# HTML
@app.get("/download_report")
def download_report(path: str):
    if os.path.exists(path):
        media = "application/pdf" if path.endswith(".pdf") else "text/html"
        return FileResponse(path, media_type=media)
    return JSONResponse({"error": "Report not found"}, status_code=404)

# Emergency Stop
@app.post("/stop_pipeline")
def stop_pipeline():
    pipeline_status["emergency_stop"] = True
    pipeline_logs.append("EMERGENCY STOP! Pipeline terminated by user.")
    pipeline_status["running"] = False
    return {"status": "stopping"}
