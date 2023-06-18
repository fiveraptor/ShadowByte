import requests
import psutil
import socket
import time

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

    data = {
        "client_id": client_id,
        "cpu_percent": cpu_percent,
        "virtual_memory": virtual_memory,
        "disk_usage": disk_usage
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
