from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

from flask import Flask, render_template, jsonify, session, redirect, request
import os
import socket
import psutil
import platform


### Login block - loads username and password from .env file ###

users_raw = os.getenv("DASH_USERS", "admin:password")

USERS = {}
for pair in users_raw.split(","):
    if ":" in pair:
        user, pwd = pair.split(":", 1)
        USERS[user.strip()] = pwd.strip()



cpu_name = platform.processor()
app = Flask(__name__)
app.secret_key = "df8765sd7a5sd67s4f4d3sdaf4ds3s4a"

app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)



   


from flask import request, render_template

@app.route("/")
def index():
    user = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    return render_template("index.html", user=user)



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





        




### VM API / VIRSH SECTION ###


    
###END VM API / VIRSH SECTION ###



###DOCKER API CONTAINER SECTION###

###END DOCKER API CONTAINER SECTION###

#######END API ENDPOINTS#######

###CURRENT STATUS###



###BACKUP SECTION###



###MONITORING SECTION###


#####RUN#####
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
