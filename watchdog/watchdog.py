import os, time, smtplib, socket, json, logging
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import requests
import psycopg2
import threading
from logging.handlers import RotatingFileHandler

# Enhanced logging setup for Part 2
def setup_logging():
    log_level = getattr(logging, os.getenv("LOG_LEVEL", "INFO").upper())
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(funcName)s:%(lineno)d] - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Console handler (for docker logs)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(simple_formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)
    
    # File handlers (for persistent logs)
    os.makedirs('/var/log/velaris', exist_ok=True)
    
    # Main application log
    try:
        app_handler = RotatingFileHandler(
            '/var/log/velaris/watchdog.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        )
        app_handler.setFormatter(detailed_formatter)
        app_handler.setLevel(log_level)
        root_logger.addHandler(app_handler)
    except:
        pass  # Fall back to console only if file logging fails
    
    # Metrics logger (structured for analysis)
    metrics_logger = logging.getLogger('metrics')
    try:
        metrics_handler = RotatingFileHandler(
            '/var/log/velaris/metrics.log',
            maxBytes=5*1024*1024,   # 5MB
            backupCount=10
        )
        metrics_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
        metrics_logger.addHandler(metrics_handler)
        metrics_logger.setLevel(logging.INFO)
        metrics_logger.propagate = False
    except:
        pass  # Fall back to console if file logging fails
    
    return logging.getLogger('watchdog'), metrics_logger

# Configuration
TZ = os.getenv("TARGET_TIMEZONE", "Asia/Colombo")
TARGETS = [t.strip() for t in os.getenv("WEB_TARGETS", "web1:80,web2:80").split(",")]
EXPECT_TEXT = os.getenv("EXPECT_TEXT", "Velaris Demo OK")
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL_SEC", "60"))
MAX_DRIFT = int(os.getenv("MAX_ALLOWED_DRIFT_SEC", "5"))

DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "velaris")
DB_USER = os.getenv("DB_USER", "velaris")
DB_PASSWORD = os.getenv("DB_PASSWORD", "velaris")

SMTP_HOST = os.getenv("SMTP_HOST", "mailhog")
SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
SMTP_FROM = os.getenv("SMTP_FROM", "alerts@velaris.local")
SMTP_TO = os.getenv("SMTP_TO", "support@velaris.local")
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")

# Performance tracking for enhanced metrics
# Global variables
logger = None
metrics_logger = None

# Enhanced monitoring configuration
performance_metrics = {
    'response_times': [],
    'check_count': 0,
    'error_count': 0,
    'start_time': datetime.now()
}

def log_metric(metric_name, value, tags=None):
    """Log structured metrics for analysis"""
    try:
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
            'tags': tags or {}
        }
        metrics_logger.info(json.dumps(metric_data))
    except:
        pass  # Don't break main flow if metrics logging fails

# Mount points that mirror each web's html volume
# map "web1:80" -> "/sites/web1/index.html"
def site_path_for(target):
    name = target.split(":")[0]
    return f"/sites/{name}/index.html"

def db_conn():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )

def send_alert(subject, body):
    try:
        alert_start = time.time()
        logger.info(f"Sending alert: {subject}")
        
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = SMTP_TO
        
        if SMTP_HOST != "mailhog" and SMTP_USER and SMTP_PASSWORD:
            logger.info("Using authenticated SMTP with TLS")
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                s.starttls()
                s.login(SMTP_USER, SMTP_PASSWORD)
                s.sendmail(SMTP_FROM, [SMTP_TO], msg.as_string())
        else:
            logger.info("Using simple SMTP (MailHog)")
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as s:
                s.sendmail(SMTP_FROM, [SMTP_TO], msg.as_string())
        
        alert_time = time.time() - alert_start
        logger.info(f"Alert sent successfully in {alert_time:.2f}s")
        
        # Log metric for alert performance
        log_metric('alert_delivery_time', alert_time, {'type': 'email', 'status': 'success'})
        
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")
        log_metric('alert_delivery_failure', 1, {'type': 'email', 'error': str(e)})
        performance_metrics['error_count'] += 1

def fetch_world_time():
    # Enhanced logging for API performance
    api_start = time.time()
    logger.info("Fetching world time...")
    logger.info("Attempting to fetch world time from external APIs...")
    
    try:
        url = "http://worldtimeapi.org/api/timezone/Asia/Colombo"
        logger.info(f"Trying HTTP: {url}")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            api_time = time.time() - api_start
            logger.info(f"Successfully fetched world time via HTTP in {api_time:.2f}s: {data['datetime']}")
            
            # Log API performance metric
            log_metric('api_response_time', api_time, {'api': 'worldtimeapi', 'status': 'success'})
            
            return datetime.fromisoformat(data["datetime"])
    except Exception as e:
        logger.warning(f"HTTP API failed: {e}")
        log_metric('api_failure', 1, {'api': 'worldtimeapi', 'error': str(e)})
    
    # Fallback: Use system time
    logger.warning("External APIs unavailable, using system time as reference")
    system_time = datetime.now().astimezone()
    logger.info(f"Using system time as fallback: {system_time}")
    
    # Log fallback usage
    log_metric('time_source_fallback', 1, {'source': 'system_time'})
    
    return system_time

def get_local_time():
    # Get local time using the container's timezone setting
    return datetime.now().astimezone()

def update_homepage(target, fetched_dt, local_dt, container_id):
    content = f"""<!doctype html>
<html>
<head><meta charset="utf-8"><title>Velaris Demo</title></head>
<body style="font-family: system-ui; max-width: 680px; margin: 40px auto;">
  <h1>Velaris Demo OK</h1>
  <p><strong>Container:</strong> {container_id}</p>
  <p><strong>Fetched time ({TZ} via worldtimeapi.org):</strong> {fetched_dt.isoformat()}</p>
  <p><strong>Local time (container):</strong> {local_dt.isoformat()}</p>
  <p>Served by lightweight NGINX. This page is updated by the watchdog.</p>
</body>
</html>
"""
    path = site_path_for(target)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def http_check(target):
    http_start = time.time()
    host, port = target.split(":")
    url = f"http://{host}:{port}/"
    
    try:
        r = requests.get(url, timeout=10)
        http_time = time.time() - http_start
        status = r.status_code
        contains = (EXPECT_TEXT in r.text)
        
        # Log HTTP performance metric
        log_metric('http_response_time', http_time, {
            'target': target, 
            'status_code': status,
            'content_valid': contains
        })
        
        # Track response times for availability calculation
        performance_metrics['response_times'].append(http_time)
        if len(performance_metrics['response_times']) > 100:
            performance_metrics['response_times'].pop(0)  # Keep last 100
            
        return status, contains, http_time
        
    except Exception as e:
        http_time = time.time() - http_start
        logger.error(f"HTTP check failed for {target}: {e}")
        log_metric('http_check_failure', 1, {'target': target, 'error': str(e)})
        performance_metrics['error_count'] += 1
        return 0, False, http_time

def main_loop():
    logger.info("Starting enhanced watchdog with logging and metrics...")
    logger.info(f"Configuration: TZ={TZ}, TARGETS={TARGETS}, CHECK_INTERVAL={CHECK_INTERVAL}s")
    logger.info(f"Enhanced logging: Application logs + Structured metrics enabled")
    
    while True:
        cycle_start = time.time()
        
        try:
            logger.info("Fetching world time...")
            fetched = fetch_world_time()
        except Exception as e:
            error_msg = f"Error fetching world time: {e}"
            logger.error(error_msg)
            send_alert("[Velaris] World time fetch failed", error_msg)
            performance_metrics['error_count'] += 1
            time.sleep(CHECK_INTERVAL)
            continue

        cycle_results = []
        
        for t in TARGETS:
            container_id = t.split(":")[0]
            logger.info(f"Checking target: {t}")
            target_start = time.time()
            
            try:
                local = get_local_time()
                drift = abs(int((local - fetched).total_seconds()))
                logger.info(f"Time drift for {container_id}: {drift} seconds")
                
                # Log time drift metric
                log_metric('time_drift_seconds', drift, {'target': t})
                
                update_homepage(t, fetched, local, container_id)
                status, contains, response_time = http_check(t)
                logger.info(f"HTTP check for {container_id}: status={status}, contains_expected={contains}, response_time={response_time:.3f}s")
                
                ok = (status == 200) and contains and (drift <= MAX_DRIFT)
                logger.info(f"Overall check result for {container_id}: {'PASS' if ok else 'FAIL'}")
                
                target_time = time.time() - target_start
                
                # Enhanced database logging with response time
                with db_conn() as conn:
                    with conn.cursor() as cur:
                        # Use enhanced schema column names
                        cur.execute("""
                            INSERT INTO checks (target, status, http_status, time_drift_seconds, 
                                              response_time_ms, fetched_time, local_time, created_at)
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                        """, (
                            t,  # Use full target instead of container_id
                            'PASS' if ok else 'FAIL',
                            status, 
                            drift, 
                            int(response_time * 1000),  # Convert to milliseconds
                            fetched, 
                            local, 
                            datetime.now()
                        ))
                        logger.info(f"Persisted enhanced check result for {container_id}")
                
                # Also log structured metrics to our metrics table (if exists)
                try:
                    with db_conn() as conn:
                        with conn.cursor() as cur:
                            status_label = "ok" if ok else "fail"
                            tags_json = f'{{"target": "{t}", "status": "{status_label}"}}'
                            cur.execute("""
                                INSERT INTO metrics (metric_name, metric_value, tags, timestamp)
                                VALUES (%s,%s,%s,%s)
                            """, (
                                'response_time_ms',
                                int(response_time * 1000),
                                tags_json,
                                datetime.now()
                            ))
                except Exception as metrics_error:
                    logger.debug(f"Metrics table not available (expected during migration): {metrics_error}")
                
                # Log comprehensive performance metrics
                log_metric('target_check_duration', target_time, {'target': t})
                log_metric('target_status', 1 if ok else 0, {'target': t, 'result': 'PASS' if ok else 'FAIL'})
                
                cycle_results.append(ok)
                performance_metrics['check_count'] += 1
                        
                if not ok:
                    msg = (
                        f"Target={t}\n"
                        f"HTTP={status}, contains='{EXPECT_TEXT}'? {contains}\n"
                        f"Drift={drift}s (max {MAX_DRIFT})\n"
                        f"Response time={response_time:.3f}s\n"
                        f"Fetched={fetched.isoformat()}, Local={local.isoformat()}\n"
                    )
                    logger.warning(f"Validation failed for {t}: {msg}")
                    send_alert(f"[Velaris] Validation failed for {t}", msg)
                    
            except Exception as e:
                error_msg = f"Error while checking {t}: {e}"
                logger.error(error_msg)
                send_alert(f"[Velaris] Error while checking {t}", error_msg)
                performance_metrics['error_count'] += 1
                cycle_results.append(False)
        
        # Log cycle-level metrics
        cycle_time = time.time() - cycle_start
        cycle_success_rate = (sum(cycle_results) / len(cycle_results)) * 100 if cycle_results else 0
        
        log_metric('cycle_duration', cycle_time)
        log_metric('cycle_success_rate', cycle_success_rate)
        
        logger.info(f"Enhanced check cycle completed in {cycle_time:.2f}s. Success rate: {cycle_success_rate:.1f}%. Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

def init_watchdog():
    """Initialize the enhanced watchdog system"""
    global logger, metrics_logger
    logger, metrics_logger = setup_logging()
    
    logger.info("Enhanced Velaris Watchdog Starting...")
    logger.info("Part 2: Logging & Monitoring Implementation")
    
    return logger, metrics_logger

if __name__ == "__main__":
    init_watchdog()
    main_loop()
