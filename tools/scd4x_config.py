#-----------------------------------------------------------------------------
# Configure SCD4x-sensor.
#
# Run "from tools import scd4x_config" and then one of the commands printed.
# 
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

SAMPLE_INTERVAL = 5
import time
import busio

from log_writer import Logger
g_logger = Logger('console')

from sensors.scd40 import SCD40
from sensors.aht20 import AHT20
from datacollector import g_config
import pins
from oled import OLED

# --- configuration function   -----------------------------------------------

def run(duration=60,altitude=None,ppm=None,temp_offset=None,persist=False):
  """ configure scd4x """

  global textlabel

  if not have_i2c:
    g_logger.print("error: no i2c-bus configured")
    return

  # operate for 10 minutes in clean air
  g_logger.print(f"operating for {duration} minutes...")
  g_logger.set_target(None)
  c_sensor.scd4x.start_periodic_measurement()
  header = f"ts,{c_sensor.headers}"
  if t_sensor:
    header += f",{t_sensor.headers},t_diff"
  print(header)

  time_left = duration*60
  while time_left > 0:
    time.sleep(SAMPLE_INTERVAL)
    time_left -= SAMPLE_INTERVAL

    ts  = time.localtime()
    ts  = f"{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d}"
    csv = f"{ts},"

    data = {}
    csv += c_sensor.read(data,[])
    if t_sensor:
      csv += f",{t_sensor.read(data,[])}"
      t_off = round(data["scd40"]["t"] - data["aht20"]["t"],1)
      print(f"{csv},{t_off}")
    else:
      print(csv)

    mins,secs = divmod(time_left,60)
    if not secs:
      print(f"time left: {mins} minutes")

    # update OLED if connected
    if textlabel:
      t_left = f"{mins:02d}:{secs:02d}"
      textlabel.text = f"Rest:  {t_left}\nC/SCD: {data["scd40"]["C/SCD:"]}"
      if t_sensor:
        textlabel.text += f"\nT-off: {t_off:0.1f}°C"

  # perform configuration
  g_logger.set_target('console')
  c_sensor.scd4x.stop_periodic_measurement()

  if persist:
    c_sensor.scd4x.self_calibration_enabled = False
    if not altitude is None:
      c_sensor.scd4x.altitude = altitude
    if not temp_offset is None:
      c_sensor.scd4x.temperature_offset = temp_offset
    if not ppm is None:
      c_sensor.scd4x.force_calibration(ppm)
    g_logger.print("persisting settings")
    c_sensor.scd4x.persist_settings()
  else:
    g_logger.print("settings unchanged")

# --- wrapper for autorun via src/scd4x_config   -----------------------------

def autorun():
  """ automatically run in update-mode """

  duration = getattr(g_config,"SCD4X_CONFIG_DURATION",60)
  ppm      = getattr(g_config,"SCD4X_CONFIG_PPM_MIN",418)
  t_off    = getattr(g_config,"SCD4X_CONFIG_T_OFF",None)
  altitude = getattr(g_config,"BMx280_ALTITUDE_AT_LOCATION",540)
  
  g_logger.print(f"starting: run(duration={duration},")
  g_logger.print(f"              altitude={altitude},")
  g_logger.print(f"              ppm={ppm},")
  g_logger.print(f"              temp_offset={t_off},")
  g_logger.print(f"              persist=True)")

  run(duration=duration,
      altitude=altitude,
      ppm=ppm,
      temp_offset=t_off,
      persist=True)

# --- code executed during import   ------------------------------------------

# Initialse i2c busses for use by sensors and RTC
have_i2c = False
try:
  i2c_busses = [None,busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)]
  have_i2c = True
except Exception as ex0:
  g_logger.print(f"exception trying to create I2C1: {ex0}")
  i2c_busses = [None,None]

if g_config.HAVE_I2C0:
  try:
    i2c_busses[0] = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
    have_i2c = True
  except Exception as ex1:
    g_logger.print(f"exception trying to create I2C0: {ex1}")
    g_logger.print("warning: could not create i2c0, check wiring!")

if not have_i2c:
  g_logger.print("error: no i2c-bus detected. Config not possible!!!")

else:
  # use OLED if available
  try:
    oled_display = OLED(g_config,i2c_busses)
    textlabel    = oled_display.get_textlabel()
    display      = oled_display.get_display()
    g_logger.print(
      f"detected OLED with size {display.width}x{display.height}")
  except Exception as ex3:
    g_logger.print(f"no OLED? Exception: {ex3}")
    display = None
    textlabel = None

  # use AHT20 if available
  try:
    t_sensor = AHT20(g_config,i2c_busses)
  except Exception as ex4:
    g_logger.print(f"no AHT20 detected. Exception: {ex4}")
    t_sensor = None

  # override some settings for this use case
  g_config.SCD4X_SAMPLES = 1
  g_config.STROB_MODE = False
  g_config.INTERVAL = SAMPLE_INTERVAL

  c_sensor = SCD40(g_config,i2c_busses)
  c_sensor.scd4x.stop_periodic_measurement()
  print(f"current altitude:    {c_sensor.scd4x.altitude}")
  print(f"current temp-offset: {c_sensor.scd4x.temperature_offset}")
  print("example usage (see docs for details):\n")
  print("  scd4x_config.run()                      # run for 60 minutes")
  print("  scd4x_config.run(altitude=540,")
  print("                   temp_offset=4,")
  print("                   ppm=418,")
  print("                   persist=True)          # dito, but save config")
