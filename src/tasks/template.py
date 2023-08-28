#-----------------------------------------------------------------------------
# Task: template
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config,app):
  """ do the needful """

  # run only once a day after 18:00
  h = data["ts"].tm_hour
  m = data["ts"].tm_min

  if h < 18 or h > 18:
    return
  elif m > 5:
    return

  # execute the task...

