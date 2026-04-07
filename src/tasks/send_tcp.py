#-----------------------------------------------------------------------------
# Task: send data using TCP. See src.receiver/ for an implementation of a
#       suitable receiver.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()
from tcp_if import TCP_If

# --- process data   -------------------------------------------------------

def run(config,app):
  """ send data using TCP """

  try:
    # this will return an existing singleton
    g_logger.print("send_tcp: fetching TCP_If-singleton...")
    tcp_if = TCP_If(None)
  except:
    g_logger.print("send_tcp: ... failed.")
    g_logger.print("send_tcp: creating TCP_If-singleton")
    tcp_if = TCP_If(config)

  g_logger.print("Send_tcp: processing sensor-data...")
  tcp_if.send_data(app.record+'\n')
