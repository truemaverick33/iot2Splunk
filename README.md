# IoT2Splunk

IoT2Splunk is an innovative project that integrates IoT devices with Splunk for real-time data logging and monitoring. The system forwards sensor data from NodeMCU devices to a Splunk instance using HTTP Event Collector (HEC). This solution is ideal for tracking and analyzing environmental metrics or any custom IoT application.

## Features

- **Real-time IoT Data Logging**: Collects and logs data from IoT sensors such as DHT11 (temperature and humidity) and IR sensors.
- **Splunk Integration**: Forward logs to Splunk for advanced analytics, visualization, and alerting.
- **Customizable Sensor Thresholds**: Define conditions to trigger specific log messages.
- **Device Management**: 
  - Block or unblock devices.
  - Assign or change Splunk indexes for specific devices.
  - View current device configurations.
- **Scalable and Extendable**: Easily add new IoT devices or sensors.
- **Logs Dashboard**: Analyze logs directly in Splunk with your custom queries and visualizations.

## Requirements

- **Hardware**:
  - NodeMCU ESP8266.
  - Sensors: DHT11, IR Sensor, or any other supported IoT sensor.
  
- **Software**:
  - Splunk installed on your PC (with HTTP Event Collector enabled).
  - Python 3.9+.
  - Arduino IDE for programming NodeMCU.

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-repo/iot2splunk.git
cd iot2splunk
```

### 2. Install Python Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Splunk
- Enable Splunk's HTTP Event Collector (HEC).
- Create an index (e.g., `iot_logs`) to store IoT logs.

### 4. Configure `conf.json`
Update the following fields in `conf.json`:
- `SPLUNK_HEC_URL`: URL for Splunk's HEC endpoint.
- `SPLUNK_HEC_TOKEN`: Token for the HEC input.
- `USERNAME` and `PASSWORD`: Splunk credentials.
- `SPLDAEMON`: Local IP address of the machine running the daemon.
- `SPLUNK_HEC_NAME`: Name of the HEC input.

### 5. Configure `dev_conf.json`
- Update the IP address of the IOT devices in the dev_conf.json according to your local configurations
- If you are unaware of IP address or have issues refer to Note 5.

### 6. Set up Arduino Enviornment
- Go to Sketch > Include Library > Manage Libraries.
- Search for DHT sensor library by Adafruit and install it.
- Install Adafruit Unified Sensor as well if prompted.
- Also Requires WifiClient library for esp8266

### 7. Set up hardware:

#### DHT11 Sensor Connection Mapping:

| **Sensor Pin** | **NodeMCU Connection** | **Arduino Connection** |  
|-----------------|-------------------------|-------------------------| 
| VCC             | 3V3                    | 5V                      |  
| Data            | D2                     | D2                      |  
| GND             | GND                    | GND                     |  

---

If there are other sensors you'd like to include, let me know and I can expand the table!

### 7. Upload Sensor Code to NodeMCU
- Replace placeholders in the provided Arduino `.ino` file:
  - `ssid` and `password` with your Wi-Fi credentials.
  - `server_ip` with the daemon's IP address (same as `SPLDAEMON` in `conf.json`).
- Upload the sketch to your NodeMCU using the Arduino IDE.

## Usage

### Start the Daemon
```bash
python iot2splunkd.py
```

### Start the Client
```bash
python iot2splunk.py
```

### Program NodeMCU
- Use the provided `.ino` file for DHT11 or IR sensors.
- Ensure necessary credentials are updated in the code.

### View Logs in Splunk
- Access Splunk's dashboard.
- Use `index=iot_logs` (or your configured index) to query IoT data.

## Screenshots

### 1. Viewing Connected Devices List  
![Cleint View Connected Device List](Screenshots/Cleint_View_Connected_Device_List.png)  

### 2. Pinging iot2Splunk Daemon via Client  
![Device Management Interface](Screenshots/Client_Ping_Server.png)  

### 3. View Device Forwarding Configuration  
![Client View Device Forwarding Configuration](Screenshots/Client_View_Device_Forwarding_Configuration.png) 

### 4. Create new splunk index to forward data:  
![Create New Splunk Index to forward data](Screenshots/Create_New_Splunk_Index_to_forward_data_to.png) 

### 5. View IOT2Splunk Daemon's Logs:
![IOT2Splunk Daemon Logs](Screenshots/IOT2Splunk_Daemon_Logs.png) 

### 6. Iot2Splunk Daemon:  
![Splunk Daemon](Screenshots/Splunk_Daemon.png) 

### 7. Server Daemon receiving logs from multiple devices:  
![Server Daemon receiving logs from multiple devices](Screenshots/Server_Daemon_receiving_logs_from_multiple_devices.png) 

### 8. Data in Splunk Index:  
![Splunk Index](Screenshots/Splunk_Index.png)


## Notes

1. **Credentials**: Update credentials and necessary placeholder values in `conf.json`, `dev_conf.json` and `.ino` files before starting.
2. **Dependencies**: Ensure all Python dependencies are installed using the provided `requirements.txt`. Also install required libraries for Arduino IDE.
3. **System Requirements**: Run both the daemon and client scripts to manage and forward IoT logs.
4. **Customizations**: Adapt sensor thresholds, Splunk index names, and log formats as per your requirements.
5. **Issues**: If you are unaware of IP address of your IOT device, you can change the dev_conf.json to just [].
6. **Wifi**: Ensure that all the devices are either in same LAN or you have configured the project accordingly to transmit over internet.
7. **Demo Code**: Demo Code for dht11 sensor and obstactle(IR) sensor are given in the Demo Directory.

## Other Contributers:
- [Mann Patel](https://github.com/Mann2oo2)

Feel free to explore, modify, and extend the project to suit your IoT and data analytics needs!
