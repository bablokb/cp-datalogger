#-----------------------------------------------------------------------------
# Noop gateway sender class.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()

# --- NoopSender class   -----------------------------------------------------

class NoopSender:
  """ NoopSender class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """
    g_logger.print(f"NoopSender: initializing")

  # --- get time from upstream   ---------------------------------------------

  def get_time(self):
    """ query time: return time-stamp or None """
    return None

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data  """

    g_logger.print("NoopSender: processing sensor-data...")
    start = time.monotonic()
    duration = time.monotonic()-start
    g_logger.print(f"NoopSender: duration: {duration}s")

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. Ignore request """

    g_logger.print(f"NoopSender: ignoring shutdown-request")
    return False
