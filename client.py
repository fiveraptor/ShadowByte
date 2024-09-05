import psutil
import socket
import time
import os
import getpass
import platform
import mysql.connector
from cpuinfo import get_cpu_info

def bytes_to_gb(bytes_value):
    """Convert bytes to gigabytes and round to two decimal places."""
    return round(bytes_value / (1024 ** 3), 2)

def get_or_create_client(connection, client_id, hostname):
    cursor = connection.cursor()

    # Prüfen, ob der Client bereits in der Datenbank existiert
    cursor.execute("SELECT id FROM clients WHERE client_id = %s", (client_id,))
    result = cursor.fetchone()

    if result:
        return result[0]  # Client ID zurückgeben
    
    # Wenn der Client nicht existiert, füge ihn hinzu
    add_client = ("INSERT INTO clients (client_id, hostname, online_status, last_online) "
                  "VALUES (%s, %s, %s, CURRENT_TIMESTAMP)")
    cursor.execute(add_client, (client_id, hostname, True))  # Online setzen, wenn der Client erstellt wird
    connection.commit()
    
    return cursor.lastrowid  # ID des neuen Clients zurückgeben

def update_system_info(connection, client_db_id, system_info):
    cursor = connection.cursor()

    # SQL-Abfrage zum Aktualisieren der bestehenden Systeminformationen und des Online-Status
    update_system_info = ("""
        INSERT INTO system_info (
            client_id, cpu_percent, virtual_memory, disk_usage, operating_system, 
            windows_version, system_name, system_vendor, system_model, system_type, 
            processor, bios_version_date, smbios_version, bios_mode, username, 
            physical_memory_installed, ssd_storage
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            cpu_percent = VALUES(cpu_percent),
            virtual_memory = VALUES(virtual_memory),
            disk_usage = VALUES(disk_usage),
            operating_system = VALUES(operating_system),
            windows_version = VALUES(windows_version),
            system_name = VALUES(system_name),
            system_vendor = VALUES(system_vendor),
            system_model = VALUES(system_model),
            system_type = VALUES(system_type),
            processor = VALUES(processor),
            bios_version_date = VALUES(bios_version_date),
            smbios_version = VALUES(smbios_version),
            bios_mode = VALUES(bios_mode),
            username = VALUES(username),
            physical_memory_installed = VALUES(physical_memory_installed),
            ssd_storage = VALUES(ssd_storage),
            recorded_at = CURRENT_TIMESTAMP;
    """)

    # Aktualisieren des Online-Status und des letzten Online-Zeitpunkts in der Clients-Tabelle
    update_client_status = ("""
        UPDATE clients
        SET online_status = %s, last_online = CURRENT_TIMESTAMP
        WHERE id = %s;
    """)

    # Daten für die Systeminformationen
    data_system_info = (
        client_db_id,
        system_info['cpu_percent'],
        system_info['virtual_memory'],
        system_info['disk_usage'],
        system_info['system_info']['operating_system'],
        system_info['system_info']['windows_version'],
        system_info['system_info']['system_name'],
        system_info['system_info']['system_vendor'],
        system_info['system_info']['system_model'],
        system_info['system_info']['system_type'],
        system_info['system_info']['processor'],
        system_info['system_info']['bios_version_date'],
        system_info['system_info']['smbios_version'],
        system_info['system_info']['bios_mode'],
        system_info['system_info']['username'],
        system_info['system_info']['physical_memory_installed'],
        system_info['system_info']['ssd_storage']
    )

    # Update-Queries ausführen
    cursor.execute(update_system_info, data_system_info)
    cursor.execute(update_client_status, (True, client_db_id))  # Online setzen und den letzten Online-Zeitpunkt aktualisieren

    connection.commit()
    cursor.close()

    print("System info and client status successfully updated in database for client ID:", client_db_id)

def send_system_info():
    # Verbinde mit der Datenbank
    connection = mysql.connector.connect(
        host="192.168.1.71", 
        user="ShadowByte", 
        password="ShadowByte", 
        database="system_info_db"
    )

    client_id = socket.gethostname()
    hostname = platform.node()
    
    # Holen oder Erstellen des Clients in der Datenbank
    client_db_id = get_or_create_client(connection, client_id, hostname)

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
        "bios_version_date": "TBD",
        "smbios_version": "TBD",
        "bios_mode": "TBD",
        "username": getpass.getuser(),
        "physical_memory_installed": bytes_to_gb(psutil.virtual_memory().total),
        "ssd_storage": bytes_to_gb(psutil.disk_usage('/').total),
    }

    data = {
        "cpu_percent": cpu_percent,
        "virtual_memory": virtual_memory,
        "disk_usage": disk_usage,
        "system_info": system_info,
    }

    # Aktualisieren der Daten in der MySQL-Datenbank
    update_system_info(connection, client_db_id, data)
    connection.close()

while True:
    send_system_info()
    time.sleep(5)
