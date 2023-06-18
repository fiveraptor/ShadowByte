from flask import Flask, render_template_string
from threading import Thread
import time

app = Flask(__name__)

# Status und Zeitstempel der letzten Aktualisierung (standardmäßig offline und 0)
client_status = "offline"
last_update = 0
TIMEOUT = 1

def check_timeout():
    global client_status, last_update
    while True:
        time.sleep(10)
        if time.time() - last_update > TIMEOUT:
            client_status = "offline"

@app.route('/')
def home():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
        <body>
            <h2>Status des Computers: {{status}}</h2>
        </body>
    </html>
    """, status=client_status)

@app.route('/update_status/<new_status>')
def update_status(new_status):
    global client_status, last_update
    client_status = new_status
    last_update = time.time()
    return "Status updated", 200

if __name__ == '__main__':
    Thread(target=check_timeout).start()
    app.run(host='0.0.0.0', port=5000)