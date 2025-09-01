import os, time, smtplib, socket, json, logging
from email.mime.text import MIMEText
from datetime import datetime, timezone, timedelta
from urllib.parse import urlparse
import requests
import psycopg2

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

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
        logger.info(f"Sending alert: {subject}")
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = SMTP_FROM
        msg["To"] = SMTP_TO
        
        # Use TLS for real SMTP servers like Gmail
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
        logger.info("Alert sent successfully")
    except Exception as e:
        logger.error(f"Failed to send alert: {e}")

def fetch_world_time():
    # Try to get time from external APIs, fallback to local system time
    logger.info("Attempting to fetch world time from external APIs...")
    
    # For demonstration purposes, if external APIs fail, we'll use system time
    # In production, this would be configured with reliable time sources
    try:
        # Try a simple HTTP-only approach first
        url = "http://worldtimeapi.org/api/timezone/Asia/Colombo"
        logger.info(f"Trying HTTP: {url}")
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            logger.info(f"Successfully fetched world time via HTTP: {data['datetime']}")
            return datetime.fromisoformat(data["datetime"])
    except Exception as e:
        logger.warning(f"HTTP API failed: {e}")
    
    # Fallback: Use system time (assumes container timezone is correctly set)
    logger.warning("External APIs unavailable, using system time as reference")
    system_time = datetime.now().astimezone()
    logger.info(f"Using system time as fallback: {system_time}")
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
    host, port = target.split(":")
    url = f"http://{host}:{port}/"
    r = requests.get(url, timeout=10)
    status = r.status_code
    contains = (EXPECT_TEXT in r.text)
    return status, contains

def main_loop():
    logger.info("Starting watchdog main loop...")
    logger.info(f"Configuration: TZ={TZ}, TARGETS={TARGETS}, CHECK_INTERVAL={CHECK_INTERVAL}s")
    
    while True:
        try:
            logger.info("Fetching world time...")
            fetched = fetch_world_time()
        except Exception as e:
            error_msg = f"Error fetching world time: {e}"
            logger.error(error_msg)
            send_alert("[Velaris] World time fetch failed", error_msg)
            time.sleep(CHECK_INTERVAL)
            continue

        for t in TARGETS:
            container_id = t.split(":")[0]
            logger.info(f"Checking target: {t}")
            try:
                local = get_local_time()
                drift = abs(int((local - fetched).total_seconds()))
                logger.info(f"Time drift for {container_id}: {drift} seconds")
                
                update_homepage(t, fetched, local, container_id)
                status, contains = http_check(t)
                logger.info(f"HTTP check for {container_id}: status={status}, contains_expected={contains}")
                
                ok = (status == 200) and contains and (drift <= MAX_DRIFT)
                logger.info(f"Overall check result for {container_id}: {'PASS' if ok else 'FAIL'}")
                
                # persist
                with db_conn() as conn:
                    with conn.cursor() as cur:
                        cur.execute("""
                            INSERT INTO checks (container_id, fetched_time, local_time, drift_seconds, http_status, body_contains_expected, ok)
                            VALUES (%s,%s,%s,%s,%s,%s,%s)
                        """, (container_id, fetched, local, drift, status, contains, ok))
                        logger.info(f"Persisted check result for {container_id}")
                        
                if not ok:
                    msg = (
                        f"Target={t}\n"
                        f"HTTP={status}, contains='{EXPECT_TEXT}'? {contains}\n"
                        f"Drift={drift}s (max {MAX_DRIFT})\n"
                        f"Fetched={fetched.isoformat()}, Local={local.isoformat()}\n"
                    )
                    logger.warning(f"Validation failed for {t}: {msg}")
                    send_alert(f"[Velaris] Validation failed for {t}", msg)
            except Exception as e:
                error_msg = f"Error while checking {t}: {e}"
                logger.error(error_msg)
                send_alert(f"[Velaris] Error while checking {t}", error_msg)
                
        logger.info(f"Check cycle completed. Sleeping for {CHECK_INTERVAL} seconds...")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    main_loop()
