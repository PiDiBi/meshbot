# meshbot

connect your node over serial to Raspberry PI and let this bot answer public and private messages

## requirements

- python3
- pip
- meshtastic python CLI - https://meshtastic.org/docs/software/python/cli/installation/
- dependencies - install with `pip install -r requirements.txt`

## Commands

- Various weather conditions
  - `sun` and `moon` return info on rise and set local time
  - `tide` returns the local tides, NOAA data source
  - `solar` gives an idea of the x-ray flux
  - `hfcond` returns a table of HF solar conditions
  - `wx` and `wxc` returns local weather forcast, NOAA data source (wxc is metric value)
- Other functions
  - `ping` - response with PONG and signal strength
  - `whereami` returns the address of location of sender if known
  - `joke` tells a joke
  - `whereami` - tries to find your location from GPS

## Recognition

Used ideas and snippets from other responder bots want to call them out!
 - https://github.com/SpudGunMan/meshing-around
