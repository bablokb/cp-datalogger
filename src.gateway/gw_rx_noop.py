#-----------------------------------------------------------------------------
# A gateway receiver doing nothing (for testing).
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()

# --- NoopReceiver class   ------------------------------------------------

class NoopReceiver:
  """ NoopReceiver class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """
    g_logger.print(f"NoopReceiver: initializing no hardware")

  # --- receive data   -------------------------------------------------------

  def receive_data(self):
    """ receive data """
    return None

  # --- reply to broadcast-messages   ----------------------------------------

  def handle_broadcast(self,values, node_sender):
    """ process broadcast requests """
    return False

  # --- reply to query-time-messages   ---------------------------------------

  def handle_time_request(self,values, node_sender):
    """ process time requests """
    return False

  # --- reply to data messages   ---------------------------------------------

  def handle_data(self, msg_type, values, node_sender):
    """ process data messages """
    return False

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system. In our case, ignore the request """

    g_logger.print(f"NoopReceiver: ignoring shutdown-request")
    return False
