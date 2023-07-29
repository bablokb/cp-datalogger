#-----------------------------------------------------------------------------
# Basic data-collection program. This program will
#
#   - initialize hardware
#   - update RTCs (time-server->) external-RTC -> internal-RTC
#   - collect data
#   - update the display
#   - save data
#   - set next wakeup alarm
#   - turn power off
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
_ts = []
_ts.append(time.monotonic())

import gc
import board
import alarm
import os
import builtins

from digitalio import DigitalInOut, Direction, Pull

# import for SD-card
import storage
import adafruit_sdcard

# imports for i2c and rtc
import busio
from rtc_ext.pcf8523 import ExtPCF8523 as ExtRTC

# pin definitions
import pins

_ts.append(time.monotonic())

# --- early configuration of the log-destination   ---------------------------

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')

_ts.append(time.monotonic())

# --- default configuration is in config.py on the pico.
#     You can override it also with a config.py on the sd-card   -------------

class Settings:
  def import_config(self):
    """ import config-module and make variables attributes """
    import config
    for var in dir(config):
      if var[0] != '_':
        g_logger.print(f"{var}={getattr(config,var)}")
        setattr(self,var,getattr(config,var))
    config = None
    gc.collect()

g_config = Settings()
g_config.import_config()

_ts.append(time.monotonic())

# --- main application class   -----------------------------------------------

class DataCollector():
  """ main application class """

  # --- hardware-setup   -----------------------------------------------------

  def setup(self):
    """ create hardware-objects """

    # early setup of SD-card (in case we send debug-logs to sd-card)
    self._spi = None
    if g_config.HAVE_SD:
      self._spi = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
      self.sd_cs = DigitalInOut(pins.PIN_SD_CS)
      sdcard     = adafruit_sdcard.SDCard(self._spi,self.sd_cs)
      self.vfs   = storage.VfsFat(sdcard)
      storage.mount(self.vfs, "/sd")
      _ts.append(time.monotonic())
      try:
        import sys
        sys.path.insert(0,"/sd")
        g_config.import_config()
        sys.path.pop(0)
      except:
        g_logger.print("no configuration found in /sd/config.py")

    _ts.append(time.monotonic())

    # Initialse i2c bus for use by sensors and RTC
    i2c1 = busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)
    if g_config.HAVE_I2C0:
      try:
        i2c0 = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
      except:
        i2c0 = None
    else:
      i2c0 = None

    # If our custom PCB is connected, we have an RTC. Initialise it.
    if g_config.HAVE_PCB:
      self.rtc = ExtRTC(i2c1,
        net_update=g_config.NET_UPDATE)         # this will also clear interrupts
      self.rtc.rtc_ext.high_capacitance = True  # the pcb uses a 12.5pF capacitor
      self.rtc.update()                         # (time-server->)ext-rtc->int-rtc

    self.done           = DigitalInOut(pins.PIN_DONE)
    self.done.direction = Direction.OUTPUT
    self.done.value     = 0

    self.vbus_sense           = DigitalInOut(board.VBUS_SENSE)
    self.vbus_sense.direction = Direction.INPUT

    _ts.append(time.monotonic())

    # display
    if g_config.HAVE_DISPLAY:
      from display import Display
      self._display = Display(g_config,self._spi)

    _ts.append(time.monotonic())

    # just for testing
    if g_config.TEST_MODE:
      self._led            = DigitalInOut(board.LED)
      self._led.direction  = Direction.OUTPUT

    self.save_status = "__"

    #configure sensors
    self._configure_sensors(i2c0,i2c1)

    _ts.append(time.monotonic())

  # --- configure sensors   ---------------------------------------------------

  def _configure_sensors(self,i2c0,i2c1):
    """ configure sensors """

    self._formats = []
    self.csv_header = f"#ID: {g_config.LOGGER_ID}\n#Location: {g_config.LOGGER_LOCATION}\n"
    self.csv_header += "#ts"

    self._sensors = []
    for spec in g_config.SENSORS.split(' '):   # spec is sensor(addr,bus)
      # defaults for normal case without addr/bus
      spec   = spec.split('(')
      sensor = spec[0]
      addr   = None
      bus    = None

      # check for parameters
      if len(spec) > 1:
        spec = spec[1][:-1].split(',')   # remove trailing ) and split
        # parse parameters
        addr = int(spec[0],16)
        spec.pop(0)
        if addr < 2:                                # addr is actually a bus
          bus  = i2c0 if addr == 0 else i2c1
          addr = None
        elif len(spec):
          bus = i2c0 if spec[2] == "0" else i2c1

      sensor_module = builtins.__import__(sensor,None,None,[sensor.upper()],0)
      sensor_class = getattr(sensor_module,sensor.upper())
      _sensor = sensor_class(g_config,i2c0,i2c1,
                             addr,bus,
                             None,None)
      self._sensors.append(_sensor.read)
      self._formats.extend(_sensor.formats)
      self.csv_header += f",{_sensor.headers}"

  # --- blink   --------------------------------------------------------------

  def blink(self, count=1, blink_time=0.25):
    for _ in range(count):
      self._led.value = 1
      time.sleep(blink_time)
      self._led.value = 0
      time.sleep(blink_time)

  # --- check for continuous-mode   ------------------------------------------

  def continuous_mode(self):
    """ returns false if on USB-power """

    return g_config.FORCE_CONT_MODE or (
            self.vbus_sense.value and not g_config.FORCE_STROBE_MODE)

  # --- collect data   -------------------------------------------------------

  def collect_data(self):
    """ collect sensor data """

    ts = time.localtime()
    ts_str = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}T{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d}"
    self.data = {
      "ts":   ts_str
      }
    self.record = ts_str

    self.values = []
    for read_sensor in self._sensors:
      rec = read_sensor(self.data,self.values)
      self.record += f",{rec}"

  # --- check if file already exists   --------------------------------------

  def file_exists(self, filename):
    """ check if file exists """
    try:
      status = os.stat(filename)
      return True
    except OSError:
      return False

  # --- save data   ----------------------------------------------------------

  def save_data(self):
    """ save data """

    if g_config.SHOW_UNITS:
      self.pretty_print()
    else:
      g_logger.print(self.record)

    if g_config.HAVE_SD:
      ymd = self.data["ts"].split("T")[0]
      y,m,d = ymd.split("-")
      outfile = g_config.CSV_FILENAME.format(
        ID=g_config.LOGGER_ID,
        YMD=ymd,Y=y,M=m,D=d)
      new_csv = not self.file_exists(outfile)
      self.save_status = ":("
      with open(outfile, "a") as f:
        if new_csv:
          f.write(f"{self.csv_header}\n")
        f.write(f"{self.record}\n")
        self.save_status = "SD"

  # --- pretty-print data to log   -------------------------------------------

  def pretty_print(self):
    """ pretty-print data to log """

    columns = self.csv_header.split('#')[-1].split(',')
    merged = zip(columns,self.record.split(','))
    for label,value in merged:
      space = '\t\t' if len(label) < 9 else '\t'
      g_logger.print(f"{label}:{space}{value}")

  # --- send data   ----------------------------------------------------------

  def send_data(self):
    """ send data using LORA """
    g_logger.print(f"not yet implemented!")

  # --- update display   -----------------------------------------------------

  def update_display(self):
    """ update display """

    gc.collect()
    if g_config.SIMPLE_UI:
      self._display.create_simple_view()
    else:
      self._display.create_view(self._formats)

    if g_config.SIMPLE_UI:
      self._display.set_ui_text(self.csv_header,self.record)
    else:
      if len(self.values) < len(self._formats):
        # fill in unused cells
        self.values.extend(
          [None for _ in range(len(self._formats)-len(self.values))])
      elif len(self.values) > len(self._formats):
        # remove extra values
        del self.values[len(self._formats):]

      dt, ts = self.data['ts'].split("T")
      footer = f"at {dt} {ts} {self.save_status}"
      self._display.set_values(self.values,footer)

    self._display.refresh()
    g_logger.print("finished refreshing display")

    if not self.continuous_mode():
      time.sleep(3)              # refresh returns before it is finished

  # --- set next wakeup   ----------------------------------------------------

  def configure_wakeup(self):
    """ configure rtc for next wakeup """
    if g_config.HAVE_PCB:
      if hasattr(g_config,"TIME_TABLE"):
        self.rtc.set_alarm(self.rtc.get_table_alarm(g_config.TIME_TABLE))
      else:
        self.rtc.set_alarm(self.rtc.get_alarm_time(m=g_config.OFF_MINUTES))

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self):
    """ tell the power-controller to cut power """

    self.done.value = 1
    time.sleep(0.2)
    self.done.value = 0
    time.sleep(2)

  # --- cleanup   -----------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """

    self._spi.deinit()

# --- main program   ---------------------------------------------------------

g_logger.print("main program start")
if g_config.TEST_MODE:
  time.sleep(5)                        # give console some time to initialize
g_logger.print("setup of hardware")

app = DataCollector()
app.setup()

print(60*"-")
print(f"{_ts[1]-_ts[0]:0.3f} (import)")
print(f"{_ts[2]-_ts[1]:0.3f} (log-config)")
print(f"{_ts[3]-_ts[2]:0.3f} (flash-config)")
print(f"{_ts[4]-_ts[3]:0.3f} (sd-mount)")
print(f"{_ts[5]-_ts[4]:0.3f} (sd-config)")
print(f"{_ts[6]-_ts[5]:0.3f} (rtc-update)")
print(f"{_ts[7]-_ts[6]:0.3f} (display-config)")
print(f"{_ts[8]-_ts[7]:0.3f} (sensor-config)")
print(f"{_ts[8]-_ts[0]:0.3f} (total)")
print(60*"-")

while True:
  if g_config.TEST_MODE:
    app.blink(count=g_config.BLINK_START, blink_time=g_config.BLINK_TIME_START)

  app.collect_data()
  try:
    app.save_data()
  except:
    g_logger.print("exception during save_data()")
    app.cleanup()
    raise
    
  if g_config.TEST_MODE:
    app.blink(count=g_config.BLINK_END, blink_time=g_config.BLINK_TIME_END)

  if g_config.HAVE_DISPLAY:
    try:
      app.update_display()
    except:
      g_logger.print("exception during update_display()")
      app.cleanup()
      raise

  if g_config.HAVE_LORA:
    app.send_data()

  # check if running on USB and sleep instead of shutdown
  if app.continuous_mode():
    g_logger.print(f"continuous mode: next measurement in {g_config.CONT_INT} seconds")
    time.sleep(g_config.CONT_INT)
  else:
    break

app.configure_wakeup()
app.shutdown()
