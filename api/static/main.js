function updateStatus(status) {
  let dot = document.getElementById("status-dot");
  let text = document.getElementById("status-text");
  let stopBtn = document.getElementById("emergency-stop");
  if (status.running) {
    dot.className = "status-dot dot-running";
    text.textContent = "Running pipeline...";
    stopBtn.style.display = "inline-block";
  } else if (status.last_report) {
    dot.className = "status-dot dot-done";
    text.textContent = "Pipeline finished!";
    stopBtn.style.display = "none";
  } else {
    dot.className = "status-dot dot-idle";
    text.textContent = "Idle";
    stopBtn.style.display = "none";
  }
}

function pollLogs() {
  fetch('/logs').then(res => res.json()).then(status => {
    let logs = document.getElementById("logs");
    logs.textContent = (status.logs || []).join("\n");
    logs.scrollTop = logs.scrollHeight;
    updateStatus(status);

    let frame = document.getElementById("report-frame");
    if (frame && status.last_report) {
      frame.style.display = 'block';
      frame.src = '/report';
    }
  });
}
setInterval(pollLogs, 1200);

document.getElementById('pipeline-form').onsubmit = function(e) {
  e.preventDefault();
  let form = e.target;
  let params = {
    pois_dir: form.pois_dir.value,
    streets_dir: form.streets_dir.value,
    output_dir: form.output_dir.value,
    test_mode: form.test_mode.checked
  };
  fetch('/run_pipeline', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(params)
  }).then(res => res.json())
    .then(data => setTimeout(pollLogs, 500));
};

function stopPipeline() {
  fetch('/stop_pipeline', {method: 'POST'})
    .then(res => res.json())
    .then(data => {
    });
}

function loadHistory() {
  fetch('/history/reports').then(res => res.json()).then(data => {
    let list = document.getElementById('history-reports');
    list.innerHTML = '';
    (data.history || []).forEach(path => {
      let a = document.createElement('a');
      a.href = '/download_report?path=' + encodeURIComponent(path);
      a.textContent = path.split('/').slice(-2).join('/');
      a.target = '_blank';
      let li = document.createElement('li');
      li.appendChild(a);
      list.appendChild(li);
    });
  });
  fetch('/history/logs').then(res => res.json()).then(data => {
    let list = document.getElementById('history-logs');
    list.innerHTML = '';
    (data.history || []).forEach(path => {
      let a = document.createElement('a');
      a.href = '/logfile?path=' + encodeURIComponent(path);
      a.textContent = path.split('/').slice(-2).join('/');
      a.target = '_blank';
      let li = document.createElement('li');
      li.appendChild(a);
      list.appendChild(li);
    });
  });
}
