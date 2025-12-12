@echo off
cd /d C:\NeuroSystem
start "" python neuro_protect.py
start "" python backup_service.py
start "" python dashboard.py
exit
