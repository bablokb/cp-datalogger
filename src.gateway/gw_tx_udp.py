#-----------------------------------------------------------------------------
# UDP gateway sender class. This sender relays data to a central UDP-receiver.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import time

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()
from wifi_impl_builtin import WifiImpl

# --- UDPSender class   ------------------------------------------------------

class UDPSender:
  """ UDPSender class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """
    g_logger.print(f"UDPSender: initializing")
    self._wifi = WifiImpl()

  # --- get time from upstream   ---------------------------------------------

  def get_time(self):
    """ query time: return time-stamp or None """
    return None

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data  """

    g_logger.print("UDPSender: processing sensor-data...")
    start = time.monotonic()
    g_logger.print("UDPSender: sending data...")
    self._wifi.sendto(bytes(','.join(values)+'\n',"UTF-8"),
                self._config.UDP_HOST,self._config.UDP_PORT)
    duration = time.monotonic()-start
    g_logger.print(f"UDPSender: duration: {duration}s")

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. Ignore request """

    g_logger.print(f"UDPSender: ignoring shutdown-request")
    return False
