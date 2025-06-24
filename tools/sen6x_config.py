#-----------------------------------------------------------------------------
# Configure SEN6x-sensor.
#
# Run "from tools import sen6x_config" and then one of the commands printed.
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

from sensors.sen6x import SEN6X
from sensors.aht20 import AHT20
from datacollector import g_config
import pins
import hw_helper

# --- configuration function   -----------------------------------------------

def run(duration=60,ppm=None,persist=False):
  """ configure sen6x """

  global textlabel

  # start cont. measurement and wait for initialization
  c_sensor.sen6x.start_measurement()
  g_logger.print("waiting 30s for sensor-initialization...")
  time.sleep(30)
  g_logger.print("...done")

  # operate for 10 minutes in clean air
  g_logger.print(f"operating for {duration} minutes...")
  g_logger.set_target(None)
  header = f"ts,{SEN6X.HEADERS_BASE}"
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
    # discard all data except (c, t, h)
    csv_sen6x = c_sensor.read(data,[]).split(',')[:3]
    csv += ','.join(csv_sen6x)
    if t_sensor:
      csv += f",{t_sensor.read(data,[])}"
      t_off = round(data["SEN66"]["t"] - data["aht20"]["t"],1)
      print(f"{csv},{t_off}")
    else:
      print(csv)

    mins,secs = divmod(time_left,60)
    if not secs:
      print(f"time left: {mins} minutes")

    # update OLED if connected
    if textlabel:
      t_left = f"{mins:02d}:{secs:02d}"
      textlabel.text = f"Rest:  {t_left}\nC/SE6: {data["SEN66"]["C/SE6:"]}"
      if t_sensor:
        textlabel.text += f"\nT-off: {t_off:0.1f}°C"

  # perform configuration
  g_logger.set_target('console')
  c_sensor.sen6x.stop_measurement()

  if persist:
    if not ppm is None:
      c_sensor.sen6x.force_co2_recalibration(ppm)
  else:
    g_logger.print("settings unchanged")

# --- wrapper for autorun via src/sen6x_config   -----------------------------

def autorun():
  """ automatically run in update-mode """

  duration = getattr(g_config,"SEN6X_CONFIG_DURATION",60)
  ppm      = getattr(g_config,"SEN6X_CONFIG_PPM_MIN",418)
  
  g_logger.print(f"starting: run(duration={duration},")
  g_logger.print(f"              ppm={ppm},")
  g_logger.print(f"              persist=True)")

  run(duration=duration,
      ppm=ppm,
      persist=True)

# --- code executed during import   ------------------------------------------

# Initialse i2c busses for use by sensors and RTC
i2c_busses = hw_helper.init_i2c(pins,g_config,g_logger)

if not i2c_busses[0] and not i2c_busses[1]:
  g_logger.print("error: no i2c-bus detected. Config not possible!!!")

else:
  # use OLED if available
  try:
    oled_display = hw_helper.init_oled(i2c_busses,g_config,g_logger)
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
  g_config.SEN6X_SAMPLES = 1
  g_config.STROBE_MODE = False
  g_config.INTERVAL = SAMPLE_INTERVAL

  c_sensor = SEN6X(g_config,i2c_busses)
  c_sensor.sen6x.stop_measurement()
  print("example usage (see docs for details):\n")
  print("  sen6x_config.run()                      # run for 60 minutes")
  print("  sen6x_config.run(duration=10,")
  print("                   ppm=418,")
  print("                   persist=True)          # dito, but save config")
