from meshtastic.stream_interface import StreamInterface
from message_processor import MessageProcessor
from geopy.geocoders import Nominatim
import maidenhead as mh
from dadjokes import Dadjoke


class BasicBot(MessageProcessor):
    def __init__(self, interface: StreamInterface):
        super(BasicBot, self).__init__(interface)
        self.trap_list = ["ping", "ack", "lheard", "sitrep", "joke", "whereami"]
        pass

    def auto_response(
        self, message, snr, rssi, hop, message_from_id, location: list[float]
    ):
        bot_response = None
        message = message.lower().strip()
        if "ping" in message:
            # Check if the user added @foo to the message
            bot_response = "PONG, " + f"SNR:{snr} RSSI:{rssi} HOP {hop}"
            if " " in message:
                bot_response += " and copy: " + message.split(" ")[1]

        elif "ack" in message:
            bot_response = "ACK-ACK! " + f"SNR:{snr} RSSI:{rssi} HOP {hop}"
            if " " in message:
                bot_response += " and copy: " + message.split(" ")[1]

        elif "lheard" in message or "sitrep" in message:
            # make a nice list for the user
            if not self.node_list:
                return "Error Processing Node List"

            short_node_list = self.get_node_list()

            node_list = []
            for x in short_node_list:
                node_list.append(f"{x[0]} [SNR:{x[2]}]")

            bot_response = "Last 5 nodes heard:\n" + str("\n".join(node_list))

        elif "whereami" in message:
            bot_response = self.where_am_i(location[0], location[1])

        elif "joke" in message:
            bot_response = self.tell_joke()

        return bot_response

    def tell_joke(self):
        dadjoke = Dadjoke()
        return dadjoke.joke

    def where_am_i(self, lat=0, lon=0):
        whereIam = ""
        if float(lat) == 0 and float(lon) == 0:
            return self.NO_DATA_NOGPS

        geolocator = Nominatim(user_agent="mesh-bot")

        location = geolocator.reverse(str(lat) + ", " + str(lon))
        address = location.raw["address"]
        address_components = [
            "house_number",
            "road",
            "city",
            "state",
            "postcode",
            "county",
            "country",
        ]
        whereIam += " ".join(
            [
                address.get(component, "")
                for component in address_components
                if component in address
            ]
        )
        grid = mh.to_maiden(float(lat), float(lon))
        whereIam += " Grid: " + grid

        return whereIam

    def get_node_list(self, limit=5):

        result = []

        for index, node in enumerate(self.node_list):
            # ignore own
            if node["num"] == self.myNodeNum:
                continue

            node_name = MessageProcessor.get_name_from_number(
                self.interface, node["num"]
            )
            snr = node.get("snr", 0)

            # issue where lastHeard is not always present
            last_heard = node.get("lastHeard", 0)

            # make a list of nodes with last heard time and SNR
            item = (node_name, last_heard, snr)
            result.append(item)

            if index >= limit:
                break

        result.sort(key=lambda x: x[1], reverse=True)

        return result
