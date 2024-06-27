import unittest
import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from weather_bot import *

class TestGetWeather(unittest.TestCase):

    def test_get_weather_with_valid_coordinates(self):
        bot = WeatherBot()
        # Test with valid coordinates
        lat = "37.7749"
        lon = "-122.4194"
        weather = bot.get_weather(lat, lon)
        print(f"weather: {weather}")
        self.assertNotEqual(weather, bot.NO_DATA_NOGPS)
        self.assertNotEqual(weather, bot.ERROR_FETCHING_DATA)
        # test replacement works
        self.assertNotIn(weather, "Sunday")
        self.assertNotIn(weather, "Monday")
        self.assertNotIn(weather, "Tuesday")
        self.assertNotIn(weather, "Wednesday")
        self.assertNotIn(weather, "Thursday")
        self.assertNotIn(weather, "Friday")
        self.assertNotIn(weather, "Saturday")
        self.assertNotIn(weather, "northwest")
        self.assertNotIn(weather, "northeast")
        self.assertNotIn(weather, "southwest")
        self.assertNotIn(weather, "southeast")
        self.assertNotIn(weather, "north")
        self.assertNotIn(weather, "south")
        self.assertNotIn(weather, "east")
        self.assertNotIn(weather, "west")
        self.assertNotIn(weather, "precipitation")
        self.assertNotIn(weather, "showers")
        self.assertNotIn(weather, "thunderstorms")
        
    def test_get_weather_with_invalid_coordinates(self):
        # Test with invalid coordinates
        bot = WeatherBot()
        lat = 0
        lon = 0
        weather = bot.get_weather(lat, lon)
        print(f"weather: {weather}")
        self.assertEqual(weather, bot.NO_DATA_NOGPS)

    def test_get_tide_with_valid_coordinates(self):
        # Test with valid coordinates
        bot = WeatherBot()
        lat = "37.7749"
        lon = "-122.4194"
        tide = bot.get_tide(lat, lon)
        print(f"tide: {tide}")
        self.assertNotEqual(tide, bot.NO_DATA_NOGPS)
        self.assertNotEqual(tide, bot.ERROR_FETCHING_DATA)

    def test_replace_weather(self):
        bot = WeatherBot()
        # Test replacing days of the week
        self.assertEqual(bot.replace_weather("Monday"), "Mon ")
        self.assertEqual(bot.replace_weather("Tuesday"), "Tue ")
        self.assertEqual(bot.replace_weather("Wednesday"), "Wed ")
        self.assertEqual(bot.replace_weather("Thursday"), "Thu ")
        self.assertEqual(bot.replace_weather("Friday"), "Fri ")
        self.assertEqual(bot.replace_weather("Saturday"), "Sat ")
        
        # Test replacing time periods
        self.assertEqual(bot.replace_weather("Today"), "Today ")
        self.assertEqual(bot.replace_weather("Tonight"), "Tonight ")
        self.assertEqual(bot.replace_weather("Tomorrow"), "Tomorrow ")
        self.assertEqual(bot.replace_weather("This Afternoon"), "Afternoon ")
        
        # Test replacing directions
        self.assertEqual(bot.replace_weather("northwest"), "NW")
        self.assertEqual(bot.replace_weather("northeast"), "NE")
        self.assertEqual(bot.replace_weather("southwest"), "SW")
        self.assertEqual(bot.replace_weather("southeast"), "SE")
        self.assertEqual(bot.replace_weather("north"), "N")
        self.assertEqual(bot.replace_weather("south"), "S")
        self.assertEqual(bot.replace_weather("east"), "E")
        self.assertEqual(bot.replace_weather("west"), "W")
        self.assertEqual(bot.replace_weather("Northwest"), "NW")
        self.assertEqual(bot.replace_weather("Northeast"), "NE")
        self.assertEqual(bot.replace_weather("Southwest"), "SW")
        self.assertEqual(bot.replace_weather("Southeast"), "SE")
        self.assertEqual(bot.replace_weather("North"), "N")
        self.assertEqual(bot.replace_weather("South"), "S")
        self.assertEqual(bot.replace_weather("East"), "E")
        self.assertEqual(bot.replace_weather("West"), "W")
        
        # Test replacing weather terms
        self.assertEqual(bot.replace_weather("precipitation"), "precip")
        self.assertEqual(bot.replace_weather("showers"), "shwrs")
        self.assertEqual(bot.replace_weather("thunderstorms"), "t-storms")


if __name__ == '__main__':
    unittest.main()