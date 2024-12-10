import pyfiglet
import json
import requests
import os
import splunklib.client as client

conf_file_path = "dev_conf.json"

def load_config(file_path='conf.json'):
    with open(file_path, 'r') as file:
        return json.load(file)
config = load_config()

SPLUNK_HEC_URL = config['SPLUNK_HEC_URL']
SPLUNK_HEC_TOKEN = config['SPLUNK_HEC_TOKEN']
SPLUNK_AUTH_USR = config['USERNAME']
SPLUNK_AUTH_PASS = config['PASSWORD']
SPLUNK_DAEMON = config['SPLDAEMON']
HEC_NAME = config['SPLUNK_HEC_NAME']

if not os.path.exists(conf_file_path):
    conf_data = []
    with open(conf_file_path, 'w') as file:
        json.dump(conf_data, file, indent=4)
else:
    with open(conf_file_path, 'r') as file:
        try:
            conf_data = json.load(file)
            if not isinstance(conf_data, list):
                raise ValueError("Configuration file does not contain a list.")
        except json.JSONDecodeError:
            conf_data = []

def save_conf_file(conf_data):
    with open(conf_file_path, 'w') as file:
        json.dump(conf_data, file, indent=4)
        print("Configuration saved successfully! Restart the iot2Splunk Daemon to Apply Changes")


def fetch_available_indexes():   
    service = client.connect(
    host=SPLUNK_DAEMON,
    port=8089,
    username=SPLUNK_AUTH_USR,
    password=SPLUNK_AUTH_PASS
    )
    available_indexes = [index.name for index in service.indexes]
    return available_indexes

def create_new_index(new_index_name):
    try:
        service = client.connect(
            host=SPLUNK_DAEMON,
            port=8089,
            username=SPLUNK_AUTH_USR,
            password=SPLUNK_AUTH_PASS
        )
        if new_index_name not in [index.name for index in service.indexes]:
            service.indexes.create(new_index_name, maxTotalDataSizeMB=5120)
            print(f"Index '{new_index_name}' created successfully!")
        else:
            print(f"Index '{new_index_name}' already exists.")

        hec_input = None
        for input_item in service.inputs:
            if input_item.name == HEC_NAME:
                hec_input = input_item
                break

        if hec_input:
            hec_config = hec_input.content()
            allowed_indexes = hec_config.get('indexes', "")
            primary_index = hec_config.get('index', "")
            if new_index_name not in allowed_indexes:
                allowed_indexes.append(new_index_name)
                hec_input.update(index=primary_index,indexes=",".join(allowed_indexes))
                print(f"Index '{new_index_name}' added to the HEC allowed list for '{HEC_NAME}'.")
            else:
                print(f"Index '{new_index_name}' is already in the HEC allowed list for '{HEC_NAME}'.")
        else:
            print(f"Error: HEC input '{HEC_NAME}' does not exist.")

        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def configure_device(device_ip):
    for device in conf_data:
        if device['device_ip'] == device_ip:
            while True:
                print(f"\n--- Configuring Device: {device_ip} ---")
                print("1. Block logs from this device")
                print("2. Change Splunk Index")
                print("3. View current configuration")
                print("4. Go back")
                choice = input("Enter your choice: ").strip()
                
                if choice == '1':
                    device['blocked'] = True
                    print(f"Device {device_ip} is now blocked from sending logs.")
                    save_conf_file(conf_data)
                elif choice == '2':
                    print("\nAvailable Splunk Indexes:")
                    available_indexes = fetch_available_indexes()
                    if available_indexes:
                        for i, index in enumerate(available_indexes, 1):
                            print(f"{i}. {index}")
                        print(f"{len(available_indexes) + 1}. Create New Index")                      
                        index_choice = input("Choose an index: ").strip()
                        index_choice = int(index_choice) - 1
                        if 1 <= index_choice < len(available_indexes) - 1:
                                selected_index = available_indexes[index_choice]
                                device['splunk_idx'] = selected_index
                                print(f"Index updated to '{selected_index}'.")
                                save_conf_file(conf_data)
                        elif index_choice == len(available_indexes):
                            new_index_name = str(input("Enter the name of the new index: ").strip())
                            if create_new_index(new_index_name):
                                    device['splunk_idx'] = new_index_name
                                    create_new_index(new_index_name)
                                    save_conf_file(conf_data)
                            else:
                                print("Invalid choice. Try again.")
                    else:
                        print("No indexes available. Please create one.")
                elif choice == '3':
                    print(f"\nCurrent Configuration for {device_ip}:")
                    print(json.dumps(device, indent=4))
                elif choice == '4':
                    break
                else:
                    print("Invalid choice. Please try again.")
            return
    print(f"Device {device_ip} not found in configuration.")

def init():
    ascii_art = pyfiglet.figlet_format("IoT2Splunk")
    line = pyfiglet.figlet_format("---------")
    print(line)
    print(ascii_art)
    print(line)
    loop()

def loop():
    while True:
        print("\nOptions:")
        print("1. View IoT Devices")
        print("2. Ping Daemon")
        print("3. View Daemon logs")
        print("4. Exit program")
        choice = input("Enter your choice: ").strip()
        
        if choice == '1':
            print("\n--- Network IoT Devices ---")
            url = "http://127.0.0.1:8080"
            payload = {"from": "i2sclient", "instruction": "view_devices"}
            try:
                response = requests.post(url, json=payload)
                if response.status_code == 200:
                    response_data = response.json()
                    devices = response_data.get('devices', [])
                    if devices:
                        for i, device_ip in enumerate(devices, 1):
                            print(f"{i}. {device_ip}")
                        while True:
                            print("\nOptions:")
                            print("1. Configure a device")
                            print("2. View device configuration")
                            print("3. Go back")
                            sub_choice = input("Enter your choice: ").strip()
                            if sub_choice == '1':
                                device_index = input("Enter the device number to configure: ").strip()
                                if device_index.isdigit() and 1 <= int(device_index) <= len(devices):
                                    device_ip = devices[int(device_index) - 1]
                                    configure_device(device_ip)
                                else:
                                    print("Invalid device number. Please try again.")
                            elif sub_choice == '2':
                                device_index = input("Enter the device number to view configuration: ").strip()
                                if device_index.isdigit() and 1 <= int(device_index) <= len(devices):
                                    device_ip = devices[int(device_index) - 1]
                                    for device in conf_data:
                                        if device["device_ip"] == device_ip:
                                            print(json.dumps(device, indent=4))
                                            break
                                else:
                                    print("Invalid device number. Please try again.")
                            elif sub_choice == '3':
                                break
                            else:
                                print("Invalid choice. Please try again.")
                    else:
                        print("No devices found.")
                else:
                    print(f"Error: {response.text}")
            except requests.RequestException as e:
                print(f"Error connecting to the server: {e}")
        
        elif choice == '2':
            url = "http://127.0.0.1:8080"
            payload = {"from": "i2sclient", "instruction": "hello"}
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                response_data = response.json()
                print("Response from server:")
                print(json.dumps(response_data, indent=4))
            else:
                print(f"Error: {response.text}")
        
        elif choice == '3':
            print("\n--- Log File Content ---")
            try:
                with open("iot_logs.txt", 'r') as file:
                    print(file.read())
            except FileNotFoundError:
                print("Log file not found.")
        
        elif choice == '4':
            print("Exiting program...")
            break
        
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    init()
