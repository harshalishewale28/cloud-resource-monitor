
from flask import Flask, jsonify
import psutil
import platform
import socket
import time
import os

app = Flask(__name__)
start_time = time.time()


def get_size(gb):
    return round(gb / (1024 ** 3), 2)


@app.route("/")
def home():
    return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CloudWatch | Resource Monitor</title>

    <style>
        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        :root {
            --bg: #0b1120;
            --panel: #111b2e;
            --panel-light: #17243a;
            --border: #26354d;
            --text: #edf4ff;
            --muted: #93a4bd;
            --blue: #579bff;
            --green: #32d6a0;
            --orange: #ffb454;
            --red: #ff667d;
        }

        body {
            font-family: "Segoe UI", Arial, sans-serif;
            background: var(--bg);
            color: var(--text);
            min-height: 100vh;
        }

        .layout {
            display: flex;
            min-height: 100vh;
        }

        .sidebar {
            width: 245px;
            padding: 28px 18px;
            background: #0e1728;
            border-right: 1px solid var(--border);
            flex-shrink: 0;
        }

        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 42px;
            font-size: 18px;
            font-weight: 700;
        }

        .brand-icon {
            display: grid;
            place-items: center;
            width: 42px;
            height: 42px;
            border-radius: 13px;
            background: linear-gradient(135deg, #438cff, #7258f5);
            font-size: 22px;
        }

        .menu-label {
            color: #70839f;
            font-size: 11px;
            font-weight: 700;
            letter-spacing: 1.5px;
            margin: 25px 12px 12px;
        }

        .menu-item {
            padding: 13px 14px;
            border-radius: 10px;
            margin: 6px 0;
            color: var(--muted);
            font-size: 14px;
        }

        .menu-item.active {
            color: white;
            background: #1d3150;
            border: 1px solid #2b4770;
        }

        .sidebar-note {
            margin-top: 45px;
            padding: 15px;
            border-radius: 12px;
            background: #142238;
            border: 1px solid var(--border);
        }

        .sidebar-note p {
            color: var(--muted);
            font-size: 12px;
            line-height: 1.7;
            margin-top: 7px;
        }

        main {
            flex: 1;
            min-width: 0;
            padding: 30px;
        }

        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 18px;
            flex-wrap: wrap;
            margin-bottom: 30px;
        }

        .eyebrow {
            color: var(--blue);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 1.5px;
            text-transform: uppercase;
            margin-bottom: 9px;
        }

        h1 {
            font-size: clamp(24px, 3vw, 32px);
            letter-spacing: -0.8px;
        }

        .subtitle {
            color: var(--muted);
            margin-top: 9px;
            font-size: 14px;
        }

        .top-actions {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
        }

        .live-badge {
            padding: 10px 13px;
            border-radius: 10px;
            background: #12352f;
            border: 1px solid #205a4d;
            color: #65e6bc;
            font-size: 12px;
        }

        .live-dot {
            display: inline-block;
            width: 7px;
            height: 7px;
            background: var(--green);
            border-radius: 50%;
            margin-right: 7px;
        }

        button {
            border: 1px solid #35537b;
            background: #1b3150;
            color: white;
            padding: 11px 15px;
            border-radius: 10px;
            font-size: 13px;
            cursor: pointer;
        }

        button:hover {
            background: #29466e;
        }

        .section-heading {
            font-size: 17px;
            margin-bottom: 16px;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 18px;
            margin-bottom: 25px;
        }

        .card {
            background: var(--panel);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 22px;
            min-width: 0;
            box-shadow: 0 8px 25px #00000012;
        }

        .metric-top {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 10px;
        }

        .metric-title {
            color: #bdcbe0;
            font-size: 14px;
            font-weight: 600;
        }

        .metric-icon {
            display: grid;
            place-items: center;
            width: 43px;
            height: 43px;
            border-radius: 12px;
            background: #1c3455;
            color: #80b5ff;
            font-size: 21px;
        }

        .metric-value {
            font-size: 34px;
            font-weight: 750;
            letter-spacing: -1px;
            margin: 22px 0 7px;
        }

        .metric-description {
            color: var(--muted);
            font-size: 12px;
            margin-bottom: 20px;
        }

        .progress-track {
            height: 7px;
            background: #26354b;
            border-radius: 20px;
            overflow: hidden;
        }

        .progress-bar {
            height: 100%;
            width: 0%;
            border-radius: 20px;
            transition: width 0.6s ease;
            background: var(--blue);
        }

        .green-bar {
            background: var(--green);
        }

        .orange-bar {
            background: var(--orange);
        }

        .red-bar {
            background: var(--red);
        }

        .progress-caption {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            color: var(--muted);
            font-size: 11px;
            margin-top: 10px;
        }

        .lower-grid {
            display: grid;
            grid-template-columns: 1.2fr 1fr;
            gap: 18px;
            margin-bottom: 25px;
        }

        .panel-heading {
            font-size: 16px;
            margin-bottom: 20px;
        }

        .status-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            padding: 16px 0;
            border-bottom: 1px solid var(--border);
        }

        .status-row:last-child {
            border-bottom: none;
        }

        .status-name {
            font-size: 13px;
            color: #c6d4e8;
        }

        .status-detail {
            color: var(--muted);
            font-size: 11px;
            margin-top: 5px;
        }

        .status-pill {
            white-space: nowrap;
            font-size: 11px;
            padding: 7px 10px;
            border-radius: 20px;
            color: #6de7bc;
            background: #153a32;
        }

        .status-pill.warning {
            color: #ffc477;
            background: #43301b;
        }

        .status-pill.danger {
            color: #ff91a1;
            background: #461f2a;
        }

        .info-list {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px 12px;
        }

        .info-label {
            font-size: 11px;
            color: var(--muted);
            margin-bottom: 8px;
        }

        .info-value {
            font-size: 14px;
            font-weight: 600;
            overflow-wrap: anywhere;
        }

        .footer {
            display: flex;
            justify-content: space-between;
            flex-wrap: wrap;
            gap: 10px;
            color: #71839e;
            font-size: 11px;
            padding: 15px 2px;
        }

        @media (max-width: 1050px) {
            .sidebar {
                width: 200px;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .lower-grid {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 650px) {
            .layout {
                display: block;
            }

            .sidebar {
                width: 100%;
                padding: 15px;
                border-right: none;
                border-bottom: 1px solid var(--border);
            }

            .brand {
                margin-bottom: 15px;
            }

            .menu-label, .sidebar-note {
                display: none;
            }

            .menu {
                display: flex;
                gap: 8px;
                overflow-x: auto;
            }

            .menu-item {
                white-space: nowrap;
                margin: 0;
            }

            main {
                padding: 20px 15px;
            }

            .card {
                padding: 19px;
            }
        }
    </style>
</head>

<body>
<div class="layout">

    <aside class="sidebar">
        <div class="brand">
            <div class="brand-icon">☁</div>
            <span>CloudMonitor</span>
        </div>

        <div class="menu-label">WORKSPACE</div>

        <nav class="menu">
            <div class="menu-item active">▦ &nbsp; Overview</div>
            <div class="menu-item">◉ &nbsp; Resources</div>
            <div class="menu-item">◷ &nbsp; Activity</div>
        </nav>

        <div class="sidebar-note">
            <strong>Monitoring active</strong>
            <p>This demo currently measures your local computer. AWS monitoring can be connected in a later stage.</p>
        </div>
    </aside>

    <main>
        <header class="topbar">
            <div>
                <div class="eyebrow">Monitoring center</div>
                <h1>Resource Overview</h1>
                <p class="subtitle">
                    Monitor your system performance in real time.
                </p>
            </div>

            <div class="top-actions">
                <div class="live-badge">
                    <span class="live-dot"></span>
                    <span id="connection">Connecting...</span>
                </div>
                <button onclick="updateDashboard()">↻ Refresh</button>
            </div>
        </header>

        <h2 class="section-heading">Resource utilization</h2>

        <section class="metrics-grid">
            <article class="card">
                <div class="metric-top">
                    <span class="metric-title">CPU Usage</span>
                    <div class="metric-icon">⌁</div>
                </div>
                <div class="metric-value" id="cpu">--%</div>
                <p class="metric-description">Processor utilization</p>
                <div class="progress-track">
                    <div class="progress-bar" id="cpuBar"></div>
                </div>
                <div class="progress-caption">
                    <span>Current usage</span>
                    <span id="cpuCaption">--%</span>
                </div>
            </article>

            <article class="card">
                <div class="metric-top">
                    <span class="metric-title">Memory Usage</span>
                    <div class="metric-icon">▤</div>
                </div>
                <div class="metric-value" id="memory">--%</div>
                <p class="metric-description" id="memoryDetail">
                    RAM utilization
                </p>
                <div class="progress-track">
                    <div class="progress-bar green-bar" id="memoryBar"></div>
                </div>
                <div class="progress-caption">
                    <span>Current usage</span>
                    <span id="memoryCaption">--%</span>
                </div>
            </article>

            <article class="card">
                <div class="metric-top">
                    <span class="metric-title">Disk Usage</span>
                    <div class="metric-icon">▣</div>
                </div>
                <div class="metric-value" id="disk">--%</div>
                <p class="metric-description" id="diskDetail">
                    Storage utilization
                </p>
                <div class="progress-track">
                    <div class="progress-bar orange-bar" id="diskBar"></div>
                </div>
                <div class="progress-caption">
                    <span>Used storage</span>
                    <span id="diskCaption">--%</span>
                </div>
            </article>
        </section>

        <section class="lower-grid">
            <article class="card">
                <h2 class="panel-heading">Resource health</h2>

                <div class="status-row">
                    <div>
                        <div class="status-name">CPU Status</div>
                        <div class="status-detail" id="cpuStatusDetail">
                            Waiting for metrics
                        </div>
                    </div>
                    <span class="status-pill" id="cpuStatus">Checking</span>
                </div>

                <div class="status-row">
                    <div>
                        <div class="status-name">Memory Status</div>
                        <div class="status-detail" id="memoryStatusDetail">
                            Waiting for metrics
                        </div>
                    </div>
                    <span class="status-pill" id="memoryStatus">Checking</span>
                </div>

                <div class="status-row">
                    <div>
                        <div class="status-name">Disk Status</div>
                        <div class="status-detail" id="diskStatusDetail">
                            Waiting for metrics
                        </div>
                    </div>
                    <span class="status-pill" id="diskStatus">Checking</span>
                </div>
            </article>

            <article class="card">
                <h2 class="panel-heading">System information</h2>

                <div class="info-list">
                    <div>
                        <div class="info-label">HOSTNAME</div>
                        <div class="info-value" id="hostname">--</div>
                    </div>
                    <div>
                        <div class="info-label">OPERATING SYSTEM</div>
                        <div class="info-value" id="system">--</div>
                    </div>
                    <div>
                        <div class="info-label">SYSTEM UPTIME</div>
                        <div class="info-value" id="uptime">--</div>
                    </div>
                    <div>
                        <div class="info-label">LAST UPDATED</div>
                        <div class="info-value" id="lastUpdated">--</div>
                    </div>
                </div>
            </article>
        </section>

        <footer class="footer">
            <span>CloudMonitor · Resource Monitoring Dashboard</span>
            <span>Refresh interval: 3 seconds</span>
        </footer>
    </main>
</div>

<script>
    function setMetric(name, value) {
        const percent = Math.max(0, Math.min(100, Number(value)));
        document.getElementById(name).textContent = percent.toFixed(1) + "%";
        document.getElementById(name + "Caption").textContent =
            percent.toFixed(1) + "%";

        const bar = document.getElementById(name + "Bar");
        bar.style.width = percent + "%";

        bar.classList.remove("green-bar", "orange-bar", "red-bar");

        if (percent >= 90) {
            bar.classList.add("red-bar");
        } else if (percent >= 75) {
            bar.classList.add("orange-bar");
        } else if (name === "memory") {
            bar.classList.add("green-bar");
        }
    }

    function setStatus(type, value) {
        const percent = Number(value);
        const pill = document.getElementById(type + "Status");
        const detail = document.getElementById(type + "StatusDetail");

        pill.className = "status-pill";

        if (percent >= 90) {
            pill.textContent = "Critical";
            pill.classList.add("danger");
            detail.textContent = "Very high resource usage";
        } else if (percent >= 75) {
            pill.textContent = "Warning";
            pill.classList.add("warning");
            detail.textContent = "Resource usage is elevated";
        } else {
            pill.textContent = "Healthy";
            detail.textContent = "Usage is within normal range";
        }
    }

    function formatUptime(seconds) {
        const days = Math.floor(seconds / 86400);
        const hours = Math.floor((seconds % 86400) / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);

        return days + "d " + hours + "h " + minutes + "m";
    }

    async function updateDashboard() {
        const connection = document.getElementById("connection");

        try {
            const response = await fetch("/api/metrics", {
                cache: "no-store"
            });

            if (!response.ok) {
                throw new Error("Could not retrieve metrics");
            }

            const data = await response.json();

            setMetric("cpu", data.cpu);
            setMetric("memory", data.memory);
            setMetric("disk", data.disk);

            document.getElementById("memoryDetail").textContent =
                data.memory_used_gb + " GB used of " +
                data.memory_total_gb + " GB RAM";

            document.getElementById("diskDetail").textContent =
                data.disk_used_gb + " GB used · " +
                data.disk_free_gb + " GB free";

            setStatus("cpu", data.cpu);
            setStatus("memory", data.memory);
            setStatus("disk", data.disk);

            document.getElementById("hostname").textContent = data.hostname;
            document.getElementById("system").textContent = data.system;
            document.getElementById("uptime").textContent =
                formatUptime(data.uptime_seconds);
            document.getElementById("lastUpdated").textContent =
                new Date().toLocaleTimeString();

            connection.textContent = "Live";
        } catch (error) {
            connection.textContent = "Connection error";
            console.error(error);
        }
    }

    updateDashboard();
    setInterval(updateDashboard, 3000);
</script>
</body>
</html>
"""


@app.route("/api/metrics")
def metrics():
    if platform.system() == "Windows":
        disk_path = os.environ.get("SystemDrive", "C:") + "\\"
    else:
        disk_path = "/"

    memory = psutil.virtual_memory()
    disk = psutil.disk_usage(disk_path)

    return jsonify({
        "cpu": psutil.cpu_percent(interval=0.2),
        "memory": memory.percent,
        "memory_used_gb": get_size(memory.used),
        "memory_total_gb": get_size(memory.total),
        "disk": disk.percent,
        "disk_used_gb": get_size(disk.used),
        "disk_free_gb": get_size(disk.free),
        "hostname": socket.gethostname(),
        "system": platform.system() + " " + platform.release(),
        "uptime_seconds": int(time.time() - start_time)
    })


if __name__ == "__main__":
    app.run(debug=True)
