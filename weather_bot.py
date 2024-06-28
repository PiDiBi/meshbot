import json
import requests
import xml.dom.minidom
import ephem
import bs4 as bs
from datetime import datetime
from datetime import timedelta

from log import log_timestamp
from message_processor import MessageProcessor


class WeatherBot(MessageProcessor):
    
    DAYS_OF_WEATHER = 2 # weather forecast days, the first two rows are today and tonight

    def __init__(self):
        super().__init__()
        self.trap_list = ["sun", "solar", "hfcond", "tide", "moon", "wxc", "wx"]
        pass
    
    def auto_response(self, message, snr, rssi, hop, message_from_id, location:list[float]):
        print(f"WeatherBot: Got message: {message}")

        message = message.lower()

        if "sun" in message:
            bot_response = self.get_sun(str(location[0]), str(location[1]))
        elif "hfcond" in message:
            bot_response = self.hf_band_conditions()
        elif "solar" in message:
            bot_response = self.drap_xray_conditions() + "\n" + self.solar_conditions()
        elif "tide" in message:
            bot_response = self.get_tide(str(location[0]), str(location[1]))
        elif "moon" in message:
            bot_response = self.get_moon(str(location[0]), str(location[1]))
        elif "wxc" in message:
            bot_response = self.get_weather(str(location[0]), str(location[1]),1)
        elif "wx" in message:
            bot_response = self.get_weather(str(location[0]), str(location[1]))
        
        return bot_response

    def hf_band_conditions(self):
        # ham radio HF band conditions
        hf_cond = ""
        band_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=super().URL_TIMEOUT)
        print (f"{log_timestamp()} System: {band_cond}")

        if(band_cond.ok):
            solarxml = xml.dom.minidom.parseString(band_cond.text)
            for i in solarxml.getElementsByTagName("band"):
                hf_cond += i.getAttribute("time")[0]+i.getAttribute("name") +"="+str(i.childNodes[0].data)+"\n"
        else:
            hf_cond += "error fetching"
        hf_cond = hf_cond[:-1] # remove the last newline
        return hf_cond

    def solar_conditions(self):
        # radio related solar conditions from hamsql.com
        solar_cond = ""
        solar_cond = requests.get("https://www.hamqsl.com/solarxml.php", timeout=super().URL_TIMEOUT)
        print (f"{log_timestamp()} System: {solar_cond}")

        if(solar_cond.ok):
            solar_xml = xml.dom.minidom.parseString(solar_cond.text)
            for i in solar_xml.getElementsByTagName("solardata"):
                solar_a_index = i.getElementsByTagName("aindex")[0].childNodes[0].data
                solar_k_index = i.getElementsByTagName("kindex")[0].childNodes[0].data
                solar_xray = i.getElementsByTagName("xray")[0].childNodes[0].data
                solar_flux = i.getElementsByTagName("solarflux")[0].childNodes[0].data
                sunspots = i.getElementsByTagName("sunspots")[0].childNodes[0].data
                signalnoise = i.getElementsByTagName("signalnoise")[0].childNodes[0].data
            solar_cond = "A-Index: " + solar_a_index + "\nK-Index: " + solar_k_index + "\nSunspots: " + sunspots + "\nX-Ray Flux: " + solar_xray + "\nSolar Flux: " + solar_flux + "\nSignal Noise: " + signalnoise
        else:
            solar_cond += "error fetching"
        return solar_cond

    def drap_xray_conditions(self):
        # DRAP X-ray flux conditions, from NOAA direct
        drap_cond = ""
        drap_cond = requests.get("https://services.swpc.noaa.gov/text/drap_global_frequencies.txt", timeout=super().URL_TIMEOUT)
        print (f"{log_timestamp()} System: {drap_cond}")

        if(drap_cond.ok):
            drap_list = drap_cond.text.split('\n')
            x_filter = '#  X-RAY Message :'
            for line in drap_list:
                if x_filter in line:
                    xray_flux = line.split(": ")[1]
        else:
            xray_flux += "error fetching"
        return xray_flux

    def get_sun(self, lat=0, lon=0):
        # get sunrise and sunset times using callers location or default
        obs = ephem.Observer()
        obs.date = datetime.now()
        sun = ephem.Sun()
        if lat != 0 and lon != 0:
            obs.lat = str(lat)
            obs.lon = str(lon)
        else:
            obs.lat = str(super().LATITUDE)
            obs.lon = str(super().LONGITUDE)

        sun.compute(obs)
        sun_table = {}
        sun_table['azimuth'] = sun.az
        sun_table['altitude'] = sun.alt

        # get the next rise and set times
        local_sunrise = ephem.localtime(obs.next_rising(sun))
        local_sunset = ephem.localtime(obs.next_setting(sun))
        sun_table['rise_time'] = local_sunrise.strftime('%a %d %I:%M')
        sun_table['set_time'] = local_sunset.strftime('%a %d %I:%M')
        # if sunset is before sunrise, then it's tomorrow
        if local_sunset < local_sunrise:
            local_sunset = ephem.localtime(obs.next_setting(sun)) + timedelta(1)
            sun_table['set_time'] = local_sunset.strftime('%a %d %I:%M')
        sun_data = "Sun Rise: " + sun_table['rise_time'] + "\nSet: " + sun_table['set_time']
        
        return sun_data

    def get_moon(self, lat=0, lon=0):
        # get moon phase and rise/set times using callers location or default
        # the phase calculation mght not be accurate (followup later)
        obs = ephem.Observer()
        moon = ephem.Moon()
        if lat != 0 and lon != 0:
            obs.lat = str(lat)
            obs.lon = str(lon)
        else:
            obs.lat = str(super().LATITUDE)
            obs.lon = str(super().LONGITUDE)
        
        obs.date = datetime.now()
        moon.compute(obs)
        moon_table = {}
        moon_phase = ['New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous', 'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'][round(moon.phase / (2 * ephem.pi) * 8) % 8]
        moon_table['phase'] = moon_phase
        moon_table['illumination'] = moon.phase
        moon_table['azimuth'] = moon.az
        moon_table['altitude'] = moon.alt

        local_moonrise = ephem.localtime(obs.next_rising(moon))
        local_moonset = ephem.localtime(obs.next_setting(moon))
        moon_table['rise_time'] = local_moonrise.strftime('%a %d %I:%M%p')
        moon_table['set_time'] = local_moonset.strftime('%a %d %I:%M%p')

        local_next_full_moon = ephem.localtime(ephem.next_full_moon((obs.date)))
        local_next_new_moon = ephem.localtime(ephem.next_new_moon((obs.date)))
        moon_table['next_full_moon'] = local_next_full_moon.strftime('%a %b %d %I:%M%p')
        moon_table['next_new_moon'] = local_next_new_moon.strftime('%a %b %d %I:%M%p')

        moon_data = "Moon Rise:" + moon_table['rise_time'] + "\nSet:" + moon_table['set_time'] + \
            "\nPhase:" + moon_table['phase'] + " @:" + str('{0:.2f}'.format(moon_table['illumination'])) + "%" \
            + "\nFull Moon:" + moon_table['next_full_moon'] + "\nNew Moon:" + moon_table['next_new_moon']
        
        return moon_data

    def get_tide(self, lat=0, lon=0):
        station_id = ""
        if float(lat) == 0 and float(lon) == 0:
            return super().NO_DATA_NOGPS
        station_lookup_url = "https://api.tidesandcurrents.noaa.gov/mdapi/prod/webapi/tidepredstations.json?lat=" + str(lat) + "&lon=" + str(lon) + "&radius=50"
        print (f"{log_timestamp()} System: {station_lookup_url}")

        try:
            station_data = requests.get(station_lookup_url, timeout=super().URL_TIMEOUT)
            if station_data.ok:
                station_json = station_data.json()
            else:
                return super().ERROR_FETCHING_DATA
        except (requests.exceptions.RequestException, json.JSONDecodeError):
            return super().ERROR_FETCHING_DATA

        if station_id is None:
                return "no tide station found"
        
        station_id = station_json['stationList'][0]['stationId']

        station_url = "https://tidesandcurrents.noaa.gov/noaatidepredictions.html?id=" + station_id
        print (f"{log_timestamp()} System: {station_url}")

        try:
            station_data = requests.get(station_url, timeout=super().URL_TIMEOUT)
            if not station_data.ok:
                return super().ERROR_FETCHING_DATA
        except (requests.exceptions.RequestException):
            return super().ERROR_FETCHING_DATA
        
        # extract table class="table table-condensed"
        soup = bs.BeautifulSoup(station_data.text, 'html.parser')
        table = soup.find('table', class_='table table-condensed')

        # extract rows
        rows = table.find_all('tr')
        # extract data from rows
        tide_data = []
        for row in rows:
            row_text = ""
            cols = row.find_all('td')
            for col in cols:
                row_text += col.text + " "
            tide_data.append(row_text)
        # format tide data into a string
        tide_string = ""
        for data in tide_data:
            tide_string += data + "\n"
        # trim off last newline
        tide_string = tide_string[:-1]
        return tide_string
        
    def get_weather(self, lat=0, lon=0, unit=0):
        weather = ""
        if float(lat) == 0 and float(lon) == 0:
            return super().NO_DATA_NOGPS
        
        weather_url = "https://forecast.weather.gov/MapClick.php?FcstType=text&lat=" + str(lat) + "&lon=" + str(lon)

        if unit == 1:
            weather_url += "&unit=1"

        print (f"{log_timestamp()} System: {weather_url}")
        
        try:
            weather_data = requests.get(weather_url, timeout=super().URL_TIMEOUT)
            if not weather_data.ok:
                return super().ERROR_FETCHING_DATA
        except (requests.exceptions.RequestException):
            return super().ERROR_FETCHING_DATA
        

        soup = bs.BeautifulSoup(weather_data.text, 'html.parser')
        table = soup.find('div', id="detailed-forecast-body")

        if table is None:
            return "no weather data found on NOAA for your location"
        else:
            # get rows
            rows = table.find_all('div', class_="row")
        
        # extract data from rows
        for row in rows:
            # shrink the text
            line = self.replace_weather(row.text)
            # only grab a few days of weather
            if len(weather.split("\n")) < self.DAYS_OF_WEATHER:
                weather += line + "\n"
        # trim off last newline
        weather = weather[:-1]

        return weather

    def replace_weather(self, row):
        replacements = {
            "Monday": "Mon ",
            "Tuesday": "Tue ",
            "Wednesday": "Wed ",
            "Thursday": "Thu ",
            "Friday": "Fri ",
            "Saturday": "Sat ",
            "Today": "Today ",
            "Tonight": "Tonight ",
            "Tomorrow": "Tomorrow ",
            "This Afternoon": "Afternoon ",
            "northwest": "NW",
            "northeast": "NE",
            "southwest": "SW",
            "southeast": "SE",
            "north": "N",
            "south": "S",
            "east": "E",
            "west": "W",
            "Northwest": "NW",
            "Northeast": "NE",
            "Southwest": "SW",
            "Southeast": "SE",
            "North": "N",
            "South": "S",
            "East": "E",
            "West": "W",
            "precipitation": "precip",
            "showers": "shwrs",
            "thunderstorms": "t-storms"
        }

        line = row
        for key, value in replacements.items():
            line = line.replace(key, value)
                        
        return line
