from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/test.db'
db = SQLAlchemy(app)

class SystemInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.String(36), unique=True, nullable=False)
    cpu_percent = db.Column(db.Float, nullable=False)
    virtual_memory = db.Column(db.Float, nullable=False)
    disk_usage = db.Column(db.Float, nullable=False)
    last_updated = db.Column(db.DateTime, nullable=False)
    online = db.Column(db.Boolean, nullable=False, default=False)

def update_client_status():
    clients = SystemInfo.query.all()
    for client in clients:
        elapsed_time = datetime.utcnow() - client.last_updated
        if elapsed_time > timedelta(seconds=30) and client.online:
            client.online = False
    db.session.commit()

@app.route('/info', methods=['POST'])
def receive_info():
    data = request.json
    client_id = data['client_id']
    cpu_percent = data['cpu_percent']
    virtual_memory = data['virtual_memory']
    disk_usage = data['disk_usage']

    system_info = SystemInfo.query.filter_by(client_id=client_id).first()
    if system_info:
        system_info.cpu_percent = cpu_percent
        system_info.virtual_memory = virtual_memory
        system_info.disk_usage = disk_usage
        system_info.last_updated = datetime.utcnow()
        system_info.online = True
    else:
        system_info = SystemInfo(client_id=client_id, cpu_percent=cpu_percent,
                                 virtual_memory=virtual_memory, disk_usage=disk_usage,
                                 last_updated=datetime.utcnow(), online=True)
        db.session.add(system_info)
    db.session.commit()

    return "Info received", 200

@app.route('/info', methods=['GET'])
def get_info():
    update_client_status()
    clients = SystemInfo.query.all()
    system_info = {}
    for client in clients:
        elapsed_time = datetime.utcnow() - client.last_updated
        online = elapsed_time.total_seconds() < 30
        system_info[client.client_id] = {
            'cpu_percent': client.cpu_percent,
            'virtual_memory': client.virtual_memory,
            'disk_usage': client.disk_usage,
            'last_updated': client.last_updated,
            'online': online
        }
    return system_info, 200

@app.route('/')
def home():
    update_client_status()
    clients = SystemInfo.query.all()
    system_info = {}
    for client in clients:
        elapsed_time = datetime.utcnow() - client.last_updated
        online = elapsed_time.total_seconds() < 30
        system_info[client.client_id] = {
            'cpu_percent': client.cpu_percent,
            'virtual_memory': client.virtual_memory,
            'disk_usage': client.disk_usage,
            'last_updated': client.last_updated,
            'online': online
        }
    return render_template('index.html', system_info=system_info)

@app.route('/update_status/<new_status>', methods=['GET'])
def update_status(new_status):
    client_id = request.remote_addr
    system_info = SystemInfo.query.filter_by(client_id=client_id).first()
    if system_info:
        system_info.online = (new_status == "online")
        system_info.last_updated = datetime.utcnow()
        db.session.commit()
        return "Status updated", 200
    else:
        return "Client not found", 404

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)