#-----------------------------------------------------------------------------
# Task: print data to log
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config,app):
  """ dump data to console/log """

  if not config.SHOW_UNITS:
    print(app.record)               # print to console (!), not g_logger
    return

  columns = app.csv_header.split('#')[-1].split(',')
  merged = zip(columns,app.record.split(','))
  for label,value in merged:
    space = '\t\t' if len(label) < 9 else '\t'
    g_logger.print(f"{label}:{space}{value}")
