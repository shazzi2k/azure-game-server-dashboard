# 🎮 ShazCorp Game Server Dashboard

A lightweight web-based control panel for managing game servers, virtual machines, and system resources from a single interface.

---

## 🚀 Features

* 🔐 **User Authentication**

  * Secure login system using environment variables
* 🖥️ **System Monitoring**

  * CPU, RAM, Disk usage
  * Hostname and hardware info
* 🧠 **VM Management (libvirt / virsh)**

  * Start / Stop / Restart virtual machines
  * Live VM status + resource usage
* 🎮 **VM Game Server Control**

  * Remote control via API agent
  * Supports:

    * Digital Combat Simulator (DCS)
    * Sons of the Forest
* 🐳 **Docker Game Server Management**

  * Start / Stop / Restart containers
  * Live CPU + RAM usage
  * Supports:

    * Project Zomboid
    * 7 Days to Die
    * Valheim
* 💾 **Backup Monitoring**

  * Last backup timestamp
  * Next scheduled backup
  * Upload status
* ⚡ **Real-time Updates**

  * Auto-refreshing dashboard (5s interval)

---

## 🏗️ Architecture

```text
Browser (Dashboard UI)
        ↓
Flask API (Main Server)
        ↓
 ├── Docker (Game containers)
 ├── libvirt / virsh (VM control)
 └── Remote Agent (Windows VM)
```

---

## 📦 Requirements

* Python 3.10+
* Flask
* psutil
* Docker
* libvirt / virsh
* Linux host (tested on Ubuntu Server)

---

## ⚙️ Installation

### 1. Clone repo

```bash
git clone https://github.com/YOURNAME/game-server-dashboard.git
cd game-server-dashboard
```

---

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Create `.env`

```env
DASH_USERS=username:password,anotheruser:password
```

⚠️ Do NOT commit this file

---

### 5. Run the app

```bash
python app.py
```

---

### 6. Access dashboard

```
http://YOUR_SERVER_IP:5000
```

---

## 🖥️ VM Agent (Windows)

A lightweight Flask API runs on the Windows VM to control game servers.

### Example endpoints:

* `/status`
* `/start/dcs`
* `/stop/dcs`
* `/restart/dcs`

---

## 🔐 Security Notes

* Uses session-based authentication
* `.env` stores credentials (keep private)
* Recommend:

  * Reverse proxy (NGINX)
  * HTTPS (Let's Encrypt)
  * Firewall rules

---

## 🛠️ API Overview

### System

* `/api/system`
* `/api/stats`

### VM

* `/api/vm/start/<name>`
* `/api/vm/stop/<name>`
* `/api/vm/restart/<name>`
* `/api/vms`
* `/api/vm-stats`

### VM Games

* `/api/start/<game>`
* `/api/stop/<game>`
* `/api/restart/<game>`
* `/api/vm-games`

### Docker

* `/api/docker/start/<name>`
* `/api/docker/stop/<name>`
* `/api/docker/restart/<name>`
* `/api/docker-stats`
* `/api/containers`

### Backup

* `/api/backup-status`

---

## 📊 Future Improvements

* 🔁 WebSocket real-time updates
* 👥 Multi-user roles & permissions
* 📜 Action logging / audit trail
* 📦 Docker Compose integration
* 📈 Performance graphs
* 🤖 Discord bot integration improvements

---

## ⚠️ Disclaimer

This project is designed for personal / homelab use.
Use proper security practices before exposing it publicly.

---

## 👤 Author

ShazCorp Cloud Platform
Built for managing distributed game infrastructure.

---
