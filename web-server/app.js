const express = require('express');
const mysql = require('mysql');
const path = require('path');
const app = express();

// MySQL-Datenbankverbindung
const db = mysql.createConnection({
  host: '192.168.1.71',
  user: 'ShadowByte',
  password: 'ShadowByte',
  database: 'system_info_db'
});

db.connect((err) => {
    if (err) throw err;
    console.log('Connected to database');
  });
  
  // Setze den Ordner für statische Dateien (CSS, JS)
  app.use(express.static(path.join(__dirname, 'public')));
  
  // EJS als Template-Engine einstellen
  app.set('view engine', 'ejs');
  
  // Funktion zur Aktualisierung des Online-Status, basierend auf der Zeit, wann der Client zuletzt online war
  function updateClientStatus(callback) {
    // Setzen wir den Wert auf 10 Sekunden, da das Client-Skript alle 5 Sekunden aktualisiert wird
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
  
  // Startseite: Liste aller Clients anzeigen
  app.get('/', (req, res) => {
    updateClientStatus(() => {
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
      res.render('client_details', { clientInfo: result[0] });
    });
  });
  
  // Server starten
  app.listen(3000, () => {
    console.log('Server läuft auf http://localhost:3000');
  });