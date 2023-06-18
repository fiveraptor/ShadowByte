import requests
import time

SERVER_URL = "http://168.119.235.72:5000/update_status/"

while True:
    try:
        requests.get(SERVER_URL + "online")  # Informiere den Server, dass der Client online ist
        time.sleep(1)  # Warte 1 Sekunden
    except Exception as e:
        print(f"Kann nicht mit dem Server verbinden: {e}")
