# GraphTriage - Windows setup

Works on Windows 10 (21H2 or newer) and Windows 11, 64-bit.
You need: about 8 GB RAM (16 GB is better), about 15 GB free disk space, internet, and admin rights (only to install Docker).

## Option A: automatic (recommended)

Open **PowerShell** (Start menu -> type "PowerShell") and paste:

```powershell
irm https://raw.githubusercontent.com/Furquan-Shaikh/graphtriage/main/setup-windows.ps1 -OutFile setup-windows.ps1
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
```

The script checks your PC, installs Docker Desktop if it is missing, downloads the project, starts everything and opens the app in your browser.

If Docker Desktop had to be installed: **restart the PC, open Docker Desktop once (accept the terms, wait for "Engine running"), then run the second command again.**

You can read the script before running it: it is `setup-windows.ps1` in this repository.

## Option B: manual

1. Install Docker Desktop: https://www.docker.com/products/docker-desktop/ (use the WSL 2 option), restart, open it, wait for "Engine running".
2. Download the project ZIP (Code -> Download ZIP) and extract it, or `git clone https://github.com/Furquan-Shaikh/graphtriage.git`.
3. In PowerShell, inside the project folder: `docker compose up -d`
4. Wait until `docker ps -a` shows `graphtriage-graph-seed` as `Exited (0)`. That is normal, it is a one-time job.

## Open the app

- App: http://localhost:8080 (login: `demo_user` / `ChangeMe123!`)
- Neo4j graph: http://localhost:7474 (login: `neo4j` / `demo_neo4j_pass`)

## Commands

- Stop: `docker compose down`
- Start again: `docker compose up -d`
- Delete all data and start fresh: `docker compose down -v`

## Troubleshooting

- **"Docker is not running"**: open Docker Desktop and wait until it says "Engine running".
- **Virtualization error**: enable Intel VT-x / AMD SVM (SVM Mode) in BIOS.
- **Port already in use**: the automatic script picks free ports for you. For the manual way, free ports 8080, 8000, 3307, 7474, 7687.
- **First start is slow**: it downloads about 3 GB. Later starts take under a minute.
- **Stuck?** Send the log file `%TEMP%\graphtriage-setup.log` to Furquan.

These are demo credentials for local use only. Do not expose these ports to the internet.