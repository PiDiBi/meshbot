#!/usr/bin/env python3
# Meshtastic Autoresponder MESH Bot

import signal
import time
from typing import List
from pubsub import pub
from basic_bot import BasicBot
from db_operations import initialize_database
from message_processor import MessageProcessor
from serial_mesh import SerialMeshHelper

import meshtastic.serial_interface
import meshtastic.tcp_interface
import meshtastic.ble_interface

from store_forward_bot import StoreForwardBot
from weather_bot import WeatherBot

# Uncomment the interface you want to use depending on your device connection
interface = meshtastic.serial_interface.SerialInterface()  # serial interface
# interface=meshtastic.tcp_interface.TCPInterface(hostname="10.0.4.36") # IP of your device
# BLE interface - find it using meshtastic --ble-scan
# interface=meshtastic.ble_interface.BLEInterface("10:06:1C:49:90:36")

initialize_database()

bb = BasicBot(interface)
wb = WeatherBot(interface)
sfb = StoreForwardBot(interface)

# node_list = interface.nodes.values()
# print(f"System: Node List {node_list}")

message_processors: List[MessageProcessor] = [bb, wb, sfb]
sh = SerialMeshHelper(interface, message_processors)

# if not serial or serial.myNodeNum == -1:
#     print("System: Critical Error script abort. Could not get myNodeNum")
#     exit()


def exit_handler(signum, frame):
    print("\nSystem: Closing Autoresponder")
    if interface:
        interface.close()
    exit(0)


print("\nMeshtastic Autoresponder MESH Bot CTL+C to exit\n")

# subscribe to process messages
pub.subscribe(sh.onReceive, "meshtastic.receive")
# subscrie to store to DB
pub.subscribe(sfb.onReceive, "meshtastic.receive")

print(
    f"System: Autoresponder Started for device {MessageProcessor.get_name_from_number(interface, sh.myNodeNum)}"
)

while True:
    # Catch CTL+C to exit
    time.sleep(0.05)
    signal.signal(signal.SIGINT, exit_handler)
    time.sleep(0.05)
    pass

# EOF
