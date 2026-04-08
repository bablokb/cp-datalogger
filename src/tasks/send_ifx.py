#-----------------------------------------------------------------------------
# Task: send data directly to an InfluxDB.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from log_writer import Logger
g_logger = Logger()
from ifx_if import IFX_If

# --- process data   -------------------------------------------------------

def run(config,app):
  """ send data using IFX """

  try:
    # this will return an existing singleton
    g_logger.print("send_ifx: fetching IFX_If-singleton...")
    ifx_if = IFX_If(None)
  except:
    g_logger.print("send_ifx: ... failed.")
    g_logger.print("send_ifx: creating IFX_If-singleton")
    ifx_if = IFX_If(config)

  g_logger.print("Send_ifx: processing sensor-data...")
  ifx_if.send_data(app.record+'\n')
