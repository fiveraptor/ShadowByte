import requests
import psutil
import socket
import time
import os
import getpass
import platform
from cpuinfo import get_cpu_info

def bytes_to_gb(bytes_value):
    """Convert bytes to gigabytes and round to two decimal places."""
    return round(bytes_value / (1024 ** 3), 2)

def send_status_update(status):
    server_url = "http://116.203.46.145:5000/update_status/" + status
    try:
        response = requests.get(server_url)
        if response.status_code == 200:
            print("Status update sent successfully")
        else:
            print("Failed to send status update")
    except requests.exceptions.RequestException as e:
        print("Error sending status update:", str(e))

def send_system_info():
    client_id = socket.gethostname()  # Replace with your client ID
    server_url = "http://116.203.46.145:5000/info"
    cpu_percent = psutil.cpu_percent()
    virtual_memory = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    system_info = {
        "operating_system": platform.system(),
        "windows_version": platform.version(),
        "system_name": platform.node(),
        "system_vendor": platform.uname().system,
        "system_model": platform.uname().machine,
        "system_type": platform.uname().processor,
        "processor": get_cpu_info()['brand_raw'],
        "bios_version_date": "TBD",  # Replace this with your method to get BIOS info
        "smbios_version": "TBD",  # Replace this with your method to get SMBIOS version
        "bios_mode": "TBD",  # Replace this with your method to get BIOS mode
        "username": getpass.getuser(),
        "physical_memory_installed": bytes_to_gb(psutil.virtual_memory().total),
        "ssd_storage": bytes_to_gb(psutil.disk_usage('/').total),
    }

    data = {
        "client_id": client_id,
        "cpu_percent": cpu_percent,
        "virtual_memory": virtual_memory,
        "disk_usage": disk_usage,
        "system_info": system_info,
    }

    try:
        response = requests.post(server_url, json=data)
        if response.status_code == 200:
            print("System info sent successfully")
        else:
            print("Failed to send system info")
    except requests.exceptions.RequestException as e:
        print("Error sending system info:", str(e))

while True:
    send_system_info()
    time.sleep(5)