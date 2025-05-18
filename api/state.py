pipeline_status = {
    "running": False,
    "emergency_stop": False,
    "last_report": None
}
pipeline_logs = []

def append_log(line):
    pipeline_logs.append(line)
    if len(pipeline_logs) > 1000:
        pipeline_logs.pop(0)
