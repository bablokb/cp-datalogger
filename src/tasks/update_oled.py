#-----------------------------------------------------------------------------
# Task: update OLED display. Only usable if no main display is defined.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import time
import gc
import displayio

from log_writer import Logger
g_logger = Logger()

def init_oled(config,app):
  try:
    from oled import OLED
    displayio.release_displays()
    oled_display = OLED(config,app.i2c1,app.i2c0)
    display = oled_display.get_display()
    label   = oled_display.get_textlabel()
    g_logger.print(
      f"OLED created with size {display.width}x{display.height}")
    return label, display.height
  except Exception as ex:
    g_logger.print(f"could not initialize OLED: {ex}")
  
def run(config,app):
  """ update oled display """

  if config.HAVE_DISPLAY or not config.HAVE_OLED:
    return

  gc.collect()
  try:
    textlabel,height = init_oled(config,app)
  except:
    return   # no OLED connected
  
  # show basic infos: 3 lines with 21 columns
  id = config.LOGGER_ID
  dt, ts = app.data['ts_str'].split("T")
  bat_level = app.data['battery']
  status = f"{app.sd_status}{app.lora_status}"
  text = (f"ID:{id:<13.13} S:{status:>2.2}\n" +
          f"{dt} {ts}\n" +
          f"Bat: {bat_level:0.1f}V")

  if height > 32:
    specs = getattr(config,"OLED_VALUES","aht20(temp) aht20(hum)").split()
    for spec in specs:
      text += f"\n{spec}: "
      spec = spec.split('(')
      sensor = spec[0]
      value  = spec[1][:-1]
      text += f"{app.data[sensor][value]}"
  textlabel.text = text

  if config.STROBE_MODE:
    display_time = getattr(config,"OLED_TIME",3)
    time.sleep(display_time)
