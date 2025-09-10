#!/usr/bin/env python3
"""
Multi-Container Monitoring Log API Server
Dynamic log reading and metrics API using Python Flask
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import json
import subprocess
import psycopg2
from datetime import datetime
import re
from collections import deque

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
LOG_DIR = '/var/log/monitoring'
DB_CONFIG = {
    'host': 'db',
    'database': 'monitoring',
    'user': 'monitoruser',
    'password': 'monitorpass',
    'port': 5432
}

def tail_file(filename, lines=50):
    """Read last N lines from a file efficiently"""
    if not os.path.exists(filename):
        return [f"Error: File not found - {filename}"]
    
    try:
        # Use deque for efficient tail operation
        with open(filename, 'r', encoding='utf-8', errors='ignore') as f:
            return list(deque(f, maxlen=lines))
    except Exception as e:
        return [f"Error reading file: {str(e)}"]

def extract_log_level(line, log_type='watchdog'):
    """Extract log level from a log line"""
    if log_type == 'watchdog':
        # Format: 2025-09-02 01:58:16,550 - watchdog - INFO - [main_loop:241] - Message
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (\w+) - (\w+) - (.+)$'
        match = re.match(pattern, line.strip())
        if match:
            return match.group(3).upper()  # Return the log level (INFO, ERROR, WARNING, etc.)
    return None

def filter_logs_by_level(lines, log_type='watchdog', level_filter=None):
    """Filter log lines by log level"""
    if not level_filter or level_filter.upper() == 'ALL':
        return lines
    
    level_filter = level_filter.upper()
    filtered_lines = []
    
    for line in lines:
        line_level = extract_log_level(line, log_type)
        if line_level == level_filter:
            filtered_lines.append(line)
    
    return filtered_lines

def format_log_line(line, log_type='watchdog'):
    """Format log lines with syntax highlighting"""
    line = line.strip()
    if not line:
        return ''
    
    if log_type == 'watchdog':
        # Format: 2025-09-02 01:58:16,550 - watchdog - INFO - [main_loop:241] - Message
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (\w+) - (\w+) - (.+)$'
        match = re.match(pattern, line)
        if match:
            timestamp, logger, level, message = match.groups()
            level_class = level.lower()
            return f'<span class="timestamp">{timestamp}</span> - <span class="log-{level_class}">{level}</span> - {message}'
    
    elif log_type == 'metrics':
        # Format: 2025-09-02 01:58:16,842 - {"timestamp": "...", "metric": "...", ...}
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+) - (.+)$'
        match = re.match(pattern, line)
        if match:
            timestamp, json_data = match.groups()
            try:
                decoded = json.loads(json_data)
                metric = decoded.get('metric', 'unknown')
                value = decoded.get('value', 'N/A')
                tags = decoded.get('tags', {})
                
                tag_str = ''
                if tags:
                    tag_pairs = [f"{k}={v}" for k, v in tags.items()]
                    tag_str = f' [{", ".join(tag_pairs)}]'
                
                return f'<span class="timestamp">{timestamp}</span> - <span class="log-info">{metric}</span>: <strong>{value}</strong>{tag_str}'
            except json.JSONDecodeError:
                pass
    
    # Fallback: return escaped line
    return line.replace('<', '&lt;').replace('>', '&gt;')

def get_database_metrics():
    """Calculate real-time metrics from database"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get metrics from last hour
        cur.execute("""
            SELECT 
                ROUND(AVG(CASE WHEN status = 'PASS' THEN 100 ELSE 0 END), 1) as availability,
                ROUND(AVG(response_time_ms), 0) as avg_response_time,
                ROUND(AVG(CASE WHEN status = 'FAIL' THEN 100 ELSE 0 END), 1) as error_rate,
                COUNT(*) as total_checks
            FROM checks 
            WHERE created_at > NOW() - INTERVAL '1 hour'
        """)
        
        result = cur.fetchone()
        conn.close()
        
        if result:
            return {
                'availability': result[0] or 0,
                'avg_response_time': result[1] or 0,
                'error_rate': result[2] or 0,
                'total_checks': result[3] or 0
            }
    except Exception as e:
        print(f"Database error: {e}")
        return {
            'availability': 'DB Error',
            'avg_response_time': 'DB Error', 
            'error_rate': 'DB Error',
            'total_checks': 0
        }

def get_container_logs(container, lines=30):
    """Get Docker container logs"""
    allowed_containers = ['watchdog', 'web1', 'web2', 'db', 'log-viewer']
    
    if container not in allowed_containers:
        return [f"Error: Invalid container '{container}'"]
    
    try:
        result = subprocess.run(
            ['docker', 'logs', container, '--tail', str(lines)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return result.stdout.split('\n') if result.stdout else ['No logs available']
        else:
            return [f"Error getting logs: {result.stderr}"]
    except subprocess.TimeoutExpired:
        return ["Error: Timeout getting container logs"]
    except Exception as e:
        return [f"Error: {str(e)}"]

@app.route('/api/logs')
def get_logs():
    """API endpoint to get formatted log files with optional log level filtering"""
    log_type = request.args.get('type', 'watchdog')
    lines = int(request.args.get('lines', 50))
    level_filter = request.args.get('level', 'ALL')  # New parameter for log level filtering
    
    log_files = {
        'watchdog': os.path.join(LOG_DIR, 'watchdog.log'),
        'metrics': os.path.join(LOG_DIR, 'metrics.log')
    }
    
    if log_type not in log_files:
        return jsonify({
            'success': False,
            'error': 'Invalid log type',
            'available_types': list(log_files.keys())
        })
    
    # Read raw log lines
    raw_lines = tail_file(log_files[log_type], lines * 2)  # Read more lines to account for filtering
    
    # Filter by log level if specified
    if level_filter and level_filter.upper() != 'ALL':
        filtered_lines = filter_logs_by_level(raw_lines, log_type, level_filter)
        # If we don't have enough filtered lines, read more from the file
        if len(filtered_lines) < lines and len(raw_lines) == lines * 2:
            raw_lines = tail_file(log_files[log_type], lines * 5)  # Read even more lines
            filtered_lines = filter_logs_by_level(raw_lines, log_type, level_filter)
    else:
        filtered_lines = raw_lines
    
    # Format the lines
    formatted_lines = [format_log_line(line, log_type) for line in filtered_lines if line.strip()]
    
    return jsonify({
        'success': True,
        'type': log_type,
        'level_filter': level_filter,
        'lines': formatted_lines[-lines:],  # Get last N lines
        'total_lines': len(formatted_lines),
        'count': len(formatted_lines[-lines:]),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get real-time system metrics"""
    metrics = get_database_metrics()
    
    return jsonify({
        'success': True,
        'metrics': metrics,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/log_levels')
def get_log_levels():
    """API endpoint to get available log levels from log files"""
    log_type = request.args.get('type', 'watchdog')
    
    log_files = {
        'watchdog': os.path.join(LOG_DIR, 'watchdog.log'),
        'metrics': os.path.join(LOG_DIR, 'metrics.log')
    }
    
    if log_type not in log_files:
        return jsonify({
            'success': False,
            'error': 'Invalid log type',
            'available_types': list(log_files.keys())
        })
    
    # Read recent log lines to extract available levels
    raw_lines = tail_file(log_files[log_type], 500)  # Read more lines to get better sample
    levels = set()
    
    for line in raw_lines:
        level = extract_log_level(line, log_type)
        if level:
            levels.add(level)
    
    # Sort levels by severity (most important first)
    level_priority = {'ERROR': 1, 'WARNING': 2, 'WARN': 2, 'INFO': 3, 'DEBUG': 4}
    sorted_levels = sorted(levels, key=lambda x: level_priority.get(x, 5))
    
    return jsonify({
        'success': True,
        'type': log_type,
        'available_levels': ['ALL'] + sorted_levels,
        'level_counts': {level: sum(1 for line in raw_lines if extract_log_level(line, log_type) == level) for level in sorted_levels},
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/container_logs')
def get_container_logs_endpoint():
    """API endpoint to get Docker container logs"""
    container = request.args.get('container', 'watchdog')
    lines = int(request.args.get('lines', 30))
    
    logs = get_container_logs(container, lines)
    
    return jsonify({
        'success': True,
        'container': container,
        'logs': logs,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/system_status')
def get_system_status():
    """API endpoint to get overall system status"""
    try:
        # Check if containers are running
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, timeout=5)
        running_containers = result.stdout.strip().split('\n') if result.stdout else []
        
        expected_containers = ['watchdog', 'web1', 'web2', 'db', 'log-viewer']
        container_status = {}
        
        for container in expected_containers:
            container_status[container] = container in running_containers
        
        overall_health = all(container_status.values())
        
        return jsonify({
            'success': True,
            'overall_health': overall_health,
            'containers': container_status,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'monitoring-log-api',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    print("Starting Multi-Container Monitoring Log API Server...")
    print(f"Log directory: {LOG_DIR}")
    print("Available endpoints:")
    print("  /api/logs?type=watchdog&lines=50&level=INFO")
    print("  /api/log_levels?type=watchdog")
    print("  /api/metrics")
    print("  /api/container_logs?container=watchdog&lines=30")
    print("  /api/system_status")
    print("  /health")
    print("\nLog level filtering options:")
    print("  - ALL: Show all log levels")
    print("  - ERROR: Show only error messages")
    print("  - WARNING/WARN: Show only warnings")
    print("  - INFO: Show only info messages")
    print("  - DEBUG: Show only debug messages")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
