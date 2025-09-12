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
from datetime import datetime, timedelta
import re
from collections import deque
import time

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

def parse_log_timestamp(line, log_type='watchdog'):
    """Extract timestamp from a log line"""
    if log_type == 'watchdog':
        pattern = r'^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d+)'
        match = re.match(pattern, line.strip())
        if match:
            try:
                # Parse timestamp: 2025-09-10 23:34:13,246
                timestamp_str = match.group(1)
                return datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S,%f')
            except ValueError:
                return None
    return None

def filter_logs_by_time(lines, start_time=None, end_time=None, log_type='watchdog'):
    """Filter log lines by time range"""
    if not start_time and not end_time:
        return lines
    
    filtered_lines = []
    for line in lines:
        timestamp = parse_log_timestamp(line, log_type)
        if timestamp:
            if start_time and timestamp < start_time:
                continue
            if end_time and timestamp > end_time:
                continue
            filtered_lines.append(line)
        else:
            # Include lines without timestamps (stack traces, etc.)
            filtered_lines.append(line)
    
    return filtered_lines

def search_logs_regex(lines, pattern, case_sensitive=True):
    """Search logs using regex pattern"""
    if not pattern:
        return lines
    
    try:
        flags = 0 if case_sensitive else re.IGNORECASE
        regex = re.compile(pattern, flags)
        return [line for line in lines if regex.search(line)]
    except re.error:
        # If regex is invalid, fall back to simple string search
        search_func = (lambda line: pattern in line) if case_sensitive else (lambda line: pattern.lower() in line.lower())
        return [line for line in lines if search_func(line)]

def get_log_statistics(lines, log_type='watchdog'):
    """Generate statistics from log lines"""
    stats = {
        'total_lines': len(lines),
        'levels': {'ERROR': 0, 'WARNING': 0, 'INFO': 0, 'DEBUG': 0, 'UNKNOWN': 0},
        'time_range': {'start': None, 'end': None},
        'lines_per_hour': {}
    }
    
    timestamps = []
    for line in lines:
        level = extract_log_level(line, log_type)
        if level and level in stats['levels']:
            stats['levels'][level] += 1
        else:
            stats['levels']['UNKNOWN'] += 1
        
        timestamp = parse_log_timestamp(line, log_type)
        if timestamp:
            timestamps.append(timestamp)
            hour_key = timestamp.strftime('%Y-%m-%d %H:00')
            stats['lines_per_hour'][hour_key] = stats['lines_per_hour'].get(hour_key, 0) + 1
    
    if timestamps:
        stats['time_range']['start'] = min(timestamps).isoformat()
        stats['time_range']['end'] = max(timestamps).isoformat()
    
    return stats
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
    """API endpoint to get formatted log files with advanced filtering"""
    log_type = request.args.get('type', 'watchdog')
    lines = int(request.args.get('lines', 50))
    level_filter = request.args.get('level', 'ALL')
    
    # New advanced search parameters
    search_pattern = request.args.get('search', '')
    case_sensitive = request.args.get('case_sensitive', 'true').lower() == 'true'
    start_time_str = request.args.get('start_time', '')
    end_time_str = request.args.get('end_time', '')
    include_stats = request.args.get('include_stats', 'false').lower() == 'true'
    
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
    
    # Parse time filters
    start_time = None
    end_time = None
    try:
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str)
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': f'Invalid time format: {str(e)}',
            'expected_format': 'YYYY-MM-DDTHH:MM:SS'
        })
    
    # Read more lines initially to account for filtering
    initial_lines = lines * 3 if any([level_filter != 'ALL', search_pattern, start_time, end_time]) else lines
    raw_lines = tail_file(log_files[log_type], initial_lines)
    
    # Apply time filtering first
    if start_time or end_time:
        raw_lines = filter_logs_by_time(raw_lines, start_time, end_time, log_type)
    
    # Apply regex search
    if search_pattern:
        raw_lines = search_logs_regex(raw_lines, search_pattern, case_sensitive)
    
    # Apply level filtering
    if level_filter and level_filter.upper() != 'ALL':
        filtered_lines = filter_logs_by_level(raw_lines, log_type, level_filter)
    else:
        filtered_lines = raw_lines
    
    # Format the lines
    formatted_lines = [format_log_line(line, log_type) for line in filtered_lines if line.strip()]
    
    # Get statistics if requested
    stats = None
    if include_stats:
        stats = get_log_statistics(filtered_lines, log_type)
    
    # Limit final results
    final_lines = formatted_lines[-lines:] if len(formatted_lines) > lines else formatted_lines
    
    response = {
        'success': True,
        'type': log_type,
        'level_filter': level_filter,
        'search_pattern': search_pattern,
        'case_sensitive': case_sensitive,
        'time_range': {
            'start': start_time_str,
            'end': end_time_str
        },
        'lines': final_lines,
        'total_lines': len(final_lines),
        'filtered_from': len(raw_lines),
        'count': len(final_lines),
        'timestamp': datetime.now().isoformat()
    }
    
    if stats:
        response['statistics'] = stats
    
    return jsonify(response)

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

@app.route('/api/export')
def export_logs():
    """API endpoint to export logs in various formats"""
    export_format = request.args.get('format', 'json').lower()
    log_type = request.args.get('type', 'watchdog')
    lines = int(request.args.get('lines', 100))
    
    # Get filtered logs using the same logic as get_logs
    level_filter = request.args.get('level', 'ALL')
    search_pattern = request.args.get('search', '')
    case_sensitive = request.args.get('case_sensitive', 'true').lower() == 'true'
    start_time_str = request.args.get('start_time', '')
    end_time_str = request.args.get('end_time', '')
    
    log_files = {
        'watchdog': os.path.join(LOG_DIR, 'watchdog.log'),
        'metrics': os.path.join(LOG_DIR, 'metrics.log')
    }
    
    if log_type not in log_files:
        return jsonify({'success': False, 'error': 'Invalid log type'})
    
    # Parse time filters
    start_time = None
    end_time = None
    try:
        if start_time_str:
            start_time = datetime.fromisoformat(start_time_str)
        if end_time_str:
            end_time = datetime.fromisoformat(end_time_str)
    except ValueError:
        pass  # Ignore invalid time formats for export
    
    # Get filtered logs
    raw_lines = tail_file(log_files[log_type], lines * 2)
    
    if start_time or end_time:
        raw_lines = filter_logs_by_time(raw_lines, start_time, end_time, log_type)
    
    if search_pattern:
        raw_lines = search_logs_regex(raw_lines, search_pattern, case_sensitive)
    
    if level_filter and level_filter.upper() != 'ALL':
        raw_lines = filter_logs_by_level(raw_lines, log_type, level_filter)
    
    final_lines = raw_lines[-lines:] if len(raw_lines) > lines else raw_lines
    
    export_data = {
        'export_info': {
            'timestamp': datetime.now().isoformat(),
            'log_type': log_type,
            'total_lines': len(final_lines),
            'filters': {
                'level': level_filter,
                'search': search_pattern,
                'time_range': {'start': start_time_str, 'end': end_time_str}
            }
        },
        'logs': []
    }
    
    # Parse each log line into structured data
    for line in final_lines:
        line = line.strip()
        if not line:
            continue
            
        log_entry = {'raw': line}
        
        # Extract structured data
        timestamp = parse_log_timestamp(line, log_type)
        if timestamp:
            log_entry['timestamp'] = timestamp.isoformat()
        
        level = extract_log_level(line, log_type)
        if level:
            log_entry['level'] = level
        
        export_data['logs'].append(log_entry)
    
    if export_format == 'json':
        return jsonify(export_data)
    
    elif export_format == 'csv':
        import csv
        from io import StringIO
        
        output = StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(['Timestamp', 'Level', 'Message'])
        
        # Write data
        for log_entry in export_data['logs']:
            writer.writerow([
                log_entry.get('timestamp', ''),
                log_entry.get('level', ''),
                log_entry['raw']
            ])
        
        return output.getvalue(), 200, {
            'Content-Type': 'text/csv',
            'Content-Disposition': f'attachment; filename=monitoring-logs-{datetime.now().strftime("%Y%m%d-%H%M%S")}.csv'
        }
    
    else:
        return jsonify({'success': False, 'error': 'Unsupported export format. Use json or csv.'})

@app.route('/api/metrics/advanced')
def get_advanced_metrics():
    """API endpoint to get enhanced metrics with time series data"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # Get metrics from different time periods
        time_periods = {
            'last_hour': 'NOW() - INTERVAL \'1 hour\'',
            'last_6_hours': 'NOW() - INTERVAL \'6 hours\'',
            'last_24_hours': 'NOW() - INTERVAL \'24 hours\'',
            'last_week': 'NOW() - INTERVAL \'7 days\''
        }
        
        metrics = {}
        
        for period_name, period_sql in time_periods.items():
            cur.execute(f"""
                SELECT 
                    ROUND(AVG(CASE WHEN status = 'PASS' THEN 100 ELSE 0 END), 1) as availability,
                    ROUND(AVG(response_time_ms), 2) as avg_response_time,
                    ROUND(MAX(response_time_ms), 2) as max_response_time,
                    ROUND(MIN(response_time_ms), 2) as min_response_time,
                    COUNT(*) as total_checks,
                    COUNT(CASE WHEN status = 'FAIL' THEN 1 END) as failed_checks
                FROM checks 
                WHERE created_at > {period_sql}
            """)
            
            result = cur.fetchone()
            if result:
                metrics[period_name] = {
                    'availability': result[0] or 0,
                    'avg_response_time': result[1] or 0,
                    'max_response_time': result[2] or 0,
                    'min_response_time': result[3] or 0,
                    'total_checks': result[4] or 0,
                    'failed_checks': result[5] or 0,
                    'error_rate': round((result[5] or 0) / max(result[4] or 1, 1) * 100, 2)
                }
        
        # Get time series data for charts (last 24 hours, hourly buckets)
        cur.execute("""
            SELECT 
                DATE_TRUNC('hour', created_at) as hour,
                target,
                ROUND(AVG(CASE WHEN status = 'PASS' THEN 100 ELSE 0 END), 1) as availability,
                ROUND(AVG(response_time_ms), 2) as avg_response_time,
                COUNT(*) as check_count
            FROM checks 
            WHERE created_at > NOW() - INTERVAL '24 hours'
            GROUP BY DATE_TRUNC('hour', created_at), target
            ORDER BY hour, target
        """)
        
        time_series = []
        for row in cur.fetchall():
            time_series.append({
                'hour': row[0].isoformat(),
                'target': row[1],
                'availability': row[2],
                'avg_response_time': row[3],
                'check_count': row[4]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'metrics': metrics,
            'time_series': time_series,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        })
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

@app.route('/api/system_status')
def get_system_status():
    """API endpoint to get system status"""
    try:
        # Get container status using docker command
        result = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], 
                              capture_output=True, text=True, check=True)
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
