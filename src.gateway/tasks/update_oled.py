#-----------------------------------------------------------------------------
# Gateway-task: update OLED display
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, msg_type, values):
  """ update OLED """

  if not (getattr(config,"HAVE_OLED",False) and app.oled):
    return
  else:
    app.update_oled(values)
