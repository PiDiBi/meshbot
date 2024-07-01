from meshtastic.stream_interface import StreamInterface
from db_operations import add_message, get_messages
from log import log_timestamp
from message_processor import MessageProcessor


class StoreForwardBot(MessageProcessor):
    def __init__(
        self, interface: StreamInterface
    ):  # myNodeNum:int, node_list:Dict[str, Dict]):
        super(StoreForwardBot, self).__init__(interface)
        self.trap_list = ["messages"]
        pass

    def auto_response(self, message, snr, rssi, hop, sender_id, location: list[float]):

        message = message.lower().strip()
        if "messages" in message:
            # Check if the user added @foo to the message
            messages = get_messages(5)
            print(f"{log_timestamp()}SFBot: Messages {messages}")
            # format messages to be more readable
            messages_nice = []
            print(f"{log_timestamp()}SFBot: Messages {messages}")
            for m in messages:
                messages_nice.append(f"[{m[3]}] {m[2]}: {m[5]}")
            if messages:
                bot_response = "Last 5 messages:\n" + str("\n".join(messages_nice))
            else:
                bot_response = "No messages found"

        return bot_response

    def onReceive(self, packet, interface):
        sender_id = 0
        channel_number = 0
        shortName = "Unknown"
        longName = "Unknown"
        reply_id = 0

        try:
            if (
                "decoded" not in packet
                or not packet["decoded"]["portnum"] == "TEXT_MESSAGE_APP"
            ):
                return

            # print(f"SFBot: START packet:")
            # print(packet)  # print the packet for debugging
            # print("SFBot: END of packet \n")

            message_string = packet["decoded"]["payload"].decode("utf-8")

            if packet["decoded"].get("replyId"):
                reply_id = packet["decoded"]["replyId"]

            message_id = packet["id"]

            if packet.get("channel"):
                channel_number = packet["channel"]

            sender_id = packet["from"]

            for node in interface.nodes.values():
                if sender_id == node["num"]:
                    longName = node["user"]["longName"]
                    shortName = node["user"]["shortName"]

            print(
                f"{log_timestamp()}SFBot: Message #{message_id} received from {longName}:{shortName} "
                f"as reply to #{reply_id} on channel {channel_number}: {message_string}"
            )

            if packet["to"] == self.myNodeNum:
                print(
                    f"{log_timestamp()}SFBot: Direct Message received for me, ignoring: {message_string}"
                )
                return

            if channel_number != 0:
                print(
                    f"{log_timestamp()}SFBot: ingoring channel other then 0: {message_string}"
                )
                return

            # add to database
            add_message(
                message_id,
                sender_id,
                shortName,
                longName,
                reply_id,
                channel_number,
                message_string,
            )
            print(f"{log_timestamp()}SFBot: Message added to database")

        except KeyError as e:
            print(f"SFBot: Error processing packet: {e}")
            print(packet)  # print the packet for debugging
            print("END of packet \n")
            return str(e)
