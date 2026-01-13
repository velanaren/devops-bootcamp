from flask import Flask, render_template_string, jsonify
import os
import subprocess
from datetime import datetime

app = Flask(__name__)

LOG_DIR = os.getenv('LOG_DIR', '/logs')
METRICS_LOG = os.path.join(LOG_DIR, 'metrics.log')
STATUS_LOG = os.path.join(LOG_DIR, 'status.log')

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Container Monitoring Dashboard</title>
    <meta http-equiv="refresh" content="10">
    <style>
        body {
            font-family: 'Courier New', monospace;
            background: #1a1a1a;
            color: #00ff00;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            border-bottom: 2px solid #00ff00;
            padding-bottom: 10px;
        }
        .metric-box {
            background: #2a2a2a;
            border: 1px solid #00ff00;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
        }
        .status-up { color: #00ff00; }
        .status-down { color: #ff0000; }
        .warning { color: #ffaa00; }
        .critical { color: #ff0000; }
        pre {
            background: #0a0a0a;
            padding: 10px;
            border-radius: 3px;
            overflow-x: auto;
        }
        .refresh-info {
            color: #888;
            font-size: 12px;
            text-align: right;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Container Monitoring Dashboard</h1>
        <div class="refresh-info">Auto-refresh: 10s | Last update: {{ timestamp }}</div>
        
        <div class="metric-box">
            <h2>📊 Current Status</h2>
            <p><strong>Container:</strong> <span class="{{ status_class }}">{{ container_status }}</span></p>
            <p><strong>HTTP Response:</strong> {{ http_code }}</p>
            <p><strong>CPU Usage:</strong> <span class="{{ cpu_class }}">{{ cpu_usage }}</span></p>
            <p><strong>Memory Usage:</strong> <span class="{{ mem_class }}">{{ mem_usage }}</span></p>
            <p><strong>Latency:</strong> {{ latency }}s</p>
        </div>
        
        <div class="metric-box">
            <h2>📈 Recent Metrics (Last 10 entries)</h2>
            <pre>{{ recent_metrics }}</pre>
        </div>
        
        <div class="metric-box">
            <h2>🚦 Status History (Last 10 entries)</h2>
            <pre>{{ recent_status }}</pre>
        </div>
        
        <div class="metric-box">
            <h2>⚠️ Alerts</h2>
            <pre>{{ alerts }}</pre>
        </div>
    </div>
</body>
</html>
"""

def read_last_lines(filepath, n=10):
    """Read last n lines from a file"""
    try:
        with open(filepath, 'r') as f:
            lines = f.readlines()
            return ''.join(lines[-n:]) if lines else 'No data yet'
    except FileNotFoundError:
        return 'Log file not found'

def parse_latest_metrics():
    """Parse the latest metrics from logs"""
    try:
        with open(METRICS_LOG, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                # Parse: "2024-01-09 10:30:00 | CPU: 25.5% | Memory: 40.2% | Latency: 0.125s"
                parts = last_line.split('|')
                
                cpu = parts[1].split(':')[1].strip() if len(parts) > 1 else '0%'
                mem = parts[2].split(':')[1].strip() if len(parts) > 2 else '0%'
                latency = parts[3].split(':')[1].strip().replace('s', '') if len(parts) > 3 else '0.0'
                
                return cpu, mem, latency
    except:
        pass
    return '0%', '0%', '0.0'

def parse_latest_status():
    """Parse the latest status from logs"""
    try:
        with open(STATUS_LOG, 'r') as f:
            lines = f.readlines()
            if lines:
                last_line = lines[-1]
                parts = last_line.split('|')
                
                container_status = parts[1].split(':')[1].strip() if len(parts) > 1 else 'UNKNOWN'
                http_code = parts[2].split(':')[1].strip() if len(parts) > 2 else '000'
                
                return container_status, http_code
    except:
        pass
    return 'UNKNOWN', '000'

def get_alert_class(cpu_str, mem_str):
    """Determine alert class based on usage"""
    try:
        cpu = float(cpu_str.replace('%', ''))
        mem = float(mem_str.replace('%', ''))
        
        if cpu > 80 or mem > 80:
            return 'critical'
        elif cpu > 60 or mem > 60:
            return 'warning'
    except:
        pass
    return ''

def check_alerts(cpu, mem, latency, status, http_code):
    """Generate alert messages"""
    alerts = []
    
    try:
        cpu_val = float(cpu.replace('%', ''))
        mem_val = float(mem.replace('%', ''))
        lat_val = float(latency)
        
        if status == 'DOWN':
            alerts.append('🔴 CRITICAL: Container is DOWN!')
        
        if http_code != '200':
            alerts.append(f'🔴 CRITICAL: HTTP response code {http_code} (expected 200)')
        
        if cpu_val > 80:
            alerts.append(f'🔴 CRITICAL: CPU usage at {cpu} (threshold: 80%)')
        elif cpu_val > 60:
            alerts.append(f'🟡 WARNING: CPU usage at {cpu} (threshold: 60%)')
        
        if mem_val > 80:
            alerts.append(f'🔴 CRITICAL: Memory usage at {mem} (threshold: 80%)')
        elif mem_val > 60:
            alerts.append(f'🟡 WARNING: Memory usage at {mem} (threshold: 60%)')
        
        if lat_val > 1.0:
            alerts.append(f'🟡 WARNING: High latency {latency}s (threshold: 1.0s)')
        
        if not alerts:
            alerts.append('✅ All systems normal')
    
    except Exception as e:
        alerts.append(f'⚠️ Error parsing metrics: {str(e)}')
    
    return '\n'.join(alerts)

@app.route('/')
def dashboard():
    """Main dashboard view"""
    cpu, mem, latency = parse_latest_metrics()
    container_status, http_code = parse_latest_status()
    
    status_class = 'status-up' if container_status == 'UP' else 'status-down'
    cpu_class = get_alert_class(cpu, '0%')
    mem_class = get_alert_class('0%', mem)
    
    alerts = check_alerts(cpu, mem, latency, container_status, http_code)
    
    return render_template_string(
        HTML_TEMPLATE,
        timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        container_status=container_status,
        status_class=status_class,
        http_code=http_code,
        cpu_usage=cpu,
        cpu_class=cpu_class,
        mem_usage=mem,
        mem_class=mem_class,
        latency=latency,
        recent_metrics=read_last_lines(METRICS_LOG, 10),
        recent_status=read_last_lines(STATUS_LOG, 10),
        alerts=alerts
    )

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics"""
    cpu, mem, latency = parse_latest_metrics()
    container_status, http_code = parse_latest_status()
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'container_status': container_status,
        'http_code': http_code,
        'cpu': cpu,
        'memory': mem,
        'latency': latency
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8001, debug=False)

