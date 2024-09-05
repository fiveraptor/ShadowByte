# ShadowByte System Monitoring
ShadowByte is a system monitoring tool that allows collecting system information from clients and displaying it on a central server. Additionally, the tool stores Wi-Fi information (SSID and password) from the clients and shows the online/offline status.

## Features
- System Information Collection: CPU usage, disk usage, operating system, memory information, and other client system data are collected at regular intervals.
- Wi-Fi Information Collection: Retrieves stored Wi-Fi SSIDs and passwords from clients and displays them on the server.
- Online/Offline Status: The online status of clients is automatically updated based on their last activity.
- Web-based Frontend: Provides an overview of all clients and their details, including system and Wi-Fi information.
- SSL Support: The web interface is hosted via HTTPS with a self-signed certificate.

## Prerequisites
- Python 3.x
- Node.js
- MySQL/MariaDB
- Network access between client and server
- Supported operating systems:
    - Windows (for retrieving Wi-Fi profiles)
    - Linux (for retrieving system and Wi-Fi data)

## Installation
1. Set Up the Database
   
    Create a MySQL database to store system and Wi-Fi information.
    ```sql
    CREATE DATABASE system_info_db;

    USE system_info_db;

    CREATE TABLE clients (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id VARCHAR(255),
        hostname VARCHAR(255),
        online_status BOOLEAN DEFAULT 0,
        last_online TIMESTAMP,
        UNIQUE (client_id)
    );

    CREATE TABLE system_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT,
        cpu_percent FLOAT,
        virtual_memory FLOAT,
        disk_usage FLOAT,
        operating_system VARCHAR(255),
        windows_version VARCHAR(255),
        system_name VARCHAR(255),
        system_vendor VARCHAR(255),
        system_model VARCHAR(255),
        system_type VARCHAR(255),
        processor VARCHAR(255),
        bios_version_date VARCHAR(255),
        smbios_version VARCHAR(255),
        bios_mode VARCHAR(255),
        username VARCHAR(255),
        physical_memory_installed FLOAT,
        ssd_storage FLOAT,
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    );

    CREATE TABLE wifi_info (
        id INT AUTO_INCREMENT PRIMARY KEY,
        client_id INT,
        ssid VARCHAR(255),
        password VARCHAR(255),
        recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
    );
    ```

2. Set Up the Server

    Install dependencies and start the server:
    1. Install Node.js and dependencies:
        ```
        npm install express ejs mysql https fs
        ```
    2. Generate SSL certificates (optional, for local development):
        ```
        openssl req -nodes -new -x509 -keyout server.key -out server.cert
        ```
    3. Start the server:
        ```
        node app.js
        ```
The server will now run at https://localhost:3000.

3. Set Up the Client
    1. Install Python dependencies:
        ```
        pip install psutil platform cpuinfo mysql-connector-python
        ```
    2. Configure the client script: Adjust the database connection in the client script.
    3. Run the client:
        ```
        python3 client.py
        ```
The client will send system and Wi-Fi information to the server every 5 seconds.

## Usage
### Web Interface
- Main Page: Lists all clients with their online/offline status, showing the last online timestamp and allowing users to view details or Wi-Fi information for each client.
- Details Page: Displays detailed system information for a selected client.
- Wi-Fi Page: Displays stored Wi-Fi SSIDs and passwords for a client.

### Features
- Delete Client: The main page includes a button to delete a client and all associated data.
- View System Information: Shows details such as CPU usage, disk usage, operating system, and more for each client.
- View Wi-Fi Information: Lists the stored Wi-Fi SSIDs and passwords for a client, with an option to copy them.

## SSL Certificate
For a development environment, you can use a self-signed certificate as described above. For production environments, it is recommended to use a trusted SSL certificate.

## Security
- Wi-Fi passwords are stored in plain text. This should only be used in a secure, closed environment.
- For production use, ensure proper security measures are in place to protect the transmission and storage of passwords.

## Authors
- Joris Bieg
- Luka Petkovic