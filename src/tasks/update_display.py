#-----------------------------------------------------------------------------
# Task: update display
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
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
  else:
    app.display.create_view(app.formats)

  if config.SIMPLE_UI:
    app.display.set_ui_text(app.csv_header,app.record)
  else:
    if len(app.values) < len(app.formats):
      # fill in unused cells
      app.values.extend(
        [None for _ in range(len(app.formats)-len(app.values))])
    elif len(app.values) > len(app.formats):
      # remove extra values
      del app.values[len(app.formats):]

    dt, ts = app.data['ts_str'].split("T")
    footer = f"at {dt} {ts} {app.save_status}"
    app.display.set_values(app.values,footer)

  app.display.refresh()
  g_logger.print("finished refreshing display")

  if config.STROBE_MODE:
    time.sleep(3)              # refresh returns before it is finished
