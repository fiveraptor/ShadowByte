import requests
import psutil
import socket
import time

# Erstelle eine eindeutige Client-ID basierend auf dem Hostnamen
client_id = socket.gethostname()

while True:  # Endlosschleife
    # Sammle Systeminformationen
    info = {
        'cpu_percent': psutil.cpu_percent(interval=1),
        'virtual_memory': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent
    }

    # Senden der Informationen an den Server
    requests.post('http://116.203.46.145:5000/info', json={'client_id': client_id, 'data': info})
    
    # Warte 60 Sekunden vor dem nächsten Update
    time.sleep(60)
