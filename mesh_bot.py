#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot

import signal
import time
from typing import List
from pubsub import pub
from datetime import datetime
from basic_bot import BasicBot
from message_processor import MessageProcessor
from serial_mesh import SerialMeshHelper

import meshtastic.serial_interface
import meshtastic.tcp_interface
import meshtastic.ble_interface

from weather_bot import WeatherBot

# Uncomment the interface you want to use depending on your device connection
#interface = meshtastic.serial_interface.SerialInterface() #serial interface
interface=meshtastic.tcp_interface.TCPInterface(hostname="10.0.4.36") # IP of your device
#interface=meshtastic.ble_interface.BLEInterface("10:06:1C:49:90:36") # BLE interface - find it using meshtastic --ble-scan

#interface = None

myinfo = interface.getMyNodeInfo()
myNodeNum = myinfo['num']
print(f"System: My Node Number is {myNodeNum}")

bb = BasicBot()
wb = WeatherBot()

message_processors:List[MessageProcessor] = [bb, wb]
sh = SerialMeshHelper(interface, message_processors)

# if not serial or serial.myNodeNum == -1:
#     print("System: Critical Error script abort. Could not get myNodeNum")
#     exit()

def exit_handler(signum, frame):
    print("\nSystem: Closing Autoresponder")
    interface.close()
    exit (0)

print ("\nMeshtastic Autoresponder MESH Bot CTL+C to exit\n")
pub.subscribe(sh.onReceive, 'meshtastic.receive')
print (f"System: Autoresponder Started for device {sh.get_name_from_number(sh.myNodeNum)}")

while True:
    # Catch CTL+C to exit
    signal.signal(signal.SIGINT, exit_handler)
    pass



# EOF
