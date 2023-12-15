#-----------------------------------------------------------------------------
# Start admin-mode: run AP together with a web-server.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import wifi
import time
from digitalio import DigitalInOut, Pull, Direction

import pins
import webap

# access point settings
try:
  from ap_config import config
except:
  config = {
    'debug': True,
    'ssid': 'datalogger',
    'password': '12345678',             # ignored for wifi.AuthMode.OPEN
    'auth_modes': [wifi.AuthMode.OPEN], # or [wifi.AuthMode.WPA2, wifi.AuthMode.PSK]
    'hostname': 'datalogger'           # msdn hostname
  }


# --- turn on LED on sensor-pcb   --------------------------------------------

switch_d = DigitalInOut(pins.PIN_SWD)
switch_d.direction = Direction.OUTPUT
switch_d.value = True

# --- start AP and web-server   ----------------------------------------------

if config["debug"]:
  time.sleep(5)
  print("!!! Starting in ADMIN-Mode !!!")

server = webap.WebAP(config=config)
server.run()
