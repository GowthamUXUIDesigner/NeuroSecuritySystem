from flask import Flask, jsonify, render_template_string
import os
import json
from datetime import datetime

app = Flask(__name__)

LOG_FILE = "neuro_logs.json"


def get_last_events(n=50):
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()[-n:]
    events = []
    for line in lines:
        try:
            events.append(json.loads(line))
        except:
            continue
    # Newest last; we can reverse if we want newest first
    return events[::-1]


@app.get("/api/status")
def api_status():
    events = get_last_events()
    summary = {
        "total_events": len(events),
        "alerts": sum(1 for e in events if e.get("level") == "ALERT"),
        "warnings": sum(1 for e in events if e.get("level") == "WARNING"),
        "info": sum(1 for e in events if e.get("level") == "INFO")
    }
    return jsonify({
        "system": "Neuro Security Ecosystem",
        "state": "Protected",
        "timestamp": str(datetime.now()),
        "summary": summary,
        "events": events
    })


@app.get("/")
def home():
    # Minimal UI with auto-refresh via JS
    template = """
    <!doctype html>
    <html>
    <head>
        <title>Neuro Security Dashboard</title>
        <style>
            body {
                font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
                margin: 0;
                padding: 1rem 2rem;
                background: #0b1120;
                color: #e5e7eb;
            }
            h1 {
                font-size: 1.6rem;
                margin-bottom: 0.2rem;
            }
            .subtitle {
                font-size: 0.9rem;
                color: #9ca3af;
                margin-bottom: 1rem;
            }
            .cards {
                display: flex;
                flex-wrap: wrap;
                gap: 1rem;
                margin-bottom: 1rem;
            }
            .card {
                background: #020617;
                border-radius: 0.8rem;
                padding: 0.8rem 1rem;
                box-shadow: 0 10px 25px rgba(0,0,0,0.4);
                min-width: 180px;
            }
            .card-label {
                font-size: 0.75rem;
                text-transform: uppercase;
                letter-spacing: 0.06em;
                color: #9ca3af;
            }
            .card-value {
                font-size: 1.4rem;
                margin-top: 0.2rem;
            }
            .card-ok { border-left: 3px solid #22c55e; }
            .card-warn { border-left: 3px solid #eab308; }
            .card-alert { border-left: 3px solid #ef4444; }
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 0.85rem;
            }
            th, td {
                padding: 0.4rem 0.5rem;
                border-bottom: 1px solid #1f2937;
                vertical-align: top;
            }
            th {
                text-align: left;
                font-weight: 600;
                color: #9ca3af;
                background: #020617;
                position: sticky;
                top: 0;
            }
            tr:nth-child(even) {
                background: #020617;
            }
            .level-INFO { color: #22c55e; }
            .level-WARNING { color: #eab308; }
            .level-ALERT { color: #ef4444; }
            .tag {
                display: inline-block;
                padding: 0.1rem 0.35rem;
                border-radius: 999px;
                font-size: 0.7rem;
                background: #111827;
            }
            .tag-alert { background: #451a1a; color: #fecaca; }
            .tag-warning { background: #422006; color: #fed7aa; }
            .tag-info { background: #022c22; color: #bbf7d0; }
            .footer {
                margin-top: 1rem;
                font-size: 0.75rem;
                color: #6b7280;
            }
        </style>
    </head>
    <body>
        <h1>Neuro Security Dashboard</h1>
        <div class="subtitle">
            Live view of what the system is doing, what it detected, and how it responded.
        </div>

        <div class="cards">
            <div class="card card-ok">
                <div class="card-label">Overall State</div>
                <div class="card-value" id="state">Loading...</div>
            </div>
            <div class="card card-ok">
                <div class="card-label">Events (Last 50)</div>
                <div class="card-value" id="total-events">–</div>
            </div>
            <div class="card card-alert">
                <div class="card-label">Alerts</div>
                <div class="card-value" id="alerts">–</div>
            </div>
            <div class="card card-warn">
                <div class="card-label">Warnings</div>
                <div class="card-value" id="warnings">–</div>
            </div>
        </div>

        <h2 style="font-size:1rem; margin-top:0.5rem;">Recent Activity</h2>
        <table>
            <thead>
                <tr>
                    <th>Time</th>
                    <th>Level</th>
                    <th>Type</th>
                    <th>Source</th>
                    <th>What happened / How it reacted</th>
                </tr>
            </thead>
            <tbody id="events-body">
            </tbody>
        </table>

        <div class="footer">
            Auto-refreshes every 5 seconds. The system uses heuristic + optional ML analysis in the background.<br/>
            This is an educational/helper layer – keep a trusted antivirus + OS security enabled as well.
        </div>

        <script>
            async function loadStatus() {
                try {
                    const res = await fetch('/api/status');
                    const data = await res.json();

                    document.getElementById('state').textContent = data.state || 'Unknown';
                    document.getElementById('total-events').textContent = data.summary.total_events;
                    document.getElementById('alerts').textContent = data.summary.alerts;
                    document.getElementById('warnings').textContent = data.summary.warnings;

                    const tbody = document.getElementById('events-body');
                    tbody.innerHTML = '';

                    (data.events || []).forEach(ev => {
                        const tr = document.createElement('tr');

                        const tdTime = document.createElement('td');
                        tdTime.textContent = ev.time || '';
                        tr.appendChild(tdTime);

                        const tdLevel = document.createElement('td');
                        tdLevel.textContent = ev.level || '';
                        tdLevel.className = 'level-' + (ev.level || '');
                        tr.appendChild(tdLevel);

                        const tdType = document.createElement('td');
                        const tag = document.createElement('span');
                        tag.textContent = ev.event_type || '';
                        let baseClass = 'tag ';
                        if (ev.level === 'ALERT') baseClass += 'tag-alert';
                        else if (ev.level === 'WARNING') baseClass += 'tag-warning';
                        else baseClass += 'tag-info';
                        tag.className = baseClass;
                        tdType.appendChild(tag);
                        tr.appendChild(tdType);

                        const tdSource = document.createElement('td');
                        tdSource.textContent = ev.source || '';
                        tr.appendChild(tdSource);

                        const tdMsg = document.createElement('td');
                        tdMsg.textContent = ev.message || '';
                        tr.appendChild(tdMsg);

                        tbody.appendChild(tr);
                    });

                } catch (e) {
                    console.error('Failed to load status', e);
                }
            }

            loadStatus();
            setInterval(loadStatus, 5000);
        </script>
    </body>
    </html>
    """
    return render_template_string(template)


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
