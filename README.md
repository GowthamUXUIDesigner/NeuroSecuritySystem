**Neuro Security Ecosystem**
AI-Assisted, File-Level Threat Monitoring, Backup Protection & Dashboard System
Runs fully automated on Windows.

**Overview**

The Neuro Security Ecosystem is a lightweight, local security monitoring framework that:
Detects abnormal file behavior
Identifies suspicious executables
Warns about ransomware-like activity
Predicts anomalies using ML
Performs automatic backups
Displays a live minimal dashboard
Starts automatically when Windows boots

It is NOT a replacement for commercial antivirus.
It is an awareness + monitoring + backup safety layer.

**Features
✔ Real-time monitoring**

Detects new files, deleted files, modified files, and hash changes.

**✔ Attack-type classification**

Flags:

Possible ransomware
Suspicious executable/script
Abnormal file patterns
ML-based anomalies

**✔ Auto backups**

Every 10 minutes, the system mirrors protected data into secure backups.

**✔ Minimal UI Dashboard**

Runs at:

http://localhost:5000/


Shows:

Alerts
Warnings
Live events
What was detected
How the system responded

**✔ Auto-start on login**

A small Task Scheduler job starts the system at boot.

**Folder Structure**
C:\NeuroSystem\
│
├── neuro_protect.py      # AI threat engine
├── backup_service.py     # Auto backup system
├── dashboard.py          # Minimal UI dashboard
├── start_all.bat         # Starts all services
├── firewall_setup.bat    # Firewall hardening (one-time setup)
├── config.json           # Configuration paths
│
├── neuro_logs.json       # (auto-created) security logs
├── file_state.json       # (auto-created) previous scan snapshot
│
├── protected_data\       # Files monitored + protected
└── backups\              # Auto backups

**Requirements**
**1. Install Python**

**Download from:**
https://www.python.org/downloads/windows/

**During installation, CHECK:**

✔ Add Python to PATH
Then click Install Now

**2. Install dependencies**

Open Command Prompt:

pip install flask scikit-learn

Configuration

Edit config.json:

{
  "protected_folder": "C:/NeuroSystem/protected_data",
  "backup_folder": "C:/NeuroSystem/backups"
}

**How to Run the System**

There are two ways.

**METHOD 1 — Start manually (for testing)**
1) Start protection engine
python neuro_protect.py

2) Start backup service
python backup_service.py

3) Start dashboard
python dashboard.py

**Open in browser:**

http://localhost:5000/

**METHOD 2 — Auto-start when Windows boots (recommended)**
**Step 1 — Create autostart script**

start_all.bat:

@echo off
cd /d C:\NeuroSystem
start "" python neuro_protect.py
start "" python backup_service.py
start "" python dashboard.py
exit

**Step 2 — Add to Task Scheduler**

Open Task Scheduler
Create Task → Name: NeuroSecurity AutoStart
Trigger: At log on
Action: Start Program → start_all.bat

Save

Now your security system starts automatically every login.

**How It Works (Internally)**
**1. File Monitoring**

Every 30 seconds:
Scans folder
Compares with previous snapshot
Detects new/modified/deleted files
Evaluates suspicious patterns
Generates alerts

**2. ML Analysis**

IsolationForest model:
Learns file size distributions
Flags abnormal file behavior

**3. Ransomware Detection**

Triggered when:
Many files change too quickly
Hash + size shift together

**4. Suspicious Executable Detection**

Flags .exe, .dll, .js, .bat, .ps1 dropped into the folder.

**5. Auto Backup**

Every 10 minutes:
Copies protected folder → backup folder
Maintains clean recoverable versions

**6. Dashboard**

Reads last 50 events
Shows alerts, warnings, info
Auto-refreshes every 5 seconds

**Why This System Is Useful**

Helps users understand what kind of activity is happening
Provides explainable security logs
Early warnings for abnormal behaviors
Gives ransomware-like detection automatically
Protects files through snapshots
Helps beginners learn cybersecurity concepts

**Disclaimer**

This system is NOT a replacement for Windows Defender or professional antivirus solutions.
It is a research, monitoring, and awareness tool.

**License**

You may use, modify, and distribute freely for educational or personal use.

**For the future update i will add the fetures of:**

Email alerts
Telegram/mobile notifications
EXE installer
Encryption for backups
Role-based dashboard login
Neural-network threat classifier
Tell me what you want, and I will build the next version.

**END OF README**
