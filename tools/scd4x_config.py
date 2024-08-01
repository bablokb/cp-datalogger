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

import time
import busio

from log_writer import Logger
g_logger = Logger('console')

from sensors.scd40 import SCD40
from datacollector import g_config
import pins

# --- configuration function   -----------------------------------------------

def run(duration=60,altitude=None,ppm=418,temp_offset=None,persist=False):
  """ configure scd4x """

  if not have_i2c:
    g_logger.print("error: no i2c-bus configured")
    return

  # operate for 10 minutes in clean air
  g_logger.print(f"operating for {duration} minutes...")
  g_logger.set_target(None)
  sensor.scd4x.start_periodic_measurement()
  print(sensor.headers)
  time_left = duration*60
  while time_left > 0:
    time.sleep(5)
    time_left -= 5

    ts = time.localtime()
    data = f"{ts.tm_year}-{ts.tm_mon:02d}-{ts.tm_mday:02d}T{ts.tm_hour:02d}:{ts.tm_min:02d}:{ts.tm_sec:02d},"

    data += sensor.read({},[])
    print(data)

    mins,secs = divmod(time_left,60)
    if not secs:
      print(f"time left: {mins} minutes")

  # perform configuration
  g_logger.set_target('console')
  sensor.scd4x.stop_periodic_measurement()
  sensor.scd4x.self_calibration_enabled = False
  if altitude:
    sensor.scd4x.altitude = altitude
  if temp_offset:
    sensor.scd4x.temperature_offset = temp_offset
  if ppm:
    sensor.scd4x.force_calibration(ppm)
  if persist:
    g_logger.print("persisting settings")
    sensor.scd4x.persist_settings()
  else:
    g_logger.print("settings unchanged")

# --- wrapper for autorun via src/scd4x_config   -----------------------------

def autorun():
  """ automatically run in update-mode """

  duration = getattr(g_config,"SCD4X_CONFIG_DURATION",60)
  ppm      = getattr(g_config,"SCD4X_CONFIG_PPM_MIN",418)
  t_off    = getattr(g_config,"SCD4X_CONFIG_T_OFF",None)
  altitude = getattr(g_config,"BMx280_ALTITUDE_AT_LOCATION",None)
  
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
except Exception as ex1:
  g_logger.print(f"exception trying to create I2C1: {ex1}")
  i2c_busses = [None,None]

if g_config.HAVE_I2C0:
  try:
    i2c_busses[0] = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
    have_i2c = True
  except Exception as ex0:
    g_logger.print(f"exception trying to create I2C0: {ex0}")
    g_logger.print("warning: could not create i2c0, check wiring!")

if not have_i2c:
  g_logger.print("error: no i2c-bus detected. Config not possible!!!")
else:
  g_config.SCD4X_SAMPLES = 1
  sensor = SCD40(g_config,i2c_busses)
  sensor.scd4x.stop_periodic_measurement()
  print(f"current altitude:    {sensor.scd4x.altitude}")
  print(f"current temp-offset: {sensor.scd4x.temperature_offset}")
  print("example usage (see docs for details):\n")
  print("  scd4x_config.run()                      # run for 60 minutes")
  print("  scd4x_config.run(altitude=520,")
  print("                   temp_offset=4,")
  print("                   ppm=418,")
  print("                   persist=True)          # dito, but save config")
