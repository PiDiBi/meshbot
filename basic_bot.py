from message_processor import MessageProcessor
from geopy.geocoders import Nominatim
import maidenhead as mh
from dadjokes import Dadjoke

class BasicBot(MessageProcessor):
    def __init__(self):
        super().__init__()
        self.trap_list = ["ping", "ack", "testing", "pong", "lheard", "sitrep", "joke"]
        pass
    
    def auto_response(self, message, snr, rssi, hop, message_from_id, location:list[float], node_list:list[str]):
        print(f"BasicBot: Got message: {message}")

        message = message.lower().strip()
        if "ping" in message:
            #Check if the user added @foo to the message
            bot_response = "PONG, " + f"SNR:{snr} RSSI:{rssi} HOP {hop}"
            if " " in message:
                bot_response += " and copy: " + message.split(" ")[1]

        elif "ack" in message:
            bot_response = "ACK-ACK! " + f"SNR:{snr} RSSI:{rssi} HOP {hop}"
            if " " in message:
                bot_response += " and copy: " + message.split(" ")[1]

        elif "lheard" in message or "sitrep" in message:
            # make a nice list for the user
            short_node_list = []
            for x in node_list[:5]:
                short_node_list.append(f"{x[0]} SNR:{x[2]}")

            bot_response = "Last 5 nodes heard:\n" + str("\n".join(short_node_list))

        elif "whereami" in message:
            bot_response = self.where_am_i(location[0], location[1])
            
        elif "joke" in message:
            bot_response = self.tell_joke()
        
        return bot_response

    def tell_joke(self):
    # tell a dad joke, does it need an explanationn :)
        dadjoke = Dadjoke()
        return dadjoke.joke
    
    def where_am_i(self, lat=0, lon=0):
        whereIam = ""
        if float(lat) == 0 and float(lon) == 0:
            return super().NO_DATA_NOGPS
        # initialize Nominatim API
        geolocator = Nominatim(user_agent="mesh-bot")

        location = geolocator.reverse(lat + ", " + lon)
        address = location.raw['address']
        address_components = ['house_number', 'road', 'city', 'state', 'postcode', 'county', 'country']
        whereIam += ' '.join([address.get(component, '') for component in address_components if component in address])
        grid = mh.to_maiden(float(lat), float(lon))
        whereIam += " Grid: " + grid

        return whereIam