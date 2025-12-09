#-----------------------------------------------------------------------------
# Gateway-task: update OLED display
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, values):
  """ update OLED """

  if not (getattr(config,"HAVE_OLED",False) and app.oled):
    return
  else:
    app.update_oled(values)
