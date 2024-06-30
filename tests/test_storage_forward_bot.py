import os
import sys
import pytest
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from store_forward_bot import StoreForwardBot


@pytest.fixture
@patch("meshtastic.serial_interface.SerialInterface")
def bot(mock_interface):
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    return StoreForwardBot(mock_interface)


@pytest.fixture
def valid_packet():
    return {
        "decoded": {
            "portnum": "TEXT_MESSAGE_APP",
            "payload": b"Test message",
            "replyId": 1,
        },
        "id": 123,
        "from": 456,
        "to": 2,
        "channel": 0,
    }


@patch("store_forward_bot.add_message")
@patch("store_forward_bot.log_timestamp", return_value="[Timestamp] ")
def test_onReceive_valid_packet(
    mock_log_timestamp, mock_add_message, bot, valid_packet
):
    bot.onReceive(valid_packet, MagicMock())
    mock_add_message.assert_called_once_with(
        123, 456, "Unknown", "Unknown", 1, 0, "Test message"
    )


@patch("store_forward_bot.add_message")
@patch(
    "meshtastic.serial_interface.SerialInterface.getMyNodeInfo", return_value={"num": 1}
)
def test_onReceive_packet_not_for_bot(mock_add_message, bot, valid_packet):
    packet_not_for_bot = valid_packet.copy()
    # packet_not_for_bot["from"] = mock  # to myself so DM<
    bot.onReceive(packet_not_for_bot, MagicMock())
    mock_add_message.assert_not_called()


@patch("store_forward_bot.add_message")
def test_onReceive_invalid_portnum(mock_add_message, bot, valid_packet):
    invalid_packet = valid_packet.copy()
    invalid_packet["decoded"]["portnum"] = "INVALID_PORT"
    bot.onReceive(invalid_packet, MagicMock())
    mock_add_message.assert_not_called()
