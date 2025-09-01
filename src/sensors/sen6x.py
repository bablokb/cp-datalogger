#-----------------------------------------------------------------------------
# Class for Sensor SEN6x.
#
# Note: this wrapper currently only supports the SEN66.
#
# Naming convention:
#   - filenames in lowercase (sen6x.py)
#   - class name the same as filename in uppercase (SEN6X)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

SAMPLES = 2
INTERVAL = 5
TIMEOUT = 5                   # data should be ready every 5 seconds
DISCARD = True                # only keep last reading
PROPERTIES = "c t h"          # properties for the display
FORMATS = {
  "c":    ["C/SE6:", "{0}p"],          # 0 - 40000
  "t":    ["T/SE6:", "{0:.1f}°C"],
  "h":    ["H/SE6:", "{0:.0f}%rH"],

  "voc":  ["VOC/SE6:","{0}"],          # 1 - 500
  "nox":  ["NOX/SE6:","{0}"],          # 1 - 500

  "pm10":  ["PM1.0/SE6:","{0}"],       # 0 - 1000 µg/m³
  "pm25":  ["PM2.5/SE6:","{0}"],       # 0 - 1000 µg/m³
  "pm40":  ["PM4.0/SE6:","{0}"],       # 0 - 1000 µg/m³
  "pm100": ["PM10/SE6:","{0}"],        # 0 - 1000

  "pn10":  ["PN1.0/SE6:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn25":  ["PN2.5/SE6:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn40":  ["PN4.0/SE6:","{0:0.1f}"],  # 0 - 6554 particles/cm³
  "pn100": ["PN10/SE6:","{0:0.1f}"],   # 0 - 6554 particles/cm³
  }

from log_writer import Logger
g_logger = Logger()
from sleep import TimeSleep

import time
import adafruit_sen6x

class SEN6X:
  # we don't use timestamps on the display ...
  HEADERS_BASE = 'C/SE6 ppm,T/SE6 °C,H/SE6 %rH'
  HEADERS_GAS  = 'VOC,NOX'
  HEADERS_PM   = 'PM1.0,PM2.5,PM4.0,PM10'
  HEADERS_PN   = 'PN1.0,PN2.5,PN4.0,PN10'
  HEADERS      = ','.join([HEADERS_BASE,HEADERS_GAS,HEADERS_PM,HEADERS_PN])

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.product = "SEN66"
    self._config = config
    self.ignore = False
    self.init_time = 30   # for PM
    self.sen6x = None
    for nr,bus in enumerate(i2c):
      if not bus:
        continue
      try:
        g_logger.print(f"testing {self.product} on i2c{nr}")
        self.sen6x = adafruit_sen6x.SEN66(bus)
        g_logger.print(f"detected {self.product} on i2c{nr}")
        break
      except Exception as ex:
        g_logger.print(f"exception: {ex}")
    if not self.sen6x:
      raise Exception(f"no {self.product} detected. Check config/cabling!")

    # configure sensor
    if not getattr(config,"SEN6X_AUTO_CALIBRATE",False):
      g_logger.print(f"deactivating {self.product} auto-calibration")
      self.sen6x.co2_automatic_self_calibration = False
    offset, slope = getattr(config,"SEN6X_TEMP_OFFSET",[0,0])
    if offset or slope:
      g_logger.print(f"configuring temperature-offset to [{offset},{slope}]")
      # implicitly use time-constant=0 and slot=0
      self.sen6x.temperature_offset(offset,slope)
    altitude = getattr(config,"BMx280_ALTITUDE_AT_LOCATION",None)
    if not altitude is None:
      g_logger.print(f"setting altitude to {altitude}m above sea-level")
      self.sen6x.sensor_altitude = altitude

    self.SAMPLES  = getattr(config,"SEN6X_SAMPLES",SAMPLES)
    self.INTERVAL = getattr(config,"SEN6X_INTERVAL",INTERVAL)
    self.TIMEOUT  = getattr(config,"SEN6X_TIMEOUT",TIMEOUT)
    self.DISCARD  = getattr(config,"SEN6X_DISCARD",DISCARD)
    self.PROPERTIES = getattr(config,"SEN6X_PROPERTIES",PROPERTIES).split()
    if self.SAMPLES == 1:
      self.DISCARD = True

    # dynamically create formats for display...
    self.formats = []
    for p in self.PROPERTIES:
      self.formats.extend(FORMATS[p])

    # ... and header for csv
    if self.DISCARD:
      self.headers = SEN6X.HEADERS
    else:
      # multiple samples: add column for time
      cols = ['t'].extend(SEN6X.HEADERS.split(','))
      self.headers = ''
      for i in range(self.SAMPLES):
        for col in cols:
          self.headers += f"{col} ({i+1})"

    # start sampling
    self.sen6x.start_measurement()
    self._t0 = time.monotonic()

  def read_sensor(self):
    """ dummy method, must be implemented by subclass if necessary """
    pass

  def read(self,data,values):
    """ read sensor values """

    # compensate for pressure. Requires a BME280/BMP280 sensor
    if "bme280" in data:
      p_comp = data["bme280"]["pl"]
    elif "bmp280" in data:
      p_comp = data["bmp280"]["pl"]
    else:
      p_comp = None
    if p_comp:
      self.sen6x.ambient_pressure = int(p_comp)

    # take multiple readings
    if self.SAMPLES > 2 or self.INTERVAL > 5:
      g_logger.print(f"SEN6x: taking {self.SAMPLES} " +
                     f"samples with interval {self.INTERVAL}s")
    csv_results = ""
    for i in range(self.SAMPLES):
      t_rel = 0;  co2  = 0;  temp = 0;  hum   = 0
      pm10  = -1; pm25 = -1; pm40 = -1; pm100 = -1
      pn10  = -1; pn25 = -1; pn40 = -1; pn100 = -1
      voc   = -1; nox  = -1
      start = time.monotonic()
      while time.monotonic()-start < self.TIMEOUT:
        if self.sen6x.data_ready:
          t_rel = time.monotonic() - self._t0
          sen6x_std = self.sen6x.all_measurements()
          sen6x_pc  = self.sen6x.number_concentration()

          co2   = int(sen6x_std["co2"])
          temp  = round(sen6x_std["temperature"],1)
          hum   = round(sen6x_std["humidity"],0)
          voc   = int(sen6x_std["voc_index"])
          nox   = int(sen6x_std["nox_index"])
          pm10  = int(sen6x_std["pm1_0"])
          pm25  = int(sen6x_std["pm2_5"])
          pm40  = int(sen6x_std["pm4_0"])
          pm100 = int(sen6x_std["pm10"])
          pn10  = round(sen6x_pc["nc_pm1_0"],1)
          pn25  = round(sen6x_pc["nc_pm2_5"],1)
          pn40  = round(sen6x_pc["nc_pm4_0"],1)
          pn100 = round(sen6x_pc["nc_pm10"],1)
          break
        else:
          time.sleep(0.2)

      # add data to csv-record
      if not self.DISCARD and self.SAMPLES > 1:
        csv_results += f",{t_rel:.2f},{co2},{temp:.1f},{hum:.0f}"
        csv_results += f",{voc},{nox}"
        csv_results += f",{pm10},{pm25},{pm40},{pm100}"
        csv_results += f",{pn10:.1f},{pn25:.1f},{pn40:.1f},{pn100:.1f}"

      # sleep the given time for the next sensor-readout
      if i < self.SAMPLES-1:
        TimeSleep.light_sleep(
          duration=max(0,self.INTERVAL-(time.monotonic()-start)))

    # switch sensor off in strobe mode (or cont. mode with deep-sleep)
    if self._config.STROBE_MODE or self._config.INTERVAL > 60:
      self.sen6x.stop_measurement()

    # only keep last reading for CSV if DISCARD is active
    if self.DISCARD:
      csv_results = f",{co2},{temp:.1f},{hum:.0f}"
      csv_results += f",{voc},{nox}"
      csv_results += f",{pm10},{pm25},{pm40},{pm100}"
      csv_results += f",{pn10:.1f},{pn25:.1f},{pn40:.1f},{pn100:.1f}"

    # in any case, only save and show last reading
    data[self.product] = {
      "t": temp,
      "h":  hum,
      "c":  co2,
      "voc": voc,
      "nox": nox,
      "pm10": pm10,
      "pm25": pm25,
      "pm40": pm40,
      "pm100": pm100,
      "pn10": pn10,
      "pn25": pn25,
      "pn40": pn40,
      "pn100": pn100,

      FORMATS['t'][0]: FORMATS['t'][1].format(temp),
      FORMATS['h'][0]: FORMATS['h'][1].format(hum),
      FORMATS['c'][0]: FORMATS['c'][1].format(co2),

      FORMATS['voc'][0]: FORMATS['voc'][1].format(voc),
      FORMATS['nox'][0]: FORMATS['nox'][1].format(nox),

      FORMATS['pm10'][0]: FORMATS['pm10'][1].format(pm10),
      FORMATS['pm25'][0]: FORMATS['pm25'][1].format(pm25),
      FORMATS['pm40'][0]: FORMATS['pm40'][1].format(pm40),
      FORMATS['pm100'][0]: FORMATS['pm100'][1].format(pm100),

      FORMATS['pn10'][0]: FORMATS['pn10'][1].format(pn10),
      FORMATS['pn25'][0]: FORMATS['pn25'][1].format(pn25),
      FORMATS['pn40'][0]: FORMATS['pn40'][1].format(pn40),
      FORMATS['pn100'][0]: FORMATS['pn100'][1].format(pn100),
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data[self.product][p]])
    return csv_results[1:]
