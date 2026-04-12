from flask import Flask, render_template, jsonify, session, redirect, request
import os
import subprocess
import socket
import psutil
import platform



### Login block - loads username and password from .env file ###

from dotenv import load_dotenv
load_dotenv("/srv/data/stacks/game-server-dashboard/.env")

users_raw = os.getenv("DASH_USERS")

USERS = {}

if users_raw:
    for pair in users_raw.split(","):
        user, pwd = pair.split(":")
        USERS[user.strip()] = pwd.strip()



cpu_name = platform.processor()
app = Flask(__name__)
app.secret_key = "df8765sd7a5sd67s4f4d3sdaf4ds3s4a"

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='none'
)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        print("RAW INPUT:", username, password)
        print("USERS:", USERS)

        if username:
            username = username.strip()
        if password:
            password = password.strip()

        print("STRIPPED:", username, password)

        if username in USERS:
            print("User exists")
            print("Expected password:", USERS[username])

        if username in USERS and USERS[username] == password:
            print("LOGIN SUCCESS")
            session['logged_in'] = True
            session['user'] = username
            return redirect('/')

        print("LOGIN FAILED")

        return render_template('login.html', error="Invalid login")

    return render_template('login.html')


@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect('/login')

    return render_template('index.html', user=session.get('user'))

from flask import make_response

@app.route('/logout')
def logout():
    session.clear()
    response = make_response(redirect('/login'))
    response.headers['Cache-Control'] = 'no-store'
    return response


from flask import request
from functools import wraps

from functools import wraps

from flask import request

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):

        # 🔥 allow login + static always
        if request.endpoint in ['login', 'static']:
            return f(*args, **kwargs)

        if not session.get('logged_in'):
            return {"error": "Unauthorized"}, 401

        return f(*args, **kwargs)
    return wrapper

### End login block ###




def get_cpu_name():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except:
        return "Unknown CPU"

cpu_name = get_cpu_name()


#######API ENDPOINTS#######

@app.route("/api/stats")
@login_required
def stats():
    return {
        "cpu": get_cpu_name(),
        "cpu_usage": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    }




@app.route('/api/containers')
@login_required
def get_containers():
    result = subprocess.run(
        ["docker", "ps", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )

    running = result.stdout.splitlines()

    containers = ["zomboid", "7days2die", "valheim"]

    status = {}
    for name in containers:
        status[name] = "running" if name in running else "stopped"

    return status

from flask import jsonify

@app.route('/api/system')
@login_required
def system_status():
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')

    return jsonify({
        "hostname": socket.gethostname(),
        "cpu": cpu,
        "ram_used": round(ram.used / (1024**3), 2),
        "ram_total": round(ram.total / (1024**3), 2),
        "disk_used": round(disk.used / (1024**3), 2),
        "disk_total": round(disk.total / (1024**3), 2)
    })
@app.route('/api/docker-stats')
@login_required
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


@app.route('/api/backup-status')
@login_required
def backup_status():
    import os
    import json
    from flask import jsonify

    path = '/srv/backups/backup_status.json'

    try:
        if not os.path.exists(path):
            return jsonify({
                "status": "unknown",
                "last_backup": "never",
                "upload": "unknown"
            })

        with open(path, 'r') as f:
            raw = f.read().strip()

            if not raw:
                raise Exception("Empty JSON file")

            data = json.loads(raw)

        return jsonify(data)

    except Exception as e:
        print("Backup status error:", e)

        return jsonify({
            "status": "error",
            "last_backup": "error",
            "upload": "error"
        })

import subprocess

@app.route('/api/vm-stats')
@login_required
def vm_stats():
    vm_name = "windows-gaming"

    try:
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory()

        return {
            "cpu": cpu,
            "ram_used": int(ram.used / (1024**2)),
            "ram_max": int(ram.total / (1024**2))
        }

    except Exception as e:
        return {"error": str(e)}, 500

@app.route('/api/vm-games')
@login_required
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
@login_required
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


### VM API / VIRSH SECTION ###

@app.route('/api/vm/start/<name>', methods=['POST'])
@login_required
def start_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "start", name],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        return {"vm": name, "status": "started"}
    else:
        return {"error": result.stderr}, 500

@app.route('/api/vm/stop/<name>', methods=['POST'])
@login_required
def stop_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "shutdown", name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"vm": name, "status": "stopping"}
    else:
        return {"error": result.stderr}, 500
    
@app.route('/api/vm/restart/<name>', methods=['POST'])
@login_required
def restart_vm(name):
    result = subprocess.run(
        ["virsh", "-c", "qemu:///system", "reboot", name],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        return {"vm": name, "status": "restarting"}
    else:
        return {"error": result.stderr}, 500

@app.route('/api/stop/<game>', methods=['POST'])
@login_required
def stop_game(game):
    import requests
    try:
        r = requests.get(f"http://192.168.0.58:6000/stop/{game}", timeout=5)
        return r.text
    except Exception as e:
        return str(e), 500


@app.route('/api/restart/<game>', methods=['POST'])
@login_required
def restart_game(game):
    import requests
    try:
        r = requests.get(f"http://192.168.0.58:6000/restart/{game}", timeout=5)
        return r.text
    except Exception as e:
        return str(e), 500
    


@app.route('/api/start/sotf', methods=['POST'])
@login_required
def start_sotf():
    import requests
    try:
        r = requests.get("http://192.168.0.58:6000/start/sotf", timeout=5)
        return r.text
    except Exception as e:
        return str(e)


@app.route('/api/start/dcs', methods=['POST'])
@login_required
def start_dcs():
    import requests
    try:
        r = requests.get("http://192.168.0.58:6000/start/dcs", timeout=5)
        return r.text
    except Exception as e:
        return str(e)
    
###END VM API / VIRSH SECTION ###



###DOCKER API CONTAINER SECTION###
from flask import jsonify
import subprocess

@app.route('/api/docker/start/<name>', methods=['POST'])
@login_required
def start_container(name):
    result = subprocess.run(
        ["docker", "start", name],
        capture_output=True,
        text=True
    )

    print("START:", name)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    if result.returncode != 0:
        return jsonify({
            "status": "error",
            "error": result.stderr
        }), 500

    return jsonify({"status": "started", "container": name})


@app.route('/api/docker/stop/<name>', methods=['POST'])
@login_required
def stop_container(name):
    result = subprocess.run(
        ["docker", "stop", name],
        capture_output=True,
        text=True
    )

    print("STOP:", name)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    if result.returncode != 0:
        return jsonify({
            "status": "error",
            "error": result.stderr
        }), 500

    return jsonify({"status": "stopped", "container": name})


@app.route('/api/docker/restart/<name>', methods=['POST'])
@login_required
def restart_container(name):
    result = subprocess.run(
        ["docker", "restart", name],
        capture_output=True,
        text=True
    )

    print("RESTART:", name)
    print("STDOUT:", result.stdout)
    print("STDERR:", result.stderr)

    if result.returncode != 0:
        return jsonify({
            "status": "error",
            "error": result.stderr
        }), 500

    return jsonify({"status": "restarted", "container": name})
###END DOCKER API CONTAINER SECTION###

#######END API ENDPOINTS#######

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
