#-----------------------------------------------------------------------------
# Sensor definition for power-status of Tasmota smart-plugs.
#
# This "sensor" queries the power-status of Tasmota smart-plugs.
#
# Note: this sensor needs WLAN-access and is therefore not battery-friendly!
#
# Naming convention:
#   - filenames in lowercase (tm_power.py)
#   - class name the same as filename in uppercase (TM_POWER)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

# recommendation: set TM_POWER_PROPERTIES="P", since voltage is more or
#                 less constant and current is usually not relevant

PROPERTIES = "P V C"     # properties for the display
FORMATS = {
  "P":       ["P/tm:", "{0:.1f}W"],
  "V":       ["V/tm:", "{0}V"],
  "C":       ["C/tm:", "{0:.3f}A"],
  }

from singleton import singleton
from wifi_impl_builtin import WifiImpl

@singleton
class TM_POWER:
  headers = 'P/tm W ({0}), V/tm V ({0}), C/tm A ({0})'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self._config = config
    self.ignore = False
    self.TM_POWER_HOSTS = getattr(config,"TM_POWER_HOSTS")
    self.TM_POWER_URL   = getattr(config,"TM_POWER_URL",
                                 "http://{0}/cm?cmnd=status%2010")
    self.PROPERTIES     = getattr(config,
                                  "TM_POWER_PROPERTIES",PROPERTIES).split()

    # dynamically create formats for display...
    formats = []
    for p in self.PROPERTIES:
      formats.extend(FORMATS[p])
    self.formats = formats*len(self.TM_POWER_HOSTS)

    # ... and header for csv
    self.headers = ', '.join(
      [self.headers.format(i) for i in range(len(self.TM_POWER_HOSTS))])

    self._wifi = WifiImpl()

  def read(self,data,values):
    """ read (query) all smart-plugs """

    # Query plugs. The expected result is:
    #   {
    #     "StatusSNS": {
    #       "Time": "2026-01-10T13:34:33",
    #       "ENERGY": {
    #         "TotalStartTime": "2026-01-10T13:22:27",
    #         "Total": 0.001,
    #         "Yesterday": 0,
    #         "Today": 0.001,
    #         "Power": 41,
    #         "ApparentPower": 41,
    #         "ReactivePower": 0,
    #         "Factor": 1,
    #         "Voltage": 233,
    #         "Current": 0.175
    #       }
    #     }
    #   }

    resp = []
    for ip in self.TM_POWER_HOSTS:
      try:
        resp.append(self._wifi.get(self.TM_POWER_URL.format(ip)).json())
      except Exception as ex:
        g_logger.print(f"failed to query data from {ip} with exception: {ex}")
        resp.append(None)

    # shutdown wifi if in strobe mode
    if self._config.STROBE_MODE or self._config.INTERVAL > 60:
      self._wifi.radio.enabled = False

    # don't record anything without a response
    if not any(resp):
      return

    # parse data
    csv_results = ""
    results = []
    for response in resp:
      if not response:
        power   = 0.0
        voltage = 0
        current = 0.0
      else:
        info    = response["StatusSNS"]["ENERGY"]
        power   = round(info["Power"],1)
        voltage = int(info["Voltage"])
        current = round(info["Current"],3)

      # add to csv
      csv_results += f"{power:0.1f},{voltage:d},{current:0.3f}"

      # add to data-structure
      results.append({
        "P": power,
        "V": voltage,
        "C": current,
        FORMATS['P'][0]: FORMATS['P'][1].format(power),
        FORMATS['V'][0]: FORMATS['V'][1].format(voltage),
        FORMATS['C'][0]: FORMATS['C'][1].format(current),
        })

    # final data-structure
    data["tm_power"] = results

    # fill in subset of data for display
    if not self.ignore:
      for result in results:
        for p in self.PROPERTIES:
          values.extend([None,result[p]])

    # return all data for csv
    return csv_results
