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
from datacollector import Settings

# access point settings
try:
  from ap_config import ap_config
except:
  ap_config = {
    'debug': True,
    'cache': False,
    'ssid': 'datalogger',
    'password': '12345678',             # ignored for wifi.AuthMode.OPEN
    'auth_modes': [wifi.AuthMode.OPEN], # or [wifi.AuthMode.WPA2, wifi.AuthMode.PSK]
    'hostname': 'datalogger'           # msdn hostname
  }

g_config = Settings()
g_config.import_config()

# --- turn on LED on sensor-pcb   --------------------------------------------

switch_d = DigitalInOut(pins.PIN_SWD)
switch_d.direction = Direction.OUTPUT
switch_d.value = True

# --- mount sd-card if available   -------------------------------------------

if g_config.HAVE_SD:
  import storage
  import adafruit_sdcard
  import busio
  spi    = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
  sd_cs  = DigitalInOut(pins.PIN_SD_CS)
  sdcard = adafruit_sdcard.SDCard(spi,sd_cs)
  vfs    = storage.VfsFat(sdcard)
  storage.mount(vfs, "/sd")

# --- start AP and web-server   ----------------------------------------------

if ap_config["debug"]:
  time.sleep(5)
  print("!!! Starting in ADMIN-Mode !!!")

server = webap.WebAP(config=ap_config)
server.run()
