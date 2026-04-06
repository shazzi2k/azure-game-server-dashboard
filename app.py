from flask import Flask, render_template, jsonify
import os
import subprocess
import socket
import psutil
import platform



cpu_name = platform.processor()
app = Flask(__name__)

def get_cpu_name():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except:
        return "Unknown CPU"

cpu_name = get_cpu_name()




@app.route("/stats")
def stats():
    return {
        "cpu": get_cpu_name(),
        "cpu_usage": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    }


@app.route("/")
def home():
    return render_template("index.html")

@app.route('/api/containers')
def container_status():
    output = subprocess.getoutput("docker ps -a --format '{{.Names}} {{.State}}'")
    
    containers = {}
    
    for line in output.splitlines():
        name, state = line.split()
        containers[name] = state
    
    return containers

@app.route('/api/system')
def system_status():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return {
        "hostname": socket.gethostname(),
        "cpu": cpu,
        "ram_used": round(ram.used / (1024**3), 2),
        "ram_total": round(ram.total / (1024**3), 2),
        "disk_used": round(disk.used / (1024**3), 2),
        "disk_total": round(disk.total / (1024**3), 2)
    }
@app.route('/api/docker-stats')
def docker_stats():
    import json

    cmd = "docker stats --no-stream --format '{{json .}}'"
    output = subprocess.getoutput(cmd)

    stats = {}

    for line in output.splitlines():
        try:
            data = json.loads(line)
            name = data["Name"]

            stats[name] = {
                "cpu": data["CPUPerc"],
                "mem": data["MemUsage"]
            }
        except:
            continue

    return stats

@app.route('/api/vm-games')
def vm_games():
    import requests

    vm_output = subprocess.getoutput("virsh -c qemu:///system list --all")

    if "windows-gaming" in vm_output and "running" not in vm_output:
        return {
            "dcs": False,
            "sons": False,
            "vm": "stopped"
        }

    try:
        data = requests.get("http://192.168.0.58:6000/status", timeout=2).json()

        # 🔥 NORMALISE KEYS HERE
        return {
            "dcs": data.get("dcs", False),
            "sons": data.get("sons", False),
            "vm": "running"
        }

    except Exception as e:
        print("VM GAMES ERROR:", e)
        return {
            "dcs": False,
            "sons": False,
            "vm": "unknown"
        }


@app.route('/api/vms')
def vm_status():
    output = subprocess.getoutput("virsh list --all")

    vms = {}

    for line in output.splitlines()[2:]:
        parts = line.split()

        if len(parts) >= 3:
            name = parts[1]
            state = " ".join(parts[2:]).lower()  # handles "shut off"

            if "running" in state:
                vms[name] = "running"
            else:
                vms[name] = "stopped"

    return vms

### VM / VIRSH SECTION ###

@app.route('/vm/start/<name>')
def start_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "start", name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return f"{name} started"
    else:
        return f"Error: {result.stderr}"


@app.route('/vm/stop/<name>')
def stop_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "shutdown", name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return f"{name} stopping"
    else:
        return f"Error: {result.stderr}"


@app.route('/vm/restart/<name>')
def restart_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "reboot", name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return f"{name} restarting"
    else:
        return f"Error: {result.stderr}"
    


@app.route('/api/start/sotf')
def start_sotf():
    import requests
    try:
        r = requests.get("http://192.168.0.58:6000/start/sotf", timeout=5)
        return r.text
    except Exception as e:
        return str(e)


@app.route('/api/start/dcs')
def start_dcs():
    import requests
    try:
        r = requests.get("http://192.168.0.58:6000/start/dcs", timeout=5)
        return r.text
    except Exception as e:
        return str(e)

###DOCKER CONTAINER SECTION###
@app.route('/docker/start/<name>')
def start_container(name):
    subprocess.run(["docker", "start", name])
    return f"{name} started"

@app.route('/docker/stop/<name>')
def stop_container(name):
    subprocess.run(["docker", "stop", name])
    return f"{name} stopped"

@app.route('/docker/restart/<name>')
def restart_container(name):
    subprocess.run(["docker", "restart", name])
    return f"{name} restarted"

###CURRENT STATUS###
@app.route('/status')
def status():
    vms = subprocess.getoutput("virsh list --all")
    containers = subprocess.getoutput("docker ps -a")
    return f"<pre>{vms}\n\n{containers}</pre>"


###BACKUP SECTION###


###MONITORING SECTION###


#####RUN#####
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
