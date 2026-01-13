import boto3
import os
import time
from datetime import datetime, timedelta

# AWS SES Configuration
AWS_REGION = os.getenv('AWS_REGION', 'us-east-1')
SENDER_EMAIL = os.getenv('SENDER_EMAIL')
RECIPIENT_EMAILS = os.getenv('RECIPIENT_EMAILS', '').split(',')

# Alert Configuration
ALERT_COOLDOWN = int(os.getenv('ALERT_COOLDOWN', 300))  # 5 minutes
CHECK_INTERVAL = int(os.getenv('CHECK_INTERVAL', 30))   # 30 seconds
CPU_THRESHOLD = float(os.getenv('CPU_THRESHOLD', 80))
MEMORY_THRESHOLD = float(os.getenv('MEMORY_THRESHOLD', 80))

# Log paths
LOG_DIR = '/logs'
METRICS_LOG = os.path.join(LOG_DIR, 'metrics.log')
STATUS_LOG = os.path.join(LOG_DIR, 'status.log')

# Alert tracking
last_alert_time = {}

def send_email_alert(subject, body, severity='WARNING'):
    """Send email alert via AWS SES"""
    try:
        ses_client = boto3.client('ses', region_name=AWS_REGION)
        
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                .alert-box {{ 
                    background: {'#ff4444' if severity == 'CRITICAL' else '#ffaa44'};
                    color: white;
                    padding: 20px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                .details {{
                    background: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }}
                pre {{
                    background: #2a2a2a;
                    color: #00ff00;
                    padding: 10px;
                    border-radius: 3px;
                    overflow-x: auto;
                }}
            </style>
        </head>
        <body>
            <div class="alert-box">
                <h2>🚨 {severity} ALERT</h2>
                <h3>{subject}</h3>
            </div>
            <div class="details">
                {body.replace(chr(10), '<br>')}
            </div>
            <p><small>Sent from Docker Monitoring System at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</small></p>
        </body>
        </html>
        """
        
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email.strip() for email in RECIPIENT_EMAILS]},
            Message={
                'Subject': {'Data': f"[{severity}] {subject}"},
                'Body': {
                    'Html': {'Data': html_body},
                    'Text': {'Data': body}
                }
            }
        )
        
        print(f"✅ Alert sent successfully! MessageId: {response['MessageId']}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to send alert: {str(e)}")
        return False

def should_send_alert(alert_type):
    """Check if enough time has passed since last alert"""
    now = datetime.now()
    
    if alert_type not in last_alert_time:
        last_alert_time[alert_type] = now
        return True
    
    time_since_last = (now - last_alert_time[alert_type]).total_seconds()
    
    if time_since_last >= ALERT_COOLDOWN:
        last_alert_time[alert_type] = now
        return True
    
    return False

def parse_metrics():
    """Parse latest metrics from log file"""
    try:
        with open(METRICS_LOG, 'r') as f:
            # Read last 10 lines to get recent trends
            lines = f.readlines()[-10:]
            
            if not lines:
                return None
            
            # Parse last line
            last_line = lines[-1]
            parts = last_line.split('|')
            
            timestamp = parts[0].strip()
            cpu = parts[1].split(':')[1].strip().replace('%', '')
            memory = parts[2].split(':')[1].strip().replace('%', '')
            latency = parts[3].split(':')[1].strip().replace('s', '')
            
            return {
                'timestamp': timestamp,
                'cpu': float(cpu),
                'memory': float(memory),
                'latency': float(latency),
                'recent_lines': ''.join(lines)
            }
    
    except Exception as e:
        print(f"Error parsing metrics: {str(e)}")
        return None

def parse_status():
    """Parse latest status from log file"""
    try:
        with open(STATUS_LOG, 'r') as f:
            lines = f.readlines()[-5:]
            
            if not lines:
                return None
            
            last_line = lines[-1]
            parts = last_line.split('|')
            
            timestamp = parts[0].strip()
            container_status = parts[1].split(':')[1].strip()
            http_code = parts[2].split(':')[1].strip()
            
            return {
                'timestamp': timestamp,
                'container_status': container_status,
                'http_code': http_code,
                'recent_lines': ''.join(lines)
            }
    
    except Exception as e:
        print(f"Error parsing status: {str(e)}")
        return None

def check_and_alert():
    """Main alert checking logic"""
    metrics = parse_metrics()
    status = parse_status()
    
    if not metrics or not status:
        print("⏳ Waiting for metrics...")
        return
    
    alerts = []
    
    # Check for critical: container down
    if status['container_status'] == 'DOWN':
        if should_send_alert('container_down'):
            subject = "Container is DOWN!"
            body = f"""
Container Status: {status['container_status']}
HTTP Response: {status['http_code']}
Timestamp: {status['timestamp']}

Recent Status History:
{status['recent_lines']}

Action Required: Investigate and restart container immediately.
"""
            send_email_alert(subject, body, severity='CRITICAL')
            alerts.append('container_down')
    
    # Check for critical: unhealthy response
    if status['http_code'] != '200':
        if should_send_alert('unhealthy_response'):
            subject = f"Unhealthy HTTP Response: {status['http_code']}"
            body = f"""
HTTP Response Code: {status['http_code']} (Expected: 200)
Container Status: {status['container_status']}
Timestamp: {status['timestamp']}

Recent Status History:
{status['recent_lines']}

Action Required: Check application logs and health.
"""
            send_email_alert(subject, body, severity='CRITICAL')
            alerts.append('unhealthy_response')
    
    # Check for critical: high CPU
    if metrics['cpu'] > CPU_THRESHOLD:
        if should_send_alert('high_cpu'):
            subject = f"High CPU Usage: {metrics['cpu']}%"
            body = f"""
CPU Usage: {metrics['cpu']}% (Threshold: {CPU_THRESHOLD}%)
Memory Usage: {metrics['memory']}%
Latency: {metrics['latency']}s
Timestamp: {metrics['timestamp']}

Recent Metrics:
{metrics['recent_lines']}

Action Required: Investigate CPU-intensive processes or scale resources.
"""
            send_email_alert(subject, body, severity='CRITICAL')
            alerts.append('high_cpu')
    
    # Check for warning: high memory
    if metrics['memory'] > MEMORY_THRESHOLD:
        if should_send_alert('high_memory'):
            subject = f"High Memory Usage: {metrics['memory']}%"
            body = f"""
Memory Usage: {metrics['memory']}% (Threshold: {MEMORY_THRESHOLD}%)
CPU Usage: {metrics['cpu']}%
Latency: {metrics['latency']}s
Timestamp: {metrics['timestamp']}

Recent Metrics:
{metrics['recent_lines']}

Action Required: Check for memory leaks or scale resources.
"""
            send_email_alert(subject, body, severity='WARNING')
            alerts.append('high_memory')
    
    # Check for warning: high latency
    if metrics['latency'] > 1.0:
        if should_send_alert('high_latency'):
            subject = f"High Latency: {metrics['latency']}s"
            body = f"""
Response Latency: {metrics['latency']}s (Threshold: 1.0s)
CPU Usage: {metrics['cpu']}%
Memory Usage: {metrics['memory']}%
Timestamp: {metrics['timestamp']}

Recent Metrics:
{metrics['recent_lines']}

Action Required: Investigate slow database queries or external dependencies.
"""
            send_email_alert(subject, body, severity='WARNING')
            alerts.append('high_latency')
    
    # Status output
    if alerts:
        print(f"⚠️  Alerts sent: {', '.join(alerts)}")
    else:
        print(f"✅ All metrics normal | CPU: {metrics['cpu']}% | Memory: {metrics['memory']}% | Latency: {metrics['latency']}s")

def main():
    """Main alert service loop"""
    print("=" * 60)
    print("🔔 Alert Service Started")
    print(f"Sender: {SENDER_EMAIL}")
    print(f"Recipients: {', '.join(RECIPIENT_EMAILS)}")
    print(f"Check Interval: {CHECK_INTERVAL}s")
    print(f"Alert Cooldown: {ALERT_COOLDOWN}s")
    print(f"CPU Threshold: {CPU_THRESHOLD}%")
    print(f"Memory Threshold: {MEMORY_THRESHOLD}%")
    print("=" * 60)
    
    # Wait for logs to be available
    print("Waiting for monitoring logs...")
    time.sleep(30)
    
    while True:
        try:
            check_and_alert()
        except Exception as e:
            print(f"❌ Error in alert check: {str(e)}")
        
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    main()
