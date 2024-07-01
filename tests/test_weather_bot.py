import os
import sys
from unittest.mock import patch, MagicMock

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather_bot import WeatherBot


@patch("meshtastic.serial_interface.SerialInterface")
def test_get_weather_with_valid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    bot = WeatherBot(mock_interface)
    # Test with valid coordinates
    lat = "37.7749"
    lon = "-122.4194"
    weather = bot.get_weather(lat, lon)
    print(f"weather: {weather}")
    assert weather != bot.NO_DATA_NOGPS
    assert weather != bot.ERROR_FETCHING_DATA
    # test replacement works
    assert "Sunday" not in weather
    assert "Monday" not in weather
    assert "Tuesday" not in weather
    assert "Wednesday" not in weather
    assert "Thursday" not in weather
    assert "Friday" not in weather
    assert "Saturday" not in weather
    assert "northwest" not in weather
    assert "northeast" not in weather
    assert "southwest" not in weather
    assert "southeast" not in weather
    assert "north" not in weather
    assert "south" not in weather
    assert "east" not in weather
    assert "west" not in weather
    assert "precipitation" not in weather
    assert "showers" not in weather
    assert "thunderstorms" not in weather


@patch("meshtastic.serial_interface.SerialInterface")
def test_get_weather_with_invalid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    # Test with invalid coordinates
    bot = WeatherBot(mock_interface)
    lat = 0
    lon = 0
    weather = bot.get_weather(lat, lon)
    print(f"weather: {weather}")
    assert weather == bot.NO_DATA_NOGPS


@patch("meshtastic.serial_interface.SerialInterface")
def test_get_tide_with_valid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    # Test with valid coordinates
    bot = WeatherBot(mock_interface)
    lat = "37.7749"
    lon = "-122.4194"
    tide = bot.get_tide(lat, lon)
    print(f"tide: {tide}")
    assert tide != bot.NO_DATA_NOGPS
    assert tide != bot.ERROR_FETCHING_DATA


@patch("meshtastic.serial_interface.SerialInterface")
def test_replace_weather(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    bot = WeatherBot(mock_interface)
    # Test replacing days of the week
    assert bot.replace_weather("Monday") == "Mon "
    assert bot.replace_weather("Tuesday") == "Tue "
    assert bot.replace_weather("Wednesday") == "Wed "
    assert bot.replace_weather("Thursday") == "Thu "
    assert bot.replace_weather("Friday") == "Fri "
    assert bot.replace_weather("Saturday") == "Sat "

    # Test replacing time periods
    assert bot.replace_weather("Today") == "Today "
    assert bot.replace_weather("Tonight") == "Tonight "
    assert bot.replace_weather("Tomorrow") == "Tomorrow "
    assert bot.replace_weather("This Afternoon") == "Afternoon "

    # Test replacing directions
    assert bot.replace_weather("northwest") == "NW"
    assert bot.replace_weather("northeast") == "NE"
    assert bot.replace_weather("southwest") == "SW"
    assert bot.replace_weather("southeast") == "SE"
    assert bot.replace_weather("north") == "N"
    assert bot.replace_weather("south") == "S"
    assert bot.replace_weather("east") == "E"
    assert bot.replace_weather("west") == "W"
    assert bot.replace_weather("Northwest") == "NW"
    assert bot.replace_weather("Northeast") == "NE"
    assert bot.replace_weather("Southwest") == "SW"
    assert bot.replace_weather("Southeast") == "SE"
    assert bot.replace_weather("North") == "N"
    assert bot.replace_weather("South") == "S"
    assert bot.replace_weather("East") == "E"
    assert bot.replace_weather("West") == "W"

    # Test replacing weather terms
    assert bot.replace_weather("precipitation") == "precip"
    assert bot.replace_weather("showers") == "shwrs"
    assert bot.replace_weather("thunderstorms") == "t-storms"


@patch("meshtastic.serial_interface.SerialInterface")
def test_get_moon_with_valid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    # Test with valid coordinates
    bot = WeatherBot(mock_interface)
    lat = "37.7749"
    lon = "-122.4194"
    moon = bot.get_moon(lat, lon)
    print(f"moon: {moon}")
    assert moon != bot.NO_DATA_NOGPS
    assert moon != bot.ERROR_FETCHING_DATA
    assert "Moon Rise" in moon
    assert "Set" in moon
    assert "Phase" in moon
    assert "Full Moon" in moon
    assert "New Moon" in moon


@patch("meshtastic.serial_interface.SerialInterface")
def test_solar_with_valid_coordinates(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    # Test with valid coordinates
    bot = WeatherBot(mock_interface)
    solar = bot.solar_conditions()
    print(f"solar: {solar}")
    assert solar != bot.NO_DATA_NOGPS
    assert solar != bot.ERROR_FETCHING_DATA
    assert "A-Index" in solar
    assert "K-Index" in solar
    assert "Sunspots" in solar
    assert "Solar Flux" in solar
    assert "X-Ray Flux" in solar
    assert "Signal Noise" in solar


@patch("meshtastic.serial_interface.SerialInterface")
def test_drap_xray_conditions(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface

    bot = WeatherBot(mock_interface)
    xray = bot.drap_xray_conditions()
    print(f"xray: {xray}")
    assert xray != bot.NO_DATA_NOGPS
    assert xray != bot.ERROR_FETCHING_DATA
    assert "X-ray" in xray


@patch("meshtastic.serial_interface.SerialInterface")
def test_get_hf_band_conditions(mock_interface):
    # Mock the SerialInterface to avoid actual serial communication
    mock_interface = MagicMock()
    mock_interface.return_value = mock_interface
    bot = WeatherBot(mock_interface)
    hf = bot.hf_band_conditions()
    print(f"hf: {hf}")
    assert hf != bot.NO_DATA_NOGPS
    assert hf != bot.ERROR_FETCHING_DATA
    # d80m-40m=Poor
    # d30m-20m=Poor
    # d17m-15m=Good
    # d12m-10m=Good
    # n80m-40m=Fair
    # n30m-20m=Good
    # n17m-15m=Good
    # n12m-10m=Poor
    assert "80m" in hf
    assert "40m" in hf
    assert "30m" in hf
    assert "20m" in hf
    assert "15m" in hf
    assert "10m" in hf
