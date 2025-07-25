# Host Setup (Server)

This guide is for the person running the central server (host) for the ASA-Database app on a local network.

## 1. Requirements
- A computer connected to the local network (WiFi or Ethernet)
- Docker and Docker Compose installed

## 2. Setup Steps
1. Copy the entire ASA-Database project folder to the host computer.
2. (Optional) Edit `research_data_app/settings.py` and set `ALLOWED_HOSTS = ['*']` or add your LAN IP address.
3. Open a terminal in the project folder.
4. Run:
   ```bash
   chmod +x run_host.sh
   ./run_host.sh
   ```
5. Wait for the app to start. It will be available at `http://localhost:8000` on the host.

## 3. Find the Host IP Address
- Run `hostname -I` or `ip addr` in the terminal.
- Note the IP (e.g., `192.168.1.10`).

## 4. Client Devices Connect
- Other users on the same network can access the app at `http://<host-ip>:8000` (e.g., `http://192.168.1.10:8000`).

## 5. Stopping & Backing Up
- Stop the app with `Ctrl+C` in the terminal.
- To back up data, copy the `postgres_data` folder.

## 6. Migrating the Server
- Copy the whole project folder (including `postgres_data`) to a new host and repeat these steps.
