"""
Project Theia - Radiation Monitoring & Multi-Cloud Proxy
Creator: Alexandros - Ermis Tsourapas (SV1RVP)
License: GNU Affero General Public License v3.0 (AGPL-3.0)
"""

import csv
import io
import ipaddress
import json
import os
import queue
import shutil
import sqlite3
import subprocess
import sys
import threading
import time
import zipfile
from contextlib import closing
from datetime import datetime, timedelta, timezone

from flask import Flask, jsonify, render_template, request, send_from_directory
import requests

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DB_NAME = os.path.join(CONFIG_DIR, "radiation_data.db")
CSV_NAME = os.path.join(CONFIG_DIR, "radiation_log.csv")

VERSION = "2.3.8"
GITHUB_REPO = "https://github.com/SV1RVP/Theia"
GITHUB_API_COMMITS = "https://api.github.com/repos/SV1RVP/Theia/commits/main"


def load_config_file(filename, default_dict):
    """
    Load JSON config from config/ directory with fallback to default_dict.
    Safely enriches existing local files with documentation/schema updates without
    overwriting user configurations.
    """
    filepath = os.path.join(CONFIG_DIR, filename)
    if not os.path.exists(filepath):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(default_dict, f, indent=2, ensure_ascii=False)
        except Exception:
            pass
        return dict(default_dict)
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        merged = dict(default_dict)
        if isinstance(data, dict):
            needs_rewrite = False
            # Check if any documentation or default schema keys are missing
            for key in default_dict:
                if key not in data:
                    needs_rewrite = True
                    break
            if data.get("_instructions") != default_dict.get("_instructions") or data.get("_comment") != default_dict.get("_comment"):
                needs_rewrite = True

            # Preserve all user configuration settings from existing file
            for k, v in data.items():
                if not k.startswith("_"):
                    merged[k] = v

            # If the file on disk was missing documentation or schema keys, enrich it safely
            if needs_rewrite:
                try:
                    with open(filepath, "w", encoding="utf-8") as fw:
                        json.dump(merged, fw, indent=2, ensure_ascii=False)
                except Exception as write_err:
                    print(f"[!] Notice: could not rewrite enriched {filename}: {write_err}")

            return merged
        return merged
    except Exception as exc:
        print(f"[!] Warning reading {filename}: {exc}. Using default configuration.")
        return dict(default_dict)


# --- LOAD CONFIGURATIONS (FROM config/*.json) ---
APP_CONFIG = load_config_file(
    "app.json",
    {
        "_comment": "Project Theia - Project & Server Settings / Ρυθμίσεις Συστήματος",
        "_instructions": {
            "port": "Listening port (default 80, or 5000 / 8080) / Θύρα ακρόασης.",
            "retention_days": "Database retention limit in days (0 for unlimited) / Ημέρες διατήρησης στη βάση.",
            "ingest_auth_token": "Optional secret token for /log2.asp / Μυστικό token ασφαλείας.",
            "allowed_device_ips": "Allowed IP/CIDR list for LAN access / Επιτρεπόμενες IP/υποδίκτυα.",
            "max_upload_retries": "Upload retry attempts on connection error / Επαναπροσπάθειες αποστολής.",
            "upload_retry_delay_seconds": "Delay between upload retries in seconds / Χρόνος αναμονής επανάληψης.",
        },
        "port": 80,
        "retention_days": 30,
        "ingest_auth_token": "",
        "allowed_device_ips": [],
        "max_upload_retries": 3,
        "upload_retry_delay_seconds": 30,
    },
)

GMCMAP_CONFIG = load_config_file(
    "gmcmap.json",
    {
        "_comment": "GMCMap.com (GQ Electronics) Configuration / Ρυθμίσεις GMCMap.com",
        "_instructions": {
            "enabled": "true or false / true ή false για ενεργοποίηση",
            "user_account_id": "Your User Account ID from GMCMap.com / Το User Account ID σας από το GMCMap.com",
            "geiger_counter_id": "Your Geiger Counter ID from GMCMap.com / Το Geiger Counter ID σας από το GMCMap.com",
        },
        "enabled": False,
        "user_account_id": "",
        "geiger_counter_id": "",
    },
)

RADMON_CONFIG = load_config_file(
    "radmon.json",
    {
        "_comment": "Radmon.org Community Network Configuration / Ρυθμίσεις Radmon.org",
        "_instructions": {
            "enabled": "true or false / true ή false για ενεργοποίηση",
            "username": "Your Radmon.org username / Το όνομα χρήστη σας στο Radmon.org",
            "password": "Your Radmon.org data submission password / Ο κωδικός υποβολής δεδομένων σας στο Radmon.org",
        },
        "enabled": False,
        "username": "",
        "password": "",
    },
)

SAFECAST_CONFIG = load_config_file(
    "safecast.json",
    {
        "_comment": "Safecast.org Global Open Data Configuration / Ρυθμίσεις Safecast.org",
        "_instructions": {
            "enabled": "true or false / true ή false για ενεργοποίηση",
            "api_key": "Your Safecast API key / Το API key σας από το Safecast.org",
            "device_id": "Safecast device ID / Το αναγνωριστικό συσκευής (Device ID) στο Safecast",
            "latitude": "Sensor coordinates (e.g. 37.9838) / Γεωγραφικό πλάτος αισθητήρα",
            "longitude": "Sensor coordinates (e.g. 23.7275) / Γεωγραφικό μήκος αισθητήρα",
        },
        "enabled": False,
        "api_key": "",
        "device_id": "",
        "latitude": "",
        "longitude": "",
    },
)

OPENSENSEMAP_CONFIG = load_config_file(
    "opensensemap.json",
    {
        "_comment": "OpenSenseMap.org Citizen Science Configuration / Ρυθμίσεις OpenSenseMap.org",
        "_instructions": {
            "enabled": "true or false / true ή false για ενεργοποίηση",
            "sensebox_id": "Your senseBox ID / Το senseBox ID σας από το OpenSenseMap",
            "sensor_id": "Radiation sensor ID on OpenSenseMap / Το ID του αισθητήρα ακτινοβολίας στο OpenSenseMap",
        },
        "enabled": False,
        "sensebox_id": "",
        "sensor_id": "",
    },
)

# Optional Environment Overrides (Docker / CLI / test fixtures)
if "PORT" in os.environ:
    try:
        APP_CONFIG["port"] = int(os.environ["PORT"])
    except ValueError:
        pass
if "THEIA_RETENTION_DAYS" in os.environ:
    try:
        APP_CONFIG["retention_days"] = int(os.environ["THEIA_RETENTION_DAYS"])
    except ValueError:
        pass
if "THEIA_INGEST_TOKEN" in os.environ:
    APP_CONFIG["ingest_auth_token"] = os.environ["THEIA_INGEST_TOKEN"]
if "THEIA_ALLOWED_IPS" in os.environ:
    APP_CONFIG["allowed_device_ips"] = [
        v.strip() for v in os.environ["THEIA_ALLOWED_IPS"].split(",") if v.strip()
    ]

# Module-level variables for app runtime and backward-compatible test access
APP_PORT = APP_CONFIG.get("port", 80)
RETENTION_DAYS = APP_CONFIG.get("retention_days", 30)
INGEST_AUTH_TOKEN = APP_CONFIG.get("ingest_auth_token", "")
ALLOWED_DEVICE_IPS = APP_CONFIG.get("allowed_device_ips", [])
MAX_UPLOAD_RETRIES = max(1, int(APP_CONFIG.get("max_upload_retries", 3)))
UPLOAD_RETRY_DELAY_SECONDS = max(1, int(APP_CONFIG.get("upload_retry_delay_seconds", 30)))

GMCMAP_ENABLED = GMCMAP_CONFIG.get("enabled", False)
USER_ACCOUNT_ID = GMCMAP_CONFIG.get("user_account_id", "")
GEIGER_COUNTER_ID = GMCMAP_CONFIG.get("geiger_counter_id", "")

RADMON_ENABLED = RADMON_CONFIG.get("enabled", False)
RADMON_USERNAME = RADMON_CONFIG.get("username", "")
RADMON_PASSWORD = RADMON_CONFIG.get("password", "")

SAFECAST_ENABLED = SAFECAST_CONFIG.get("enabled", False)
SAFECAST_API_KEY = SAFECAST_CONFIG.get("api_key", "")
SAFECAST_DEVICE_ID = SAFECAST_CONFIG.get("device_id", "")
SAFECAST_LATITUDE = SAFECAST_CONFIG.get("latitude", "")
SAFECAST_LONGITUDE = SAFECAST_CONFIG.get("longitude", "")

OPENSENSEMAP_ENABLED = OPENSENSEMAP_CONFIG.get("enabled", False)
OPENSENSEMAP_SENSEBOX_ID = OPENSENSEMAP_CONFIG.get("sensebox_id", "")
OPENSENSEMAP_SENSOR_ID = OPENSENSEMAP_CONFIG.get("sensor_id", "")

upload_queue = queue.Queue()
upload_worker_started = False
upload_worker_lock = threading.Lock()


def gmcmap_enabled():
    return bool(GMCMAP_ENABLED and USER_ACCOUNT_ID and GEIGER_COUNTER_ID)


def radmon_enabled():
    return bool(RADMON_ENABLED and RADMON_USERNAME and RADMON_PASSWORD)


def safecast_enabled():
    return bool(SAFECAST_ENABLED and SAFECAST_API_KEY)


def opensensemap_enabled():
    return bool(OPENSENSEMAP_ENABLED and OPENSENSEMAP_SENSEBOX_ID and OPENSENSEMAP_SENSOR_ID)


def any_cloud_enabled():
    return (
        gmcmap_enabled()
        or radmon_enabled()
        or safecast_enabled()
        or opensensemap_enabled()
    )


def current_timestamp():
    now = datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S"), int(now.timestamp())


def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_storage():
    """Initialize SQLite storage and the CSV log file inside config/ directory."""
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # 1. Migrate or merge legacy database from root directory
    legacy_db = os.path.join(BASE_DIR, "radiation_data.db")
    if os.path.exists(legacy_db):
        try:
            if not os.path.exists(DB_NAME):
                shutil.move(legacy_db, DB_NAME)
                print(f"[+] Migrated legacy database from {legacy_db} to {DB_NAME}")
            else:
                # Merge unique records from legacy database into DB_NAME
                print(f"[*] Merging legacy database records from {legacy_db} into {DB_NAME}...")
                with closing(sqlite3.connect(DB_NAME)) as conn:
                    conn.execute("ATTACH DATABASE ? AS legacy", (legacy_db,))
                    tables = [r[0] for r in conn.execute("SELECT name FROM legacy.sqlite_master WHERE type='table'").fetchall()]
                    if "measurements" in tables:
                        conn.execute("""
                            INSERT OR IGNORE INTO measurements (
                                timestamp, recorded_at_unix, cpm, acpm, usvh, total_dose, uploaded_to_gmcmap
                            )
                            SELECT
                                timestamp,
                                CAST(strftime('%s', replace(timestamp, ' ', 'T')) AS INTEGER),
                                cpm, acpm, usvh, total_dose,
                                uploaded_to_gmcmap
                            FROM legacy.measurements
                            WHERE timestamp NOT IN (SELECT timestamp FROM measurements)
                        """)
                        conn.commit()
                    conn.execute("DETACH DATABASE legacy")
                bak_path = legacy_db + ".migrated.bak"
                if not os.path.exists(bak_path):
                    shutil.move(legacy_db, bak_path)
                print(f"[+] Successfully merged legacy database measurements into {DB_NAME}")
        except Exception as exc:
            print(f"[!] Warning processing legacy database: {exc}")

    # 2. Migrate or merge legacy CSV log from root directory
    legacy_csv = os.path.join(BASE_DIR, "radiation_log.csv")
    if os.path.exists(legacy_csv):
        try:
            if not os.path.exists(CSV_NAME):
                shutil.move(legacy_csv, CSV_NAME)
                print(f"[+] Migrated legacy CSV log from {legacy_csv} to {CSV_NAME}")
            else:
                with open(legacy_csv, "r", encoding="utf-8", errors="ignore") as f_in, \
                     open(CSV_NAME, "a", encoding="utf-8") as f_out:
                    lines = f_in.readlines()
                    data_lines = [line for line in lines if not line.lower().startswith("timestamp")]
                    f_out.writelines(data_lines)
                bak_csv = legacy_csv + ".migrated.bak"
                if not os.path.exists(bak_csv):
                    shutil.move(legacy_csv, bak_csv)
                print(f"[+] Appended legacy CSV measurements into {CSV_NAME}")
        except Exception as exc:
            print(f"[!] Warning processing legacy CSV log: {exc}")

    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS measurements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                recorded_at_unix INTEGER,
                cpm INTEGER,
                acpm REAL,
                usvh REAL,
                total_dose REAL,
                uploaded_to_gmcmap INTEGER DEFAULT 0
            )
            """
        )

        columns = {
            row["name"] for row in cursor.execute("PRAGMA table_info(measurements)").fetchall()
        }
        if "recorded_at_unix" not in columns:
            cursor.execute("ALTER TABLE measurements ADD COLUMN recorded_at_unix INTEGER")

        # Guarantee all records have valid recorded_at_unix
        cursor.execute(
            """
            UPDATE measurements
            SET recorded_at_unix = CAST(strftime('%s', replace(timestamp, ' ', 'T')) AS INTEGER)
            WHERE (recorded_at_unix IS NULL OR recorded_at_unix = 0) AND timestamp IS NOT NULL
            """
        )

        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_measurements_recorded_at_unix ON measurements(recorded_at_unix)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_measurements_uploaded_to_gmcmap ON measurements(uploaded_to_gmcmap)"
        )
        conn.commit()

    if not os.path.exists(CSV_NAME):
        with open(CSV_NAME, mode="w", newline="", encoding="utf-8") as file_obj:
            writer = csv.writer(file_obj)
            writer.writerow(
                ["Timestamp", "CPM", "ACPM", "uSv/h", "Total Dose (uSv)", "Uploaded"]
            )

    clear_old_measurements()


def clear_old_measurements():
    if RETENTION_DAYS <= 0:
        return

    cutoff_unix = int((datetime.now() - timedelta(days=RETENTION_DAYS)).timestamp())
    with closing(get_db_connection()) as conn:
        conn.execute("DELETE FROM measurements WHERE recorded_at_unix > 0 AND recorded_at_unix < ?", (cutoff_unix,))
        conn.commit()


def client_ip_is_allowed(remote_addr):
    if not remote_addr:
        return False

    try:
        remote_ip = ipaddress.ip_address(remote_addr)
    except ValueError:
        return False

    if ALLOWED_DEVICE_IPS:
        for candidate in ALLOWED_DEVICE_IPS:
            try:
                network = ipaddress.ip_network(candidate, strict=False)
                if remote_ip in network:
                    return True
            except ValueError:
                try:
                    if remote_ip == ipaddress.ip_address(candidate):
                        return True
                except ValueError:
                    continue
        return False

    return remote_ip.is_private or remote_ip.is_loopback


def request_is_authorized(req):
    if not client_ip_is_allowed(req.remote_addr):
        return False

    if not INGEST_AUTH_TOKEN:
        return True

    token = (
        req.headers.get("X-Theia-Token")
        or req.headers.get("X-Geiger-Token")
        or req.args.get("token")
    )
    return token == INGEST_AUTH_TOKEN


def write_csv_row(timestamp, cpm, acpm, usvh, dose, upload_state):
    try:
        with open(CSV_NAME, mode="a", newline="", encoding="utf-8") as file_obj:
            writer = csv.writer(file_obj)
            writer.writerow([timestamp, cpm, acpm, usvh, dose, upload_state])
    except Exception as exc:
        print(f"CSV Error: {exc}")


def save_measurement(cpm, acpm, usvh, dose):
    timestamp, recorded_at_unix = current_timestamp()
    with closing(get_db_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO measurements (
                timestamp, recorded_at_unix, cpm, acpm, usvh, total_dose, uploaded_to_gmcmap
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (timestamp, recorded_at_unix, cpm, acpm, usvh, dose, 0),
        )
        conn.commit()
        measurement_id = cursor.lastrowid

    upload_state = "QUEUED" if any_cloud_enabled() else "DISABLED"
    write_csv_row(timestamp, cpm, acpm, usvh, dose, upload_state)
    return measurement_id, timestamp


# --- CLOUD FORWARDERS ---

def build_gmcmap_url(cpm, usvh):
    return (
        f"http://www.gmcmap.com/log2.asp?AID={USER_ACCOUNT_ID}"
        f"&GID={GEIGER_COUNTER_ID}&CPM={cpm}&uSV={usvh}"
    )


def upload_to_gmcmap(cpm, usvh, timestamp):
    headers = {
        "User-Agent": "GMC-500+ WiFi V2.45",
        "Host": "www.gmcmap.com",
        "Connection": "close",
    }
    try:
        response = requests.get(build_gmcmap_url(cpm, usvh), headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"[{timestamp}] [GMCMap.com] -> Successful upload! Response: {response.text.strip()}")
            return True
        print(f"[{timestamp}] [GMCMap.com] -> API Error (HTTP {response.status_code})")
        return False
    except Exception as exc:
        print(f"[{timestamp}] [GMCMap.com] -> Connection failed: {exc}")
        return False


def upload_to_radmon(cpm, timestamp):
    url = (
        f"https://radmon.org/radmon.php?function=submit"
        f"&user={RADMON_USERNAME}&password={RADMON_PASSWORD}&unit=CPM&value={cpm}"
    )
    headers = {"User-Agent": f"Project-Theia/{VERSION}"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        clean_resp = response.text.replace("<br>", " ").replace("<br/>", " ").replace("<br />", " ").strip()
        if response.status_code == 200 and "OK" in response.text.upper():
            if "COULD NOT CREATE USER FOLDER" in response.text.upper():
                print(f"[{timestamp}] [Radmon.org] -> Upload accepted with server notice: '{clean_resp}' (Check station setup on radmon.org)")
            else:
                print(f"[{timestamp}] [Radmon.org] -> Successful upload! Response: {clean_resp}")
            return True
        print(f"[{timestamp}] [Radmon.org] -> API Error (HTTP {response.status_code}): {clean_resp}")
        return False
    except Exception as exc:
        print(f"[{timestamp}] [Radmon.org] -> Connection failed: {exc}")
        return False


def upload_to_safecast(cpm, timestamp):
    url = "https://api.safecast.org/measurements.json"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"Project-Theia/{VERSION}",
    }
    params = {"api_key": SAFECAST_API_KEY}
    measurement = {
        "value": cpm,
        "unit": "cpm",
        "captured_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    if SAFECAST_LATITUDE and SAFECAST_LONGITUDE:
        try:
            measurement["latitude"] = float(SAFECAST_LATITUDE)
            measurement["longitude"] = float(SAFECAST_LONGITUDE)
        except ValueError:
            pass
    if SAFECAST_DEVICE_ID:
        try:
            measurement["device_id"] = int(SAFECAST_DEVICE_ID)
        except ValueError:
            pass

    payload = {"measurement": measurement}
    try:
        response = requests.post(url, params=params, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            print(f"[{timestamp}] [Safecast.org] -> Successful upload! (HTTP {response.status_code})")
            return True
        if response.status_code == 401:
            print(f"[{timestamp}] [Safecast.org] -> Authentication Error (HTTP 401): Invalid API Key. Please verify 'api_key' in config/safecast.json (https://api.safecast.org)")
            return False
        print(f"[{timestamp}] [Safecast.org] -> API Error (HTTP {response.status_code}): {response.text.strip()}")
        return False
    except Exception as exc:
        print(f"[{timestamp}] [Safecast.org] -> Connection failed: {exc}")
        return False


def upload_to_opensensemap(cpm, timestamp):
    url = f"https://api.opensensemap.org/boxes/{OPENSENSEMAP_SENSEBOX_ID}/{OPENSENSEMAP_SENSOR_ID}"
    headers = {
        "Content-Type": "application/json",
        "User-Agent": f"Project-Theia/{VERSION}",
    }
    payload = {
        "value": str(cpm),
        "createdAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        if response.status_code in (200, 201):
            print(f"[{timestamp}] [OpenSenseMap.org] -> Successful upload! (HTTP {response.status_code})")
            return True
        print(f"[{timestamp}] [OpenSenseMap.org] -> API Error (HTTP {response.status_code}): {response.text.strip()}")
        return False
    except Exception as exc:
        print(f"[{timestamp}] [OpenSenseMap.org] -> Connection failed: {exc}")
        return False


def mark_upload_complete(measurement_id):
    with closing(get_db_connection()) as conn:
        conn.execute(
            "UPDATE measurements SET uploaded_to_gmcmap = 1 WHERE id = ?",
            (measurement_id,),
        )
        conn.commit()


def enqueue_cloud_uploads(measurement_id, cpm, usvh, timestamp):
    if gmcmap_enabled():
        upload_queue.put({
            "target": "gmcmap",
            "measurement_id": measurement_id,
            "cpm": cpm,
            "usvh": usvh,
            "timestamp": timestamp,
            "attempt": 1,
            "ready_at": time.time(),
        })

    if radmon_enabled():
        upload_queue.put({
            "target": "radmon",
            "measurement_id": measurement_id,
            "cpm": cpm,
            "usvh": usvh,
            "timestamp": timestamp,
            "attempt": 1,
            "ready_at": time.time(),
        })

    if safecast_enabled():
        upload_queue.put({
            "target": "safecast",
            "measurement_id": measurement_id,
            "cpm": cpm,
            "usvh": usvh,
            "timestamp": timestamp,
            "attempt": 1,
            "ready_at": time.time(),
        })

    if opensensemap_enabled():
        upload_queue.put({
            "target": "opensensemap",
            "measurement_id": measurement_id,
            "cpm": cpm,
            "usvh": usvh,
            "timestamp": timestamp,
            "attempt": 1,
            "ready_at": time.time(),
        })


# Backward-compatible alias
enqueue_gmcmap_upload = enqueue_cloud_uploads


def upload_worker():
    while True:
        job = upload_queue.get()
        try:
            wait_seconds = job["ready_at"] - time.time()
            if wait_seconds > 0:
                time.sleep(wait_seconds)

            target = job.get("target", "gmcmap")
            success = False

            if target == "gmcmap":
                success = upload_to_gmcmap(job["cpm"], job["usvh"], job["timestamp"])
                if success:
                    mark_upload_complete(job["measurement_id"])
            elif target == "radmon":
                success = upload_to_radmon(job["cpm"], job["timestamp"])
            elif target == "safecast":
                success = upload_to_safecast(job["cpm"], job["timestamp"])
            elif target == "opensensemap":
                success = upload_to_opensensemap(job["cpm"], job["timestamp"])

            if success:
                continue

            if job["attempt"] < MAX_UPLOAD_RETRIES:
                job["attempt"] += 1
                job["ready_at"] = time.time() + UPLOAD_RETRY_DELAY_SECONDS
                upload_queue.put(job)
                print(
                    f"[{job['timestamp']}] [{target}] -> Re-queued upload attempt "
                    f"{job['attempt']}/{MAX_UPLOAD_RETRIES}"
                )
        finally:
            upload_queue.task_done()


def ensure_upload_worker():
    global upload_worker_started

    with upload_worker_lock:
        if upload_worker_started:
            return

        worker = threading.Thread(target=upload_worker, daemon=True)
        worker.start()
        upload_worker_started = True


@app.route("/log2.asp", methods=["GET"])
def log_endpoint():
    if not request_is_authorized(request):
        return "Forbidden", 403

    cpm_param = request.args.get("CPM")
    acpm_param = request.args.get("ACPM", 0)
    usv_param = request.args.get("uSV")
    dose_param = request.args.get("dose", 0)

    if cpm_param is None:
        return "Missing CPM", 400

    try:
        cpm = int(cpm_param)
        acpm = float(acpm_param)
        usvh = float(usv_param) if usv_param else round(cpm / 151.4, 4)
        dose = float(dose_param)

        print(
            f"\n[+] Data Received: CPM={cpm} | ACPM={acpm} | "
            f"uSv/h={usvh} | TotalDose={dose} uSv"
        )

        measurement_id, timestamp = save_measurement(cpm, acpm, usvh, dose)
        enqueue_cloud_uploads(measurement_id, cpm, usvh, timestamp)
        return "OK", 200
    except ValueError as exc:
        return f"Bad Request: {exc}", 400


@app.route("/")
def index():
    return render_template(
        "index.html",
        cloud_targets={
            "gmcmap": gmcmap_enabled(),
            "radmon": radmon_enabled(),
            "safecast": safecast_enabled(),
            "opensense": opensensemap_enabled(),
        },
    )


@app.route("/logo/<path:filename>")
def serve_logo(filename):
    return send_from_directory(os.path.join(BASE_DIR, "logo"), filename)


@app.route("/api/data")
def api_data():
    try:
        clear_old_measurements()

        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT timestamp, cpm, acpm, usvh, total_dose
                FROM measurements
                ORDER BY recorded_at_unix DESC, id DESC
                LIMIT 1
                """
            )
            latest_row = cursor.fetchone()
            latest = {}
            if latest_row:
                latest = {
                    "timestamp": latest_row["timestamp"],
                    "cpm": latest_row["cpm"],
                    "acpm": latest_row["acpm"],
                    "usvh": latest_row["usvh"],
                    "total_dose": latest_row["total_dose"],
                }

            now = datetime.now()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_start_unix = int(today_start.timestamp())
            today_end = today_start + timedelta(days=1) - timedelta(microseconds=1)

            # Query rolling 24 hours of measurements so all views (1H, 6H, 12H, 24H) have full data
            rolling_24h_unix = int((now - timedelta(hours=24)).timestamp())
            rolling_24h_str = (now - timedelta(hours=24)).strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute(
                """
                SELECT timestamp, recorded_at_unix, cpm, usvh
                FROM measurements
                WHERE (recorded_at_unix >= ? OR (recorded_at_unix IS NULL AND timestamp >= ?))
                ORDER BY COALESCE(recorded_at_unix, 0) ASC, timestamp ASC, id ASC
                """,
                (rolling_24h_unix, rolling_24h_str),
            )
            history_rows = cursor.fetchall()

        # Calculate 24h accumulated dose over the rolling 24h history
        dose_24h = 0.0
        for i in range(1, len(history_rows)):
            t_prev = history_rows[i - 1]["recorded_at_unix"]
            t_curr = history_rows[i]["recorded_at_unix"]
            if t_prev is not None and t_curr is not None:
                dt_hours = (t_curr - t_prev) / 3600.0
                if 0 < dt_hours <= 2.0:
                    avg_rate = (history_rows[i - 1]["usvh"] + history_rows[i]["usvh"]) / 2.0
                    dose_24h += avg_rate * dt_hours
        if len(history_rows) == 1 and history_rows[0]["usvh"] is not None:
            dose_24h = history_rows[0]["usvh"] / 60.0

        # Also calculate today's calendar-day accumulated dose strictly from 00:00:00 to now
        today_rows = [
            r for r in history_rows
            if (r["recorded_at_unix"] is not None and r["recorded_at_unix"] >= today_start_unix)
            or (r["recorded_at_unix"] is None and r["timestamp"] >= today_start.strftime("%Y-%m-%d 00:00:00"))
        ]
        dose_today = 0.0
        for i in range(1, len(today_rows)):
            t_prev = today_rows[i - 1]["recorded_at_unix"]
            t_curr = today_rows[i]["recorded_at_unix"]
            if t_prev is not None and t_curr is not None:
                dt_hours = (t_curr - t_prev) / 3600.0
                if 0 < dt_hours <= 2.0:
                    avg_rate = (today_rows[i - 1]["usvh"] + today_rows[i]["usvh"]) / 2.0
                    dose_today += avg_rate * dt_hours
        if len(today_rows) == 1 and today_rows[0]["usvh"] is not None:
            dose_today = today_rows[0]["usvh"] / 60.0

        history = [
            {
                "timestamp": row["timestamp"],
                "recorded_at_unix": row["recorded_at_unix"],
                "cpm": row["cpm"],
                "usvh": row["usvh"],
            }
            for row in history_rows
        ]

        return jsonify({
            "status": "success",
            "latest": latest,
            "dose_24h": round(dose_24h, 4),
            "dose_today": round(dose_today, 4),
            "today_start": today_start.strftime("%Y-%m-%d 00:00:00"),
            "today_end": today_end.strftime("%Y-%m-%d 23:59:59"),
            "history": history,
            "cloud_targets": {
                "gmcmap": gmcmap_enabled(),
                "radmon": radmon_enabled(),
                "safecast": safecast_enabled(),
                "opensense": opensensemap_enabled(),
            },
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/system/version")
def system_version():
    return jsonify({
        "status": "success",
        "version": VERSION,
        "github_repo": GITHUB_REPO,
    })


@app.route("/api/system/check-update")
def check_update():
    try:
        headers = {"User-Agent": f"Project-Theia/{VERSION}"}
        resp = requests.get(GITHUB_API_COMMITS, headers=headers, timeout=5)
        if resp.status_code == 200:
            commit_data = resp.json()
            latest_sha = commit_data.get("sha", "")[:7]
            commit_msg = commit_data.get("commit", {}).get("message", "").split("\n")[0]
            commit_date = commit_data.get("commit", {}).get("author", {}).get("date", "")
            return jsonify({
                "status": "success",
                "current_version": VERSION,
                "latest_commit": latest_sha,
                "commit_message": commit_msg,
                "commit_date": commit_date,
                "github_url": GITHUB_REPO,
            })
        return jsonify({
            "status": "unavailable",
            "current_version": VERSION,
            "message": f"GitHub returned HTTP {resp.status_code}",
            "github_url": GITHUB_REPO,
        })
    except Exception as exc:
        return jsonify({
            "status": "error",
            "current_version": VERSION,
            "message": str(exc),
            "github_url": GITHUB_REPO,
        })


def perform_system_update():
    """
    Downloads latest repository archive from GitHub and updates system files,
    strictly EXCLUDING the config/ directory and local user data.
    """
    archive_url = f"{GITHUB_REPO}/archive/refs/heads/main.zip"
    headers = {"User-Agent": f"Project-Theia/{VERSION}"}
    resp = requests.get(archive_url, headers=headers, timeout=30)
    if resp.status_code != 200:
        raise RuntimeError(f"Failed to download update from GitHub (HTTP {resp.status_code})")

    with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
        namelist = zf.namelist()
        if not namelist:
            raise RuntimeError("Downloaded archive is empty")
        root_prefix = namelist[0].split("/")[0] + "/"

        updated_files = 0
        for member in zf.infolist():
            rel_path = member.filename
            if rel_path.startswith(root_prefix):
                rel_path = rel_path[len(root_prefix):]
            if not rel_path:
                continue

            rel_parts = [p for p in rel_path.replace("\\", "/").split("/") if p]
            if not rel_parts:
                continue

            first_segment = rel_parts[0].lower()

            # Strictly ignore internal / virtualenv / git directories
            if first_segment in (".git", ".venv", "__pycache__"):
                continue

            # Special safe handling for config/ directory
            if first_segment == "config":
                file_name = rel_parts[-1].lower()

                # STRICTLY PROTECT databases, logs, wal files, and backups
                if file_name.endswith((".db", ".db-wal", ".db-shm", ".db-journal", ".csv", ".bak", ".log")):
                    continue

                target_path = os.path.join(BASE_DIR, *rel_parts)

                # Smart non-destructive merge for JSON config files
                if file_name.endswith(".json"):
                    try:
                        with zf.open(member) as src:
                            incoming_content = src.read().decode("utf-8")
                            incoming_json = json.loads(incoming_content)

                        if os.path.exists(target_path):
                            try:
                                with open(target_path, "r", encoding="utf-8") as f:
                                    local_json = json.load(f)
                            except Exception:
                                local_json = {}

                            # Start with incoming JSON template (has latest comments, instructions & defaults)
                            merged_config = dict(incoming_json) if isinstance(incoming_json, dict) else {}
                            # Preserve all local user settings & credentials
                            if isinstance(local_json, dict):
                                for k, v in local_json.items():
                                    if not k.startswith("_"):
                                        merged_config[k] = v

                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with open(target_path, "w", encoding="utf-8") as f:
                                json.dump(merged_config, f, indent=2, ensure_ascii=False)
                            updated_files += 1
                            continue
                        else:
                            # New config file from repository - write directly
                            os.makedirs(os.path.dirname(target_path), exist_ok=True)
                            with open(target_path, "w", encoding="utf-8") as f:
                                json.dump(incoming_json, f, indent=2, ensure_ascii=False)
                            updated_files += 1
                            continue
                    except Exception as exc:
                        print(f"[!] Warning merging config file {rel_path}: {exc}")
                        continue

                # Safely update documentation in config/ (e.g. config/README.md)
                if file_name.endswith(".md"):
                    os.makedirs(os.path.dirname(target_path), exist_ok=True)
                    with zf.open(member) as src, open(target_path, "wb") as dst:
                        shutil.copyfileobj(src, dst)
                    updated_files += 1
                    continue

                # Ignore any other unexpected files in config/
                continue

            target_path = os.path.join(BASE_DIR, *rel_parts)

            if member.is_dir():
                os.makedirs(target_path, exist_ok=True)
            else:
                os.makedirs(os.path.dirname(target_path), exist_ok=True)
                with zf.open(member) as src, open(target_path, "wb") as dst:
                    shutil.copyfileobj(src, dst)
                updated_files += 1

    # Upgrade dependencies if .venv exists
    venv_pip = os.path.join(BASE_DIR, ".venv", "Scripts", "pip.exe")
    if not os.path.exists(venv_pip):
        venv_pip = os.path.join(BASE_DIR, ".venv", "bin", "pip")

    req_file = os.path.join(BASE_DIR, "requirements.txt")
    if os.path.exists(venv_pip) and os.path.exists(req_file):
        try:
            subprocess.run([venv_pip, "install", "-r", req_file, "--upgrade"], check=False, timeout=60)
        except Exception as exc:
            print(f"[!] Warning updating pip requirements: {exc}")

    return updated_files


def schedule_service_restart(delay_seconds=1.5):
    """
    Schedules an asynchronous restart of the service/process after sending response.
    """
    def _restart():
        time.sleep(delay_seconds)
        print("[*] Initiating service restart...")

        # 1. Linux systemd check
        if os.name != "nt":
            try:
                res = subprocess.run(["systemctl", "is-active", "--quiet", "theia"], check=False)
                if res.returncode == 0:
                    subprocess.run(["sudo", "systemctl", "restart", "theia"], check=False)
                    return
            except Exception:
                pass

        # 2. Windows / Direct process re-execution
        try:
            # Self-healing for Windows virtual environments if python path changed
            venv_cfg = os.path.join(BASE_DIR, ".venv", "pyvenv.cfg")
            if os.path.isfile(venv_cfg):
                try:
                    with open(venv_cfg, "r", encoding="utf-8") as f:
                        cfg_lines = f.readlines()
                    cfg_changed = False
                    new_lines = []
                    for line in cfg_lines:
                        if line.strip().startswith("home ="):
                            home_dir = line.split("=", 1)[1].strip()
                            if not os.path.isdir(home_dir):
                                real_py = shutil.which("python")
                                if real_py:
                                    new_home = os.path.dirname(real_py)
                                    line = f"home = {new_home}\n"
                                    cfg_changed = True
                        new_lines.append(line)
                    if cfg_changed:
                        with open(venv_cfg, "w", encoding="utf-8") as f:
                            f.writelines(new_lines)
                        print("[*] Automatically healed .venv pyvenv.cfg home path.")
                except Exception as cfg_err:
                    print(f"[!] Warning reading/healing pyvenv.cfg: {cfg_err}")

            # Identify a working python executable
            py_bin = sys.executable
            try:
                test_py = subprocess.run([py_bin, "-c", "import sys"], capture_output=True, timeout=5)
                if test_py.returncode != 0:
                    py_bin = None
            except Exception:
                py_bin = None

            if not py_bin:
                candidates = [
                    os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe"),
                    os.path.join(BASE_DIR, ".venv", "bin", "python"),
                    shutil.which("python"),
                    shutil.which("python3")
                ]
                for c in candidates:
                    if c and os.path.isfile(c):
                        try:
                            test_c = subprocess.run([c, "-c", "import sys"], capture_output=True, timeout=5)
                            if test_c.returncode == 0:
                                py_bin = c
                                break
                        except Exception:
                            continue

            if not py_bin:
                py_bin = "python"

            main_script = os.path.join(BASE_DIR, "main.py")
            if os.name == "nt":
                CREATE_NEW_CONSOLE = 0x00000010
                bat_script = os.path.join(BASE_DIR, "start-windows.bat")
                if os.path.exists(bat_script):
                    subprocess.Popen(
                        ["cmd.exe", "/c", bat_script],
                        creationflags=CREATE_NEW_CONSOLE,
                        cwd=BASE_DIR
                    )
                else:
                    subprocess.Popen(
                        [py_bin, main_script],
                        creationflags=CREATE_NEW_CONSOLE,
                        cwd=BASE_DIR
                    )
            else:
                subprocess.Popen(
                    [py_bin, main_script],
                    close_fds=True,
                    cwd=BASE_DIR
                )
        except Exception as exc:
            print(f"[!] Error spawning new process during restart: {exc}")
        finally:
            os._exit(0)

    t = threading.Thread(target=_restart, daemon=True)
    t.start()


@app.route("/api/system/perform-update", methods=["POST"])
def api_perform_update():
    try:
        updated_count = perform_system_update()
        schedule_service_restart(delay_seconds=1.5)
        return jsonify({
            "status": "success",
            "message": f"Επιτυχής ενημέρωση {updated_count} αρχείων συστήματος! Επανεκκίνηση σε εξέλιξη...",
            "updated_files": updated_count,
            "version": VERSION
        })
    except Exception as exc:
        print(f"[!] Update error: {exc}")
        return jsonify({
            "status": "error",
            "message": str(exc)
        }), 500


@app.route("/api/system/db-info", methods=["GET"])
def api_system_db_info():
    try:
        total_rows = 0
        min_ts = None
        max_ts = None
        db_exists = os.path.exists(DB_NAME)
        db_size = os.path.getsize(DB_NAME) if db_exists else 0

        if db_exists:
            with closing(get_db_connection()) as conn:
                row = conn.execute("SELECT COUNT(*), MIN(timestamp), MAX(timestamp) FROM measurements").fetchone()
                if row:
                    total_rows, min_ts, max_ts = row[0], row[1], row[2]

        legacy_db = os.path.join(BASE_DIR, "radiation_data.db")
        legacy_exists = os.path.exists(legacy_db)
        legacy_count = 0
        if legacy_exists:
            try:
                with closing(sqlite3.connect(legacy_db)) as lconn:
                    legacy_count = lconn.execute("SELECT COUNT(*) FROM measurements").fetchone()[0]
            except Exception:
                pass

        return jsonify({
            "status": "success",
            "db_path": DB_NAME,
            "db_exists": db_exists,
            "db_size_bytes": db_size,
            "total_records": total_rows,
            "oldest_timestamp": min_ts,
            "newest_timestamp": max_ts,
            "legacy_db_path": legacy_db,
            "legacy_db_exists": legacy_exists,
            "legacy_records": legacy_count
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


@app.route("/api/system/import-measurements", methods=["POST"])
def api_system_import_measurements():
    try:
        payload = request.get_json(silent=True)
        if not payload or not isinstance(payload.get("measurements"), list):
            return jsonify({"status": "error", "message": "Expected JSON with 'measurements' list"}), 400

        measurements = payload["measurements"]
        imported = 0
        with closing(get_db_connection()) as conn:
            cursor = conn.cursor()
            for m in measurements:
                ts = m.get("timestamp")
                if not ts:
                    continue
                cpm = int(m.get("cpm", 0))
                acpm = float(m.get("acpm", 0.0)) if m.get("acpm") is not None else None
                usvh = float(m.get("usvh", 0.0))
                total_dose = float(m.get("total_dose", 0.0)) if m.get("total_dose") is not None else None
                rec_unix = m.get("recorded_at_unix")
                if not rec_unix:
                    try:
                        rec_unix = int(datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").timestamp())
                    except Exception:
                        rec_unix = 0

                cursor.execute(
                    """
                    INSERT OR IGNORE INTO measurements (
                        timestamp, recorded_at_unix, cpm, acpm, usvh, total_dose, uploaded_to_gmcmap
                    ) VALUES (?, ?, ?, ?, ?, ?, 1)
                    """,
                    (ts, rec_unix, cpm, acpm, usvh, total_dose)
                )
                if cursor.rowcount > 0:
                    imported += 1
            conn.commit()

        return jsonify({
            "status": "success",
            "imported_count": imported,
            "total_submitted": len(measurements)
        })
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


init_storage()
ensure_upload_worker()


if __name__ == "__main__":
    print("=" * 60)
    print(" Project Theia - Radiation Monitoring & Multi-Cloud Proxy")
    print(f" Database Path: {DB_NAME}")
    print(f" CSV Log Path:  {CSV_NAME}")
    print(f" Port:          {APP_PORT}")
    print(f" GMCMap.com:    {'ENABLED' if gmcmap_enabled() else 'DISABLED'}")
    print(f" Radmon.org:    {'ENABLED' if radmon_enabled() else 'DISABLED'}")
    print(f" Safecast.org:  {'ENABLED' if safecast_enabled() else 'DISABLED'}")
    print(f" OpenSenseMap:  {'ENABLED' if opensensemap_enabled() else 'DISABLED'}")
    print(f" Retention:     {RETENTION_DAYS} day(s)")
    print("=" * 60)
    app.run(host="0.0.0.0", port=APP_PORT)
