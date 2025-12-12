import os
import time
import hashlib
import json
from datetime import datetime

# Try to import ML model – optional enhancement
try:
    from sklearn.ensemble import IsolationForest
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

CONFIG_PATH = "config.json"
LOG_FILE = "neuro_logs.json"
STATE_FILE = "file_state.json"

with open(CONFIG_PATH, "r") as f:
    CONFIG = json.load(f)

PROTECTED_FOLDER = CONFIG["protected_folder"]

SUSPICIOUS_EXTENSIONS = [".exe", ".dll", ".js", ".vbs", ".bat", ".ps1", ".jar"]

# If ML is available, set up a basic model
if ML_AVAILABLE:
    model = IsolationForest(contamination=0.05, random_state=42)
    ml_history = []


def log_event(level, event_type, message, source="neuro_protect", details=None):
    entry = {
        "time": str(datetime.now()),
        "level": level,
        "event_type": event_type,
        "source": source,
        "message": message,
        "details": details or {}
    }
    print(f"[{entry['time']}] {level} - {event_type} - {message}")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write(json.dumps(entry) + "\n")


def hash_file(path):
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            # Simple: read whole file. For huge files you’d stream in chunks.
            h.update(f.read())
        return h.hexdigest()
    except Exception as e:
        log_event("WARNING", "hash_error", f"Error hashing {path}: {e}")
        return None


def load_previous_state():
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def scan_directory(directory):
    """
    Build a current snapshot: {filepath: {size, mtime, hash, ext}}
    """
    snapshot = {}
    for root, dirs, files in os.walk(directory):
        for f in files:
            full_path = os.path.join(root, f)
            try:
                size = os.path.getsize(full_path)
                mtime = os.path.getmtime(full_path)
                ext = os.path.splitext(f)[1].lower()
                file_hash = hash_file(full_path)
            except OSError:
                continue

            snapshot[full_path] = {
                "size": size,
                "mtime": mtime,
                "hash": file_hash,
                "ext": ext,
            }
    return snapshot


def detect_changes(prev_state, curr_state):
    """
    Compare previous and current snapshots and detect changes.
    """
    prev_files = set(prev_state.keys())
    curr_files = set(curr_state.keys())

    new_files = curr_files - prev_files
    deleted_files = prev_files - curr_files
    potentially_modified = prev_files & curr_files

    modified_files = []

    for path in potentially_modified:
        prev = prev_state[path]
        curr = curr_state[path]
        if prev["hash"] != curr["hash"] or prev["size"] != curr["size"]:
            modified_files.append(path)

    return new_files, deleted_files, modified_files


def analyze_security(new_files, deleted_files, modified_files, curr_state):
    """
    Decide what kind of 'attack' pattern we might be seeing.
    Very simple heuristics, but enough for learning and awareness.
    """
    total_changes = len(new_files) + len(deleted_files) + len(modified_files)

    # Heuristic: many files modified at once → possible ransomware
    if len(modified_files) > 20:
        log_event(
            "ALERT",
            "possible_ransomware",
            f"Detected {len(modified_files)} modified files in one scan. This may indicate ransomware.",
            details={"modified_count": len(modified_files)}
        )

    # Suspicious executable/script dropped
    for path in new_files:
        ext = curr_state[path]["ext"]
        if ext in SUSPICIOUS_EXTENSIONS:
            log_event(
                "ALERT",
                "suspicious_executable",
                f"New suspicious file created: {path}",
                details={"file": path, "extension": ext}
            )

    # General info for transparency
    if total_changes > 0:
        log_event(
            "INFO",
            "scan_summary",
            f"Scan changes: new={len(new_files)}, deleted={len(deleted_files)}, modified={len(modified_files)}",
            details={
                "new_files": list(new_files),
                "deleted_files": list(deleted_files),
                "modified_files": modified_files
            }
        )
    else:
        log_event("INFO", "scan_summary", "No file changes detected in this scan.")


def ml_analyze_if_available(curr_state):
    """
    Optional ML anomaly detection over file sizes.
    """
    if not ML_AVAILABLE:
        return

    sizes = [[info["size"]] for info in curr_state.values()]
    if len(sizes) < 20:
        return  # Not enough data

    try:
        global ml_history
        ml_history.extend(sizes)
        model.fit(ml_history)
        preds = model.predict(sizes)
        anomaly_count = sum(1 for p in preds if p == -1)
        if anomaly_count > 0:
            log_event(
                "WARNING",
                "ml_anomaly",
                f"ML model flagged {anomaly_count} anomalous file size patterns.",
                details={"anomalies": anomaly_count}
            )
    except Exception as e:
        log_event("WARNING", "ml_error", f"ML analysis error: {e}")


def protect_loop():
    if not os.path.exists(PROTECTED_FOLDER):
        os.makedirs(PROTECTED_FOLDER, exist_ok=True)
        log_event("INFO", "init", f"Created protected folder: {PROTECTED_FOLDER}")

    log_event("INFO", "startup", f"Neuro AI Protection Activated. Monitoring: {PROTECTED_FOLDER}")

    prev_state = load_previous_state()

    while True:
        log_event("INFO", "scan_start", "Starting new scan cycle...")
        curr_state = scan_directory(PROTECTED_FOLDER)

        new_files, deleted_files, modified_files = detect_changes(prev_state, curr_state)

        analyze_security(new_files, deleted_files, modified_files, curr_state)
        ml_analyze_if_available(curr_state)

        save_state(curr_state)
        prev_state = curr_state

        time.sleep(30)  # Scan every 30 seconds


if __name__ == "__main__":
    protect_loop()
