#from azure.identity import DefaultAzureCredential
#from azure.mgmt.compute import ComputeManagementClient

from flask import Flask, render_template, jsonify, session, redirect, request

import os
import socket
import psutil
import platform
import requests

VM_AGENT = "http://52.142.166.248:5000"

### Login block - loads username and password from .env file ###

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


@app.route("/login")
def fix_login():
    return redirect("/")
   
from flask import request, render_template

@app.route("/")
def index():
    user = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    return render_template("index.html", user=user)

def require_auth():
    user = request.headers.get("X-MS-CLIENT-PRINCIPAL-NAME")
    if not user:
        return False
    return True

### End login block ###

### TEST VM API ###

@app.route("/api/vm-health")
def vm_health():

    try:
        response = requests.get(
            f"{VM_AGENT}/api/health",
            timeout=5
        )

        return response.json()

    except Exception as e:
        return {
            "status": "offline",
            "error": str(e)
        }


### End TEST VM API ###

### System Information Functions ###


#def get_cpu_name():
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if "model name" in line:
                    return line.split(":")[1].strip()
    except:
        return "Unknown CPU"

#cpu_name = get_cpu_name()

##End System Information Functions ###

#######API ENDPOINTS#######

@app.route("/api/stats")
def stats():
    return {
        "cpu": get_cpu_name(),
        "cpu_usage": psutil.cpu_percent(),
        "ram": psutil.virtual_memory().percent
    }


@app.route("/api/system")
def vm_system():

    response = requests.get(
        f"{VM_AGENT}/api/system",
        timeout=5
    )

    return response.json()

#######End of API ENDPOINTS#######

#######DockerContainer API ENDPOINTS#######

@app.route("/api/containers")
def containers():

    response = requests.get(
        f"{VM_AGENT}/api/containers",
        timeout=5
    )

    return response.json()

@app.route("/api/docker/start/<name>", methods=["POST"])
def docker_start(name):

    response = requests.post(
        f"{VM_AGENT}/api/docker/start/{name}",
        timeout=10
    )

    return response.json(), response.status_code

@app.route("/api/docker/stop/<name>", methods=["POST"])
def docker_stop(name):

    response = requests.post(
        f"{VM_AGENT}/api/docker/stop/{name}",
        timeout=10
    )

    return response.json(), response.status_code

@app.route("/api/docker/restart/<name>", methods=["POST"])
def docker_restart(name):

    response = requests.post(
        f"{VM_AGENT}/api/docker/restart/{name}",
        timeout=10
    )

    return response.json(), response.status_code
####### End DockerContainer API ENDPOINTS#######


        




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
