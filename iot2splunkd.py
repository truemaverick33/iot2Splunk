from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import requests
import logging
import pyfiglet

# Load the Daemon Config file
def load_config(file_path='conf.json'):
    with open(file_path, 'r') as file:
        return json.load(file)

# Load the Device config File
def load_device_config(file_path='dev_conf.json'):
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Device configuration file '{file_path}' not found. Initializing with an empty list.")
        return []
    except json.JSONDecodeError:
        print(f"Device configuration file '{file_path}' is corrupt. Initializing with an empty list.")
        return []

# Get device Index
def get_device_index(ip, device_config):
    for device in device_config:
        if device.get('device_ip') == ip:
            if device.get('blocked',False):
                return None
            return device.get('splunk_idx', 'iot_logs')
    return 'iot_logs'

config = load_config()
device_config = load_device_config()

# Extract values from config
HOST = config['HOST']
PORT = config['PORT']
SPLUNK_HEC_URL = config['SPLUNK_HEC_URL']
SPLUNK_HEC_TOKEN = config['SPLUNK_HEC_TOKEN']
LOG_FILE = config['LOG_FILE']

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

IP_STASH = []

def init():
    ascii_art = pyfiglet.figlet_format("IoT2Splunk Daemon")
    line = pyfiglet.figlet_format("-------------")
    print(line)
    print(ascii_art)
    print(line)

class LogHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Read and parse the incoming log data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            log_entry = json.loads(post_data.decode('utf-8'))
            logging.info(f"Received log: {log_entry}")
            print("Received log:", log_entry)
            
            # Handle instructions from i2sclient
            if 'from' in log_entry and log_entry['from'] == 'i2sclient':
                if log_entry['instruction'] == 'view_devices':
                    response_data = {"devices": IP_STASH}
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                    print("Returned IP_STASH to client:", response_data)
                elif log_entry['instruction'] == "hello":
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    response_data = {
                        "message": "Hello from server",
                        "status": "success"
                    }
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    print("Instruction not recognized.")
                    self.send_response(400)
                    self.end_headers()
                return
            
            # Add IP to stash if not already present
            if 'ip' in log_entry and log_entry['ip'] not in IP_STASH:
                IP_STASH.append(log_entry['ip'])

            # Determine the Splunk index for the device
            device_ip = log_entry.get('ip')
            splunk_index = get_device_index(device_ip, device_config)
            if splunk_index:
            # Prepare Splunk payload
                splunk_data = {
                    "event": log_entry,
                    "sourcetype": "_json",
                    "source": "NodeMCU",
                    "index": splunk_index
                }
                headers = {
                    "Authorization": f"Splunk {SPLUNK_HEC_TOKEN}",
                    "Content-Type": "application/json"
                }
                response = requests.post(
                    f"{SPLUNK_HEC_URL}/services/collector",
                    headers=headers,
                    json=splunk_data,
                    verify=False
                )
                
                # Handle Splunk response
                if response.status_code == 200:
                    logging.info(f"Log sent to Splunk index '{splunk_index}' successfully!")
                    print(f"Log sent to Splunk index '{splunk_index}' successfully!")
                else:
                    error_message = f"Failed to send log to Splunk: {response.status_code}, {response.text}"
                    logging.error(error_message)
                    print(error_message)

                # Respond to the NodeMCU
                self.send_response(200)
                self.end_headers()
        except Exception as e:
            error_message = "Error processing log entry: " + str(e)
            logging.error(error_message)
            print(error_message)
            self.send_response(500)
            self.end_headers()

if __name__ == "__main__":
    init()
    httpd = HTTPServer((HOST, PORT), LogHandler)
    print(f"Server started on {HOST}:{PORT}")
    httpd.serve_forever()
