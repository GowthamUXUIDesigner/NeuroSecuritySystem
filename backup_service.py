import os
import time
import shutil
import json
from datetime import datetime

CONFIG_PATH = "config.json"
LOG_FILE = "neuro_logs.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

SOURCE = CONFIG["protected_folder"]
DEST = CONFIG["backup_folder"]
INTERVAL_SECONDS = 600  # 10 minutes


def log_event(level, event_type, message, details=None):
    entry = {
        "time": str(datetime.now()),
        "level": level,
        "event_type": event_type,
        "source": "backup_service",
        "message": message,
        "details": details or {}
    }
    print(f"[{entry['time']}] {level} - {event_type} - {message}")
    with open(LOG_FILE, "a", encoding="utf-8") as logf:
        logf.write(json.dumps(entry) + "\n")


def run_backup_loop():
    log_event(
        "INFO",
        "backup_startup",
        f"Backup service started. Source={SOURCE}, Dest={DEST}"
    )

    if not os.path.exists(DEST):
        os.makedirs(DEST, exist_ok=True)
        log_event("INFO", "backup_init", f"Created backup folder at {DEST}")

    while True:
        try:
            log_event("INFO", "backup_cycle_start", "Starting backup...")
            shutil.copytree(SOURCE, DEST, dirs_exist_ok=True)
            log_event("INFO", "backup_ok", "Backup completed successfully.")
        except Exception as e:
            log_event("WARNING", "backup_failed", f"Backup failed: {e}")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run_backup_loop()
