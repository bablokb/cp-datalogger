#-----------------------------------------------------------------------------
# IFX gateway sender class. This sender sends data directly to an InfluxDB.
#
# There are two (exclusive) options for operation:
#   - add tx_send to TASKS
#   - add buffer_data to TASKS
#
# The first option will send data directly to upstream and only buffer data
# if upstream is not available. Just before shutdown, the gateway will try
# to send any pending data from the buffer again. Use this option if live
# data is required at the upstream site.
#
# The second option will buffer data and only send data to upstream just
# before shutdown. Use the second option if sending to upstream is slow, since
# this will block the gateway. This also requires that the gateway is regularly
# restarted.
#
# Additionally, you can add tx_send to I_TASKS. These tasks are executed during
# gateway idle time. This will only process buffered data and only send data
# in small amounts to ensure that the gateway is not overloaded.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os
import time

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()
from ifx_if import IFX_If

# --- IFXSender class   ------------------------------------------------------

class IFXSender:
  """ IFXSender class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config
    try:
      # this will return an existing singleton
      g_logger.print("IFXSender: fetching IFX_If-singleton...")
      self._ifx_if = IFX_If(None)
    except:
      g_logger.print("IFXSender: ... failed.")
      g_logger.print("IFXSender: creating IFX_If-singleton")
      self._ifx_if = IFX_If(config)

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c):
    """ initialize hardware """
    g_logger.print(f"IFXSender: initializing")

  # --- get time from upstream   ---------------------------------------------

  def get_time(self):
    """ query time: return time-stamp or None """
    return None

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data, single record  """

    start = time.monotonic()
    if msg_type is None:
      g_logger.print("IFXSender: processing pending data...")
      self._ifx_if.send_pending(count=1)
    else:
      g_logger.print("IFXSender: processing sensor-data...")
      self._ifx_if.send_data(','.join(values)+'\n', pending=False)

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system request.
    This sends buffered data (if available). """

    g_logger.print(f"IFXSender: shutdown(): sending buffered data")
    try:
      self._ifx_if.send_pending()
    except Exception as ex:
      g_logger.print(f"IFXSender: exception while sending data: {ex}")
    return False
