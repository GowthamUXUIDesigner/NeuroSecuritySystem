@echo off
echo Enabling Windows Firewall and hardening inbound rules...
netsh advfirewall set allprofiles state on
netsh advfirewall set allprofiles firewallpolicy blockinbound,allowoutbound
echo Done. Press any key to exit.
pause
