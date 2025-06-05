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
TIMEOUT = 10                  # data should be ready every 5 seconds
DISCARD = True                # only keep last reading
PROPERTIES = "c t h voc nox"  # properties for the display
FORMATS = {
  "c":    ["C/SE6:", "{0}p"],          # 0 - 40000
  "t":    ["T/SE6:", "{0:.1f}°C"],
  "h":    ["H/SE6:", "{0:.0f}%rH"],
  "p10":  ["PM1.0/SE6:","{0}"],        # 0 - 1000
  "p25":  ["PM2.5/SE6:","{0}"],        # 0 - 1000
  "p40":  ["PM4.0/SE6:","{0}"],        # 0 - 1000
  "p100": ["PM10/SE6:","{0}"],         # 0 - 1000
  "voc":  ["VOC/SE6:","{0}"],          # 1 - 500
  "nox":  ["NOX/SE6:","{0}"],          # 1 - 500
  }

from log_writer import Logger
g_logger = Logger()
from sleep import TimeSleep

import time
import adafruit_sen6x

class SEN6X:
  # we don't use timestamps on the display ...
  headers = ('C/SE6 ppm,T/SE6 °C,H/SE6 %rH,' +
             'PM1.0,PM2.5,PM4.0,PM10,VOC,NOX' )

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
    if not self.DISCARD:
      self.headers = (
        f't (1),' +
        f'C/SE6 ppm (1),' +
        f'T/SE6 °C (1),' +
        f'H/SE6 %rH (1),' +
        'PM1.0 (1),PM2.5 (1),PM4.0 (1),PM10 (1),' +
        'VOC (1),NOX (1)'
        )
      for i in range(1,self.SAMPLES):
        self.headers += (
          f',t ({i+1}),' +
          f'C/SE6 ppm ({i+1}),' +
          f'T/SE6 °C ({i+1}),' +
          f'H/SE6 %rH ({i+1}),' +
          f'PM1.0 ({i+1}),PM2.5 ({i+1}),PM4.0 ({i+1}),PM10 ({i+1}),' +
          f'VOC ({i+1}),NOX ({i+1})'
          )

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
      t_rel = 0;  co2 = 0;  temp = 0;  hum  = 0
      p10   = -1; p25 = -1; p40  = -1; p100 = -1
      voc   = -1; nox = -1
      start = time.monotonic()
      while time.monotonic()-start < self.TIMEOUT:
        if self.sen6x.data_ready:
          sen6_data = self.sen6x.all_measurements()
          t_rel = time.monotonic() - self._t0

          co2   = sen6_data["co2"]
          temp  = round(sen6_data["temperature"],1)
          hum   = round(sen6_data["humidity"],0)
          p10   = sen6_data["pm1_0"]
          p25   = sen6_data["pm2_5"]
          p40   = sen6_data["pm4_0"]
          p100  = sen6_data["pm10"]
          voc   = sen6_data["voc_index"]
          nox   = sen6_data["nox_index"]
          break
        else:
          time.sleep(0.2)

      # add data to csv-record
      if not self.DISCARD and self.SAMPLES > 1:
        csv_results += f",{t_rel:.2f},{co2},{temp:.1f},{hum:.0f}"
        csv_results += f",{p10},{p25},{p40},{p100}"
        csv_results += f",{voc},{nox}"

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
      csv_results += f",{p10},{p25},{p40},{p100}"
      csv_results += f",{voc},{nox}"

    # in any case, only save and show last reading
    data[self.product] = {
      "t": temp,
      "h":  hum,
      "c":  co2,
      "p10": p10,
      "p25": p25,
      "p40": p40,
      "p100": p100,
      "voc": voc,
      "nox": nox,
      FORMATS['t'][0]: FORMATS['t'][1].format(temp),
      FORMATS['h'][0]: FORMATS['h'][1].format(hum),
      FORMATS['c'][0]: FORMATS['c'][1].format(co2),
      FORMATS['p10'][0]: FORMATS['p10'][1].format(p10),
      FORMATS['p25'][0]: FORMATS['p25'][1].format(p25),
      FORMATS['p40'][0]: FORMATS['p40'][1].format(p40),
      FORMATS['p100'][0]: FORMATS['p100'][1].format(p100),
      FORMATS['voc'][0]: FORMATS['voc'][1].format(voc),
      FORMATS['nox'][0]: FORMATS['nox'][1].format(nox),
    }
    if not self.ignore:
      for p in self.PROPERTIES:
        values.extend([None,data[self.product][p]])
    return csv_results[1:]
