#!/bin/bash

# Monitoring script for Docker containers
# Tracks: CPU, Memory, Uptime, Latency

CONTAINER_NAME="${CONTAINER_NAME:-webapp}"
TARGET_URL="${TARGET_URL:-http://webapp:8000}"
LOG_DIR="/logs"

# Create log files
METRICS_LOG="$LOG_DIR/metrics.log"
STATUS_LOG="$LOG_DIR/status.log"
REPORT_LOG="$LOG_DIR/report.log"

# Initialize log files
mkdir -p "$LOG_DIR"
touch "$METRICS_LOG" "$STATUS_LOG" "$REPORT_LOG"

# Function: Get container stats
get_container_stats() {
    local container=$1
    
    # Get CPU and Memory from docker stats
    stats=$(docker stats "$container" --no-stream --format \
        "{{.CPUPerc}},{{.MemUsage}},{{.MemPerc}}")
    
    if [ -n "$stats" ]; then
        echo "$stats"
    else
        echo "0%,0B / 0B,0%"
    fi
}

# Function: Check container uptime
check_uptime() {
    local container=$1
    
    if docker ps --filter "name=$container" --format "{{.Names}}" | grep -q "$container"; then
        echo "UP"
    else
        echo "DOWN"
    fi
}

# Function: Check response code and latency
check_response() {
    local url=$1
    
    # Get HTTP status code and response time
    response=$(curl -o /dev/null -s -w "%{http_code},%{time_total}" "$url")
    
    if [ $? -eq 0 ]; then
        echo "$response"
    else
        echo "000,0.000"
    fi
}

# Main monitoring loop
echo "Starting monitoring for container: $CONTAINER_NAME"
echo "Target URL: $TARGET_URL"
echo "Log directory: $LOG_DIR"

while true; do
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')
    
    # Get metrics
    STATS=$(get_container_stats "$CONTAINER_NAME")
    CPU=$(echo "$STATS" | cut -d',' -f1)
    MEMORY=$(echo "$STATS" | cut -d',' -f2)
    MEMORY_PERCENT=$(echo "$STATS" | cut -d',' -f3)
    
    UPTIME=$(check_uptime "$CONTAINER_NAME")
    
    RESPONSE=$(check_response "$TARGET_URL")
    HTTP_CODE=$(echo "$RESPONSE" | cut -d',' -f1)
    LATENCY=$(echo "$RESPONSE" | cut -d',' -f2)
    
    # Log metrics
    echo "$TIMESTAMP | CPU: $CPU | Memory: $MEMORY_PERCENT | Latency: ${LATENCY}s" >> "$METRICS_LOG"
    
    # Log status
    echo "$TIMESTAMP | Container: $UPTIME | HTTP: $HTTP_CODE" >> "$STATUS_LOG"
    
    # Generate report entry
    cat >> "$REPORT_LOG" << EOF
[$TIMESTAMP]
Container: $CONTAINER_NAME
Status: $UPTIME
CPU Usage: $CPU
Memory: $MEMORY ($MEMORY_PERCENT)
HTTP Response: $HTTP_CODE
Latency: ${LATENCY}s
---
EOF
    
    # Console output
    echo "[$TIMESTAMP] CPU: $CPU | Memory: $MEMORY_PERCENT | Status: $UPTIME | HTTP: $HTTP_CODE | Latency: ${LATENCY}s"
    
    # Wait 30 seconds before next check
    sleep 30
done
