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

from singleton import singleton
from wifi_impl_builtin import WifiImpl

@singleton
class METEO:
  formats = ["T/met:", "{0:.1f}°C",
             "H/met:", "{0:.0f}%rH",
             "P/met:", "{0:.0f}hPa"]
  headers = 'T/met °C,H/met %rH,P/met hPa,WMO,Wspd km/s,Wdir °,mm'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self.ignore = False
    if hasattr(config,"METEO_LATITUDE"):
      METEO_LATITUDE=config.METEO_LATITUDE
    else:
      METEO_LATITUDE=48.6967
    if hasattr(config,"METEO_LONGITUDE"):
      METEO_LONGITUDE=config.METEO_LONGITUDE
    else:
      METEO_LONGITUDE=13.4631

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
    p    = response["hourly"]["pressure_msl"][hour]
    r    = response["hourly"]["precipitation"][hour]

    data["meteo"] =  {
      "temp":     t,
      "hum":      h,
      "pressure": p,
      "code":     c,
      "w_speed":  ws,
      "w_dir":    wd,
      "precip":   r
      }

    # fill in subset of data for display
    if not self.ignore:
      values.extend([None,t])
      values.extend([None,h])
      values.extend([None,p])

    # return all data for csv
    return f"{t:0.1f},{h:0.0f},{p:0.0f},{c:d},{ws:0.1f},{wd:0.0f},{r:0.1f}"
