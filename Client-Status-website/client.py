import requests
import psutil
import socket
import time

client_id = socket.gethostname()

while True:
    info = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'virtual_memory': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }

    requests.post('http://116.203.46.145:5000/info', json={'client_id': client_id, 'data': info})
    time.sleep(60)
