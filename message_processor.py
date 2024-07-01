import time
from typing import Dict
from meshtastic.stream_interface import StreamInterface


class MessageProcessor:
    URL_TIMEOUT = 10  # wait time for URL requests
    NO_DATA_NOGPS = "No GPS data available"
    ERROR_FETCHING_DATA = "error fetching data"
    LATITUDE: float = 48.50
    LONGITUDE: float = -123.0
    node_list: Dict[str, Dict] = {}

    def __init__(self, interface: StreamInterface):
        self.interface = interface
        self.trap_list = []
        self.node_list = interface.nodes.values()
        # print(f"System: Node List {self.node_list}")
        self.myNodeNum = interface.getMyNodeInfo()["num"]
        pass

    def auto_response(
        self, message, snr, rssi, hop, message_from_id, location: list[float]
    ):
        # wait a 700ms to avoid message collision from lora-ack
        time.sleep(0.7)
        pass

    def messageTrap(self, msg):
        # Check if the message contains a trap word
        message_list = msg.split(" ")
        for m in message_list:
            for t in self.trap_list:
                if t.lower() == m.lower():
                    return True
        return False

    @staticmethod
    def get_name_from_number(interface: StreamInterface, number, type="long"):
        name = ""
        for node in interface.nodes.values():
            if number == node["num"]:
                if type == "long":
                    name = node["user"]["longName"]
                    return name
                elif type == "short":
                    name = node["user"]["shortName"]
                    return name
                else:
                    pass
            else:
                name = str(
                    MessageProcessor.decimal_to_hex(number)
                )  # If long name not found, use the ID as string
        return name

    @staticmethod
    def decimal_to_hex(decimal_number):
        return f"!{decimal_number:08x}"
