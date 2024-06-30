import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basic_bot import BasicBot


@patch("meshtastic.serial_interface.SerialInterface")
def test_where_am_i_with_valid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = BasicBot(mock_interface)
    lat = "37.7749"
    lon = "-122.4194"

    location = bot.where_am_i(lat, lon)
    print(f"location: {location}")
    assert (
        location
        == "South Van Ness Avenue San Francisco California 94103 United States Grid: CM87ss"
    )
    assert location != bot.NO_DATA_NOGPS
    assert location != bot.ERROR_FETCHING_DATA


@patch("meshtastic.serial_interface.SerialInterface")
def test_auto_response_ping(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    bot = BasicBot(mock_interface)
    message = "ping"
    snr = 10
    rssi = -80
    hop = 2
    message_from_id = "123"
    location = [0, 0]

    response = bot.auto_response(message, snr, rssi, hop, message_from_id, location)

    assert response == "PONG, SNR:10 RSSI:-80 HOP 2"


@patch("meshtastic.serial_interface.SerialInterface")
def test_auto_response_ack(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = BasicBot(mock_interface)
    message = "ack"
    snr = 8
    rssi = -90
    hop = 1
    message_from_id = "456"
    location = [0, 0]

    response = bot.auto_response(message, snr, rssi, hop, message_from_id, location)

    assert response == "ACK-ACK! SNR:8 RSSI:-90 HOP 1"


@patch("meshtastic.serial_interface.SerialInterface")
def test_auto_response_lheard(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = BasicBot(mock_interface)
    message = "lheard"
    snr = 5
    rssi = -70
    hop = 3
    message_from_id = "789"
    location = [0, 0]

    response = bot.auto_response(message, snr, rssi, hop, message_from_id, location)

    assert response == "Last 5 nodes heard:\n"


@patch("meshtastic.serial_interface.SerialInterface")
def test_auto_response_whereami(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = BasicBot(mock_interface)
    message = "whereami"
    snr = 0
    rssi = 0
    hop = 0
    message_from_id = "987"
    location = [37.7749, -122.4194]

    response = bot.auto_response(message, snr, rssi, hop, message_from_id, location)

    assert (
        response
        == "South Van Ness Avenue San Francisco California 94103 United States Grid: CM87ss"
    )


@patch("meshtastic.serial_interface.SerialInterface")
def test_auto_response_joke(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = BasicBot(mock_interface)
    message = "joke"
    snr = 0
    rssi = 0
    hop = 0
    message_from_id = "654"
    location = [0, 0]

    response = bot.auto_response(message, snr, rssi, hop, message_from_id, location)

    assert response is not None
