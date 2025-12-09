#-----------------------------------------------------------------------------
# Gateway-task: transmit data to upstream
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, values):
  """ transmit data to upstream """

  app.transmitter.process_data(values)
