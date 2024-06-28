import os
import sys
import pytest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from basic_bot import BasicBot

def test_where_am_i_with_valid_coordinates():
    # Test with invalid coordinates
    bot = BasicBot()
    lat = "37.7749"
    lon = "-122.4194"
    location = bot.where_am_i(lat, lon)
    print(f"location: {location}")
    assert location == "South Van Ness Avenue San Francisco California 94103 United States Grid: CM87ss"
    assert location != bot.NO_DATA_NOGPS
    assert location != bot.ERROR_FETCHING_DATA
