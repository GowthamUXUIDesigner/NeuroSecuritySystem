@echo off
cd /d C:\NeuroSystem

REM Start AI Protection (minimized)
start "" /MIN python neuro_protect.py

REM Start Backup Service (minimized)
start "" /MIN python backup_service.py

REM Start Dashboard (minimized)
start "" /MIN python dashboard.py

exit
