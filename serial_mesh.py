import time
from typing import List
from log import log_timestamp
from meshtastic.stream_interface import StreamInterface
from message_processor import MessageProcessor

RESPOND_BY_DM_ONLY = (
    True  # Set to True to respond messages via DM only (keeps the channel clean)
)


class SerialMeshHelper:

    interface: StreamInterface = None
    message_processors: List[MessageProcessor] = []
    trap_list = []
    myNodeNum = -1

    def __init__(
        self, interface: StreamInterface, message_processors: List[MessageProcessor]
    ):

        self.interface = interface
        self.message_processors = message_processors

        for processor in self.message_processors:
            self.trap_list += processor.trap_list
        print(f"System: Traps are: {self.trap_list}")

        self.help_message = "Commands are: " + ", ".join(self.trap_list)
        self.MOTD = "Thanks for using MeshBOT! Have a good day!"  # Message of the Day

        try:
            myinfo = self.interface.getMyNodeInfo()
            print(f"System: My Node Number is {myinfo}")
            self.myNodeNum = myinfo["num"]
        except Exception as e:
            print(f"System: Critical Error script abort. {e}")
            exit()

    def get_node_location(self, number) -> list[float]:
        # Get the location of a node by its number from nodeDB on device
        latitude = 0
        longitude = 0
        position = [0, 0]
        if self.interface.nodes:
            for node in self.interface.nodes.values():
                if number == node["num"]:
                    if "position" in node:
                        latitude = node["position"]["latitude"]
                        longitude = node["position"]["longitude"]
                        print(
                            f"System: location data for {number} is {latitude},{longitude}"
                        )
                        position = [latitude, longitude]
                        return position
                    else:
                        print(
                            f"{log_timestamp()} System: No location data for {number}"
                        )
                        return position
        else:
            print(f"{log_timestamp()} System: No nodes found")
            return position

    def onReceive(self, packet, interface):
        # receive a packet and process it, main instruction loop
        message_from_id = 0
        snr = 0
        rssi = 0
        channel_number = 0
        try:
            if (
                "decoded" not in packet
                or not packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP"
            ):
                return
            # print the packet for debugging

            # print(" -- START of Packet --")
            # print(packet)
            # print(" -- END of packet -- \n")

            message_string = packet["decoded"]["payload"].decode("utf-8")
            message_from_id = packet["from"]

            try:
                snr = packet["rxSnr"]
                rssi = packet["rxRssi"]
            except KeyError:
                pass

            if message_string == "SF":
                print(
                    "{log_timestamp()} System: Ignoring SF (Store and Forward msg) From: "
                    f"{MessageProcessor.get_name_from_number(interface, message_from_id)}"
                )
                return

            if packet.get("channel"):
                channel_number = packet["channel"]

            # check if the packet has a hop count flag use it
            if packet.get("hopsAway"):
                hop_away = packet["hopsAway"]
            else:
                # if the packet does not have a hop count try other methods
                hop_away = 0
                if packet.get("hopLimit"):
                    hop_limit = packet["hopLimit"]
                else:
                    hop_limit = 0

                if packet.get("hopStart"):
                    hop_start = packet["hopStart"]
                else:
                    hop_start = 0

            if hop_start == hop_limit:
                hop = "Direct"
            else:
                # set hop to Direct if the message was sent directly otherwise set the hop count
                if hop_away > 0:
                    hop_count = hop_away
                else:
                    hop_count = hop_start - hop_limit
                    # print (f"calculated hop count: {hop_start} - {hop_limit} = {hop_count}")

                hop = f"{hop_count} hops"

            wasHandled = False

            location: list[float] = self.get_node_location(message_from_id)

            response = None

            for processor in self.message_processors:
                if processor.messageTrap(message_string):
                    response = processor.auto_response(
                        message_string,
                        snr,
                        rssi,
                        hop,
                        message_from_id,
                        location,
                    )
                if response:
                    wasHandled = True
                    break

            if not response:
                response = self.help_message

            from_name = MessageProcessor.get_name_from_number(
                interface, message_from_id
            )
            # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us
            print(
                f"{log_timestamp()} System: Received DM: {message_string} From: {from_name}"
            )
            print(f"{log_timestamp()} System: To: {packet['to']}")
            print(f"{log_timestamp()} System: My Node Number is {self.myNodeNum}")
            if packet["to"] == self.myNodeNum:
                print(
                    f"{log_timestamp()} Received DM: '{message_string}' on Channel: {channel_number} From: {from_name}"
                )
                # respond with a direct message
                self.send_message(response, channel_number, message_from_id)
            else:
                if wasHandled:
                    print(
                        f"{log_timestamp()} Received On Channel {channel_number}: '{message_string}' From: {from_name}"
                    )
                    if RESPOND_BY_DM_ONLY:
                        # respond to channel message via direct message to keep the channel clean
                        self.send_message(response, channel_number, message_from_id)
                    else:
                        # or respond to channel message on the channel itself
                        self.send_message(response, channel_number, 0)
                else:
                    print(
                        f"{log_timestamp()} System: Ignoring incoming channel "
                        f"{channel_number}: '{message_string}' From: {from_name}"
                    )

            # wait a 700ms to avoid message collision from lora-ack
            time.sleep(0.7)

        except KeyError as e:
            print(f"System: Error processing packet: {e}")
            print(packet)  # print the packet for debugging
            print("END of packet \n")
            return str(e)

        pass

    def send_message(self, message, ch, nodeid):
        message_list = []
        # if message over 160 characters, split it into multiple messages
        if len(message) > 160:
            # message_list = [message[i:i+160] for i in range(0, len(message), 160)]
            # smarter word split
            if "\n" in message:
                split_message = message.split("\n")
                for line in split_message:
                    if len(line) > 160:
                        line = line[:160]

                    message_list.append(line)
            else:
                split_message = message.split(" ")
                line = ""
                split_len = 160
                message_list = []
                for word in split_message:
                    if len(line + word) < split_len:
                        line += word + " "
                    else:
                        message_list.append(line)
                        line = word + " "
                message_list.append(
                    line
                )  # needed add contents of the last 'line' into the list

            for m in message_list:
                if nodeid == 0:
                    # Send to channel
                    print(
                        f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: Channel:{ch}"
                    )
                    self.interface.sendText(text=m, channelIndex=ch)
                else:
                    # Send to DM
                    print(
                        f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: "
                        f"{MessageProcessor.get_name_from_number(self.interface, nodeid)}"
                    )
                    self.interface.sendText(
                        text=m, channelIndex=ch, destinationId=nodeid
                    )
                # # wait a 500ms to avoid message collision except after last message
                # if message_list.index(m) < len(message_list) - 1:
                #     time.sleep(0.5)
        else:  # message is less than 160 characters
            if nodeid == 0:
                # Send to channel
                print(f"{log_timestamp()} System: Sending: {message} To: Channel:{ch}")
                self.interface.sendText(text=message, channelIndex=ch)
            else:
                # Send to DM
                print(
                    f"{log_timestamp()} System: Sending: {message} To: "
                    f"{MessageProcessor.get_name_from_number(self.interface, nodeid)}"
                )
                self.interface.sendText(
                    text=message, channelIndex=ch, destinationId=nodeid
                )
