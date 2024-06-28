# meshbot

connect your node over serial to Raspberry PI and let this bot answer public and private messages

## requirements

- meshtastic python CLI - https://meshtastic.org/docs/software/python/cli/installation/
  - got you to install python, pip and few other dependencies
- dependencies - install with `pip install -r requirements.txt`

## test on RPI

### test over ssh terminal

- edit mesh_bot.py if you need other than serial connection
- run `python3 mesh_bot.py` 
- if it starts without errors send private message to your node from other node `PING`
- you should see response in the terminal and got it as message too
- terminate the script and install it as service

### install bot as a service

- create and edit service file (see content of [mesh_bot.service](mesh_bot.service)) `sudo nano /etc/systemd/system/meshbot.service`
- reload daemon `sudo systemctl daemon-reload`
- start service `sudo systemctl start meshbot.service`
- see status `sudo systemctl status meshbot.service | more` - this one displays log from the service so you can see when you send a message what happened

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
