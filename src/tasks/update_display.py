#-----------------------------------------------------------------------------
# Task: update display
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time
import gc

from log_writer import Logger
g_logger = Logger()

def run(config,app):
  """ update display """

  if not config.HAVE_DISPLAY:
    return

  gc.collect()
  if config.SIMPLE_UI:
    app.display.create_simple_view()
    app.display.set_ui_text(app)
  else:
    app.display.create_view(app.formats)
    app.display.set_values(app)

  app.display.refresh()
  g_logger.print("finished refreshing display")

  if config.STROBE_MODE:
    time.sleep(app.display.strobe_wait) # refresh returns before it is finished
