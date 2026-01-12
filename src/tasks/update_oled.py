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

import hw_helper

def run(config,app):
  """ update oled display """

  if config.HAVE_DISPLAY or not config.HAVE_OLED:
    return

  gc.collect()
  try:
    oled = hw_helper.init_oled(app.i2c,config,g_logger)
    if not oled:
      return
    textlabel = oled.get_textlabel()
    height   = oled.get_display().height
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
    # specs: "sensor(label) sensor(label)..."
    specs = getattr(config,"OLED_VALUES","aht20(T/AHT:) aht20(H/AHT:)").split()
    for spec in specs:
      sensor,label = spec.rstrip(')').split('(')
      if sensor in app.data:
        data = app.data[sensor]
        if isinstance(data,list):
          # special case: data is list, show only first entry
          data = data[0]
        if isinstance(data,dict):
          # for dict-data, the label is also the key
          text += f"\n{label} {data[label]}"
        else:
          text += f"\n{label} {data}"
  textlabel.text = text

  if config.STROBE_MODE or config.INTERVAL > 60:
    display_time = getattr(config,"OLED_TIME",3)
    time.sleep(display_time)
