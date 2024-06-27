import os
import sys
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from basic_bot import BasicBot

class TestGetWeather(unittest.TestCase):

    def test_where_am_i_with_valid_coordinates(self):
        # Test with invalid coordinates
        bot = BasicBot()
        lat = "37.7749"
        lon = "-122.4194"
        location = bot.where_am_i(lat, lon)
        print(f"location: {location}")
        self.assertEqual(location, "South Van Ness Avenue San Francisco California 94103 United States Grid: CM87ss")
        self.assertNotEqual(location, bot.NO_DATA_NOGPS)
        self.assertNotEqual(location, bot.ERROR_FETCHING_DATA)

if __name__ == '__main__':
    unittest.main()