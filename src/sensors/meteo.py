#-----------------------------------------------------------------------------
# Sensor definition for the METEO-API (pseudo-sensor, remote-sensor)
#
# This "sensor" queries the METEO-API for current weather-condition at the
# given location. Only a subset of the available parameters is retrieved
# and only a subset is shown on the display.
#
# Note: this sensor needs WLAN-access and is therefore not battery-friendly!
#
# Naming convention:
#   - filenames in lowercase (meteo.py)
#   - class name the same as filename in uppercase (METEO)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

PROPERTIES = "t h ps code w_speed w_dir r"     # properties for the display
FORMATS = {
  "t":       ["T/met:", "{0:.1f}°C"],
  "h":       ["H/met:", "{0:.0f}%rH"],
  "ps":      ["P/met:", "{0:.0f}hPa"],
  "code":    ["wc/met:", "{0}"],
  "w_speed": ["ws/met:", "{0:.1f}km/s"],
  "w_dir":   ["wd/met:", "{0:.0f}°"],
  "r":       ["r/met:", "{0}mm"]
  }

from singleton import singleton
from wifi_impl_builtin import WifiImpl

@singleton
class METEO:
  headers = 'T/met °C,H/met %rH,P/met hPa,WMO,Wspd km/s,Wdir °,mm'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    METEO_LATITUDE  = getattr(config,"METEO_LATITUDE",48.6967)
    METEO_LONGITUDE = getattr(config,"METEO_LONGITUDE",13.4631)

    # dynamically create formats for display...
    self.PROPERTIES = getattr(config,"METEO_PROPERTIES",PROPERTIES).split()
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

    self._url = "".join([
      "https://api.open-meteo.com/v1/forecast?",
      f"latitude={METEO_LATITUDE}",
      f"&longitude={METEO_LONGITUDE}",
      "&hourly=relativehumidity_2m,",
      "precipitation,pressure_msl,",
      "&current_weather=true",
      "&timezone=auto",
      "&forecast_days=1"
      ])
    self._wifi = WifiImpl()

  def read(self,data,values):
    """ read (query) METEO-API """

    # query api
    response = self._wifi.get(self._url).json()
    if not response:
      return

    # parse data
    t    = response["current_weather"]["temperature"]
    c    = response["current_weather"]["weathercode"]
    ws   = response["current_weather"]["windspeed"]
    wd   = response["current_weather"]["winddirection"]
    hour = int(response["current_weather"]["time"][11:13])   # 2022-01-01T12:00
    h    = response["hourly"]["relativehumidity_2m"][hour]
    ps   = response["hourly"]["pressure_msl"][hour]
    r    = response["hourly"]["precipitation"][hour]

    data["meteo"] =  {
      "t":     t,
      "h":     h,
      "ps":    ps,
      "code":  c,
      "w_speed":  ws,
      "w_dir":    wd,
      "r":     r
      }

    # fill in subset of data for display
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data["meteo"][p]])

    # return all data for csv
    return f"{t:0.1f},{h:0.0f},{ps:0.0f},{c:d},{ws:0.1f},{wd:0.0f},{r:0.1f}"
