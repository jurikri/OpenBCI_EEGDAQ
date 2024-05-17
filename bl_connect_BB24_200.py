# -*- coding: utf-8 -*-
"""
Created on Fri May 17 11:16:10 2024

@author: PC
"""

import bluetooth # https://github.com/pybluez/pybluez
import serial
import serial.tools.list_ports
from pyOpenBCI import OpenBCICyton
import subprocess

# 블루투스 기기 검색
def find_bluetooth_device(target_name):
    print("Searching for devices...")
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
    
    for addr, name in nearby_devices:
        print(f"Found {name} - {addr}")
        if target_name == name:
            print(f"Target device '{target_name}' found. Address: {addr}")
            return addr
    
    print(f"Target device '{target_name}' not found.")
    return None

# 사용 가능한 직렬 포트 검색
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    return [port.device for port in ports]

# # 특정 직렬 포트에 데이터 전송
# def send_data_via_serial(port_name, data, baud_rate=9600):
#     try:
#         with serial.Serial(port_name, baud_rate) as ser:
#             print(f"Connected to {port_name}")
#             ser.write(data.encode())
#             print(f"Data sent: {data}")
#     except serial.SerialException as e:
#         print(f"Failed to send data to {port_name}. Error: {e}")

#%%
connected = False

def connect_try(port=None):
    import time
    import os
    import pickle
    from datetime import datetime
    from pyOpenBCI import OpenBCICyton
    import queue
    import threading
    
    callback_count = 0
    full_data = []
    start_time = None
    save_interval = 5
    last_save_time = time.time()
    data_queue = queue.Queue()
    
    connection_timeout = 10  # seconds
    connection_start_time = time.time()
    
    def callback(sample):
        global callback_count, start_time, last_save_time, connected
    
        if start_time is None:
            start_time = time.time()
    
        callback_count += 1
    
        current_time = time.time()
        if current_time - start_time >= 1.0:
            print(f"FPS: {callback_count}")
            callback_count = 0
            start_time = current_time
    
        data = [sample.channels_data[channel] for channel in range(8)] + [current_time]
        if any(data[:-1]):  # Check if any data point is non-zero or valid
            connected = True  # Data is valid, so we set the connected flag to True
        full_data.append(data)
        data_queue.put(data)
    
        if False:
            if current_time - last_save_time >= save_interval:
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.pkl")
                filename = os.path.join(current_path, 'data', filename)
                with open(filename, 'wb') as file:
                    pickle.dump(full_data, file)
                    print(f"Data saved to {filename}")
                    full_data.clear()
                last_save_time = current_time
    
    def connect_with_timeout(port, daisy, timeout):
        global connected
        def target():
            global board
            try:
                board = OpenBCICyton(port=port, daisy=daisy)
                board.start_stream(callback)
            except Exception as e:
                connected = False
                print(f"An error occurred: {e}")
    
        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
    
        if not connected:
            raise TimeoutError("Connection attempt timed out or no data received.")
    
    # port = 'COM3'
    daisy = False
    
    try:
        connect_with_timeout(port, daisy, connection_timeout)
        if connected:
            print("Successfully connected to OpenBCI Cyton board.")
        else:
            print("No data received, connection failed.")
    except TimeoutError as e:
        print(f"Failed to connect: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return connected

#%%

def main():
    target_name = "BB24_200"  # 목표 블루투스 기기 이름
    target_address = find_bluetooth_device(target_name)
    
    if target_address is not None:
        # Using Bluetooth device pair script for Windows
        pair_script = f"""
        $ErrorActionPreference = "Stop"
        Add-Type -AssemblyName System.Windows.Forms
        [System.Windows.Forms.MessageBox]::Show('Pairing with {target_name} - {target_address}', 'Bluetooth Pairing', 'OK', 'Information')
        Start-Process powershell -ArgumentList "Start-Process -Verb RunAs 'powershell.exe -Command \\"& {{Add-BluetoothDevice -Address {target_address}}}\\"'" -Wait
        """
        pair_command = f'powershell -Command "{pair_script}"'
        try:
            subprocess.run(pair_command, shell=True, check=True)
            print(f"Pairing with device {target_name} at address {target_address}")
        except subprocess.CalledProcessError as e:
            print(f"Failed to pair with device: {e}")
    else:
        print(f"Could not find target device '{target_name}'")
        
    if target_address:
        print(f"Target Bluetooth device '{target_name}' found with address {target_address}")
        
        # 사용 가능한 모든 직렬 포트 나열
        ports = list_serial_ports()
        print("Available serial ports:", ports)
        
        for port in ports:
            print(f"Trying port {port}...")
            connected = connect_try(port=port)
            if connected: 
                print('Connecting is succeeded at port', port)
                break

if __name__ == "__main__":
    main()
    
    
#%%

# import threading
# import time
# from pyOpenBCI import OpenBCICyton

# class TimeoutException(Exception):
#     pass

# def connect_with_timeout(board, timeout):
#     def target():
#         try:
#             board.start_stream()  # Replace with the actual connection method if different
#         except Exception as e:
#             board.error = e

#     thread = threading.Thread(target=target)
#     thread.start()
#     thread.join(timeout)

#     if thread.is_alive():
#         raise TimeoutException("Connection attempt timed out")
#     if hasattr(board, 'error'):
#         raise board.error

# port = 'COM3'  # Replace with your actual port
# daisy = False

# try:
#     board = OpenBCICyton(port=port, daisy=daisy)
#     connect_with_timeout(board, timeout=10)  # 10 seconds timeout
#     print("Successfully connected to OpenBCI Cyton board.")
# except TimeoutException as e:
#     print(f"Failed to connect: {e}")
# except Exception as e:
#     print(f"An error occurred: {e}")


#%%

































