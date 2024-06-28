import time

class MessageProcessor:
  URL_TIMEOUT = 10 # wait time for URL requests
  NO_DATA_NOGPS = "No GPS data available"
  ERROR_FETCHING_DATA = "error fetching data"
  LATITUDE:float = 48.50
  LONGITUDE:float = -123.0

  def __init__(self):
    self.trap_list = []
    pass
  
  def auto_response(self, message, snr, rssi, hop, message_from_id, location:list[float], node_list:list[str]):
    # wait a 700ms to avoid message collision from lora-ack
    time.sleep(0.7)
    pass

  def messageTrap(self, msg):
        # Check if the message contains a trap word
        message_list=msg.split(" ")
        for m in message_list:
            for t in self.trap_list:
                if t.lower() == m.lower():
                    return True
        return False