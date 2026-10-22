# GraphTriage - Windows Setup Guide

This guide helps anyone run GraphTriage on a Windows PC.
You do not need to know Docker. You do not need Git.

## What you need

- Windows 10 (version 21H2 or newer) or Windows 11, 64-bit
- 8 GB RAM or more (16 GB is better)
- 15 GB free space on drive C:
- Internet connection
- Administrator permission (only once, to install Docker Desktop)

## Choose one way

- **Way 1: Automatic (easiest).** A script checks your PC, installs Docker if needed, and starts the app.
- **Way 2: Manual.** You do each step yourself. Use this if Way 1 does not work.

---

## Way 1: Automatic

### Step 1: Open PowerShell

Click the **Start** button, type `PowerShell`, press **Enter**.
A window with a blue or black background opens.

### Step 2: Run the setup script

Copy these two lines, paste them into the PowerShell window (right-click pastes), then press **Enter**:

```powershell
irm https://raw.githubusercontent.com/Furquan-Shaikh/graphtriage/main/setup-windows.ps1 -OutFile setup-windows.ps1
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
```

The script prints `[OK]` for every check that passes. Now one of three things happens:

- It prints **ALL DONE**: go to Step 4.
- It says **Docker Desktop is installed, restart your PC**: go to Step 3.
- It prints a red **[XX]** error: read the message, or see Troubleshooting at the bottom.

### Step 3: Only if the script told you to restart

1. Restart your PC.
2. Open **Docker Desktop** from the Start menu. Accept the terms. Wait until the bottom-left corner shows **Engine running** (green).
3. Open PowerShell again (Step 1) and run only this line:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup-windows.ps1
```

The first run downloads about 3 GB and takes 5 to 15 minutes. Wait until you see **ALL DONE**.

### Step 4: Test in the browser

The browser opens by itself. If it does not, open http://localhost:8080

1. Log in with username `demo_user` and password `ChangeMe123!`
2. You should see a dashboard with **1202 total tickets**.
3. Click any ticket in the list, then click **Get prediction** and **Get explanation**. Results should appear.
4. Open http://localhost:7474 (Neo4j). Log in with `neo4j` and `demo_neo4j_pass`.
5. Type this in the top box and press the blue play button. You should see a graph:

```
MATCH (t:Ticket)-[:RAISED_ON]->(s:Service) RETURN t,s LIMIT 50
```

If a port was busy, the script chose another one and printed the correct addresses at the end. Use those.

---

## Way 2: Manual

### Step 1: Check your Windows version

Press **Windows key + R**, type `winver`, press **Enter**.
You need Windows 10 version 21H2 or newer, or Windows 11.

### Step 2: Check that virtualization is enabled

1. Press **Ctrl + Shift + Esc** to open Task Manager.
2. Click **Performance**, then **CPU**.
3. At the bottom right, find **Virtualization**. It must say **Enabled**.

If it says **Disabled**: restart the PC, open the BIOS (usually by pressing F2, F10 or Del while it starts; the key depends on the laptop brand), enable **Intel Virtualization Technology** or **SVM Mode**, save, and boot Windows again.

### Step 3: Install Docker Desktop

1. Go to https://www.docker.com/products/docker-desktop/
2. Click **Download Docker Desktop** and choose **Windows**.
3. Run the installer. Keep **Use WSL 2** ticked.
4. When it finishes, restart the PC if it asks.

### Step 4: Start Docker Desktop

1. Open **Docker Desktop** from the Start menu.
2. Accept the terms. You can skip signing in.
3. Wait until the bottom-left corner shows **Engine running** (green).

### Step 5: Download the project

1. Open https://github.com/Furquan-Shaikh/graphtriage/archive/refs/heads/main.zip (the download starts).
2. Right-click the ZIP file, choose **Extract All**, and extract it to `C:\`.
3. You now have the folder `C:\graphtriage-main`.

### Step 6: Open PowerShell inside the project folder

1. Open `C:\graphtriage-main` in File Explorer. You should see the file `docker-compose.yml`.
2. Click the address bar at the top, type `powershell`, press **Enter**.

### Step 7: Start the app

```powershell
docker compose up -d
```

The first run downloads about 3 GB and takes 5 to 15 minutes.

### Step 8: Check that everything started

```powershell
docker ps -a
```

You should see `graphtriage-ticketing-service`, `graphtriage-inference-service`, `graphtriage-mysql` and `graphtriage-neo4j` with status **Up**.
`graphtriage-graph-seed` shows **Exited (0)**. That is normal: it is a one-time job that loads the graph.

### Step 9: Test in the browser

Same as Way 1, Step 4.

---

## Everyday commands

Run these in the project folder (for Way 1 it is `C:\Users\<your name>\graphtriage`).

| What you want | Command |
|---|---|
| Stop the app (keeps data) | `docker compose down` |
| Start it again | `docker compose up -d` |
| Delete all data and start fresh | `docker compose down -v` |

## Troubleshooting

- **"Docker is not running" or "cannot connect to the docker API"**: open Docker Desktop and wait for **Engine running**.
- **"WSL needs an update"**: open PowerShell as Administrator and run `wsl --update`, then restart Docker Desktop.
- **Virtualization error**: see Way 2, Step 2.
- **Port already in use (Way 2)**: close the program that uses ports 8080, 8000, 3307, 7474 or 7687, or use Way 1, which picks free ports automatically.
- **Download keeps failing or is very slow**: turn off VPN or proxy and try again. The same command can be run again; it continues where it stopped.
- **The first start is slow**: it downloads about 3 GB. Later starts take under a minute.
- **Still stuck?** Send the file `%TEMP%\graphtriage-setup.log` (Way 1) or the error text to whoever shared the project with you.

## Remove everything

1. In the project folder: `docker compose down -v`
2. Delete the project folder.
3. Uninstall Docker Desktop from Windows Settings -> Apps (optional).

## Notes

- The usernames and passwords in this guide are demo values for local use only. Do not expose these ports to the internet.
- You can read the script before running it: `setup-windows.ps1` is in this repository.