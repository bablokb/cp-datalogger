#-----------------------------------------------------------------------------
# Gateway-task: transmit data to upstream
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()

def run(config, app, msg_type, values):
  """ transmit data to upstream """

  app.transmitter.process_data(msg_type, values)
