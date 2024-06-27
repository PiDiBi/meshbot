
import time
from typing import List
from log import log_timestamp

from meshtastic.stream_interface import StreamInterface
from meshtastic.serial_interface import SerialInterface
from meshtastic.tcp_interface import TCPInterface
import meshtastic.serial_interface
import meshtastic.tcp_interface
import meshtastic.ble_interface


from message_processor import MessageProcessor

RESPOND_BY_DM_ONLY = True # Set to True to respond messages via DM only (keeps the channel clean)

class SerialMeshHelper:

    interface: StreamInterface = None
    message_processors: List[MessageProcessor] = []
    trap_list = []
    myNodeNum = -1

    def __init__(self, interface: StreamInterface, message_processors: List[MessageProcessor]):

        self.interface = interface
        self.message_processors = message_processors

        for processor in self.message_processors:
            self.trap_list += processor.trap_list
        print(f"System: Traps are: {self.trap_list}")

        self.help_message = "Commands are: " + ", ".join(self.trap_list)
        self.MOTD = "Thanks for using MeshBOT! Have a good day!" # Message of the Day

        try:
            myinfo = self.interface.getMyNodeInfo()
            print(f"System: My Node Number is {myinfo}")
            self.myNodeNum = myinfo['num']
        except Exception as e:
            print(f"System: Critical Error script abort. {e}")
            exit()

    def get_node_location(self, number) -> list[float]:
        # Get the location of a node by its number from nodeDB on device
        latitude = 0
        longitude = 0
        position = [0,0]
        if self.interface.nodes:
            for node in self.interface.nodes.values():
                if number == node['num']:
                    if 'position' in node:
                        latitude = node['position']['latitude']
                        longitude = node['position']['longitude']
                        print (f"System: location data for {number} is {latitude},{longitude}")
                        position = [latitude, longitude]
                        return position
                    else:
                        print (f"{log_timestamp()} System: No location data for {number}")
                        return position
        else:
            print (f"{log_timestamp()} System: No nodes found")
            return position

    def onReceive(self, packet, interface):
        # receive a packet and process it, main instruction loop
        message_from_id = 0
        snr = 0
        rssi = 0
        try:
            if 'decoded' in packet and packet['decoded']['portnum'] == 'TEXT_MESSAGE_APP':
                # print the packet for debugging
                
                # print(" -- START of Packet --")
                # print(packet)
                # print(" -- END of packet -- \n")

                message_bytes = packet['decoded']['payload']
                message_string = message_bytes.decode('utf-8')
                message_from_id = packet['from']
                snr = packet['rxSnr']
                rssi = packet['rxRssi']

                if packet.get('channel'):
                    channel_number = packet['channel']
                else:
                    channel_number = 0
            
                # check if the packet has a hop count flag use it
                if packet.get('hopsAway'):
                    hop_away = packet['hopsAway']
                else:
                    # if the packet does not have a hop count try other methods
                    hop_away = 0
                    if packet.get('hopLimit'):
                        hop_limit = packet['hopLimit']
                    else:
                        hop_limit = 0
                    
                    if packet.get('hopStart'):
                        hop_start = packet['hopStart']
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
                        #print (f"calculated hop count: {hop_start} - {hop_limit} = {hop_count}")

                    hop = f"{hop_count} hops"

                wasHandled = False

                location:list[float] = self.get_node_location(message_from_id)

                response = None
                
                for processor in self.message_processors:
                    if processor.messageTrap(message_string):
                        response = processor.auto_response(message_string, snr, rssi, hop, message_from_id, location)
                    if response:
                        wasHandled = True
                        break

                if not response:
                    response = self.help_message

                # If the packet is a DM (Direct Message) respond to it, otherwise validate its a message for us
                print(f"{log_timestamp()} System: Received DM: {message_string} From: {self.get_name_from_number(message_from_id)}")
                print(f"{log_timestamp()} System: To: {packet['to']}")
                print(f"{log_timestamp()} System: My Node Number is {self.myNodeNum}")
                if packet['to'] == self.myNodeNum:
                    print(f"{log_timestamp()} Received DM: {message_string} on Channel: {channel_number} From: {self.get_name_from_number(message_from_id)}")
                    # respond with a direct message
                    self.send_message(response, channel_number, message_from_id)
                else:
                    if wasHandled:
                        print(f"{log_timestamp()} Received On Channel {channel_number}: {message_string} From: {self.get_name_from_number(message_from_id)}")
                        if RESPOND_BY_DM_ONLY:
                            # respond to channel message via direct message to keep the channel clean
                            self.send_message(response, channel_number, message_from_id)
                        else:
                            # or respond to channel message on the channel itself
                            self.send_message(response, channel_number, 0)
                    else:
                        print(f"{log_timestamp()} System: Ignoring incoming channel {channel_number}: {message_string} From: {self.get_name_from_number(message_from_id)}")
                
                # wait a 700ms to avoid message collision from lora-ack
                time.sleep(0.7)

        except KeyError as e:
            print(f"System: Error processing packet: {e}")
            print(packet) # print the packet for debugging
            print("END of packet \n")
            return str(e)

        pass

    def get_node_list(self):
        node_list = []
        short_node_list = []
        if self.interface.nodes:
            for node in self.interface.nodes.values():
                # ignore own
                if node['num'] != self.myNodeNum:
                    node_name = self.get_name_from_number(node['num'])
                    snr = node.get('snr', 0)

                    # issue where lastHeard is not always present
                    last_heard = node.get('lastHeard', 0)
                    
                    # make a list of nodes with last heard time and SNR
                    item = (node_name, last_heard, snr)
                    node_list.append(item)
            
            node_list.sort(key=lambda x: x[1], reverse=True)
            #print (f"Node List: {node_list[:5]}\n")

            # make a nice list for the user
            for x in node_list[:5]:
                short_node_list.append(f"{x[0]} SNR:{x[2]}")

            return "\n".join(short_node_list)
        
        else:
            return "Error Processing Node List"
                
    def send_message(self, message, ch, nodeid):
        # if message over 160 characters, split it into multiple messages
        if len(message) > 160:
            #message_list = [message[i:i+160] for i in range(0, len(message), 160)]
            # smarter word split
            split_message = message.split()
            line = ''
            split_len = 160
            message_list = []
            for word in split_message:
                if len(line+word)<split_len:
                    line += word + ' '
                else:
                    message_list.append(line)
                    line = word + ' '
            message_list.append(line) # needed add contents of the last 'line' into the list

            for m in message_list:
                if nodeid == 0:
                    #Send to channel
                    print (f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: Channel:{ch}")
                    self.interface.sendText(text=m, channelIndex=ch)
                else:
                    # Send to DM
                    print (f"{log_timestamp()} System: Sending Multi-Chunk: {m} To: {self.get_name_from_number(nodeid)}")
                    self.interface.sendText(text=m,channelIndex=ch, destinationId=nodeid)
                # # wait a 500ms to avoid message collision except after last message
                # if message_list.index(m) < len(message_list) - 1:
                #     time.sleep(0.5)
        else: # message is less than 160 characters
            if nodeid == 0:
                # Send to channel
                print (f"{log_timestamp()} System: Sending: {message} To: Channel:{ch}")
                self.interface.sendText(text=message, channelIndex=ch)
            else:
                # Send to DM
                print (f"{log_timestamp()} System: Sending: {message} To: {self.get_name_from_number(nodeid)}")
                self.interface.sendText(text=message, channelIndex=ch, destinationId=nodeid)

    def get_name_from_number(self, number, type='long'):
        name = ""
        for node in self.interface.nodes.values():
            if number == node['num']:
                if type == 'long':
                    name = node['user']['longName']
                    return name
                elif type == 'short':
                    name = node['user']['shortName']
                    return name
                else:
                    pass
            else:
                name =  str(self.decimal_to_hex(number))  # If long name not found, use the ID as string
        return name

    def decimal_to_hex(self, decimal_number):
        return f"!{decimal_number:08x}"

    
        

