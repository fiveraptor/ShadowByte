from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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

@app.route('/info', methods=['GET'])
def get_info():
    clients = SystemInfo.query.all()
    system_info = {}
    for client in clients:
        elapsed_time = datetime.utcnow() - client.last_updated
        online = elapsed_time.total_seconds() < 300
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
    clients = SystemInfo.query.all()
    system_info = {}
    for client in clients:
        elapsed_time = datetime.utcnow() - client.last_updated
        online = elapsed_time.total_seconds() < 300
        system_info[client.client_id] = {
            'cpu_percent': client.cpu_percent,
            'virtual_memory': client.virtual_memory,
            'disk_usage': client.disk_usage,
            'last_updated': client.last_updated,
            'online': online
        }
    return render_template('index.html', system_info=system_info)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)