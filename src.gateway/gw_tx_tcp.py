#-----------------------------------------------------------------------------
# TCP gateway sender class. This sender relays data to a central TCP-receiver.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os
import time

CHUNK = 1024   # chunk-size for TCP transmission

# --- early configuration of the log-destination   ---------------------------

from log_writer import Logger
g_logger = Logger()
from wifi_impl_builtin import WifiImpl

# --- TCPSender class   ------------------------------------------------------

class TCPSender:
  """ TCPSender class """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """
    self._config = config

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c,spi):
    """ initialize hardware """
    g_logger.print(f"TCPSender: initializing")
    self._wifi = WifiImpl()

  # --- get time from upstream   ---------------------------------------------

  def get_time(self):
    """ query time: return time-stamp or None """
    return None

  # --- send buffered data   -------------------------------------------------

  def _send_buffered_data(self):
    """ send buffered data """

    if not hasattr(self._config,"HAVE_SD"):  # no SD, no buffered daa
      return

    buffer_file = "/sd/tx_buffer.csv"
    try:
      status = os.stat(buffer_file)
      size = status[6]
      if size == 0:
        g_logger.print(f"TCPSender: empty file /sd/tx_buffer.csv")
        os.remove(buffer_file)
        os.sync()
        return
      else:
        g_logger.print(f"TCPSender: size of buffered data: {size}")
    except:
      # file does not exist
      g_logger.print(f"TCPSender: no data file /sd/tx_buffer.csv")
      return

    # fetch all data and send it. Efficient, but not robust.
    host = self._config.TCP_HOST
    port = self._config.TCP_PORT
    g_logger.print(f"TCPSender: sending buffered data to {host}:{port}...")
    sent = 0
    socket = None
    with open(buffer_file,"rb") as file:
      data = file.read(CHUNK)
      g_logger.print(f"TCPSender: sending {len(data)} bytes")
      socket, n = self._wifi.send(data,host,port,socket)
      sent += n
    socket.close()
    g_logger.print(f"TCPSender: total bytes sent: {sent}")
    if sent == size:
      g_logger.print(f"TCPSender: deleting {buffer_file}")
      os.remove(buffer_file)
      os.sync()
    return

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data  """

    g_logger.print("TCPSender: processing sensor-data...")
    start = time.monotonic()
    g_logger.print("TCPSender: sending data...")
    # convert values to bytes and send them
    socket, n = self._wifi.send(bytes(','.join(values)+'\n',"UTF-8"),
                                self._config.TCP_HOST,self._config.TCP_PORT)
    # ignore n, since we can't do anything about an error anyway
    socket.close()
    duration = time.monotonic()-start
    g_logger.print(f"TCPSender: duration: {duration}s")

  # --- shutdown   -----------------------------------------------------------

  def shutdown(self,wakeup):
    """ Shutdown system request.
    This sends buffered data (if available). """

    g_logger.print(f"TCPSender: shutdown(): sending buffered data")
    try:
      self._send_buffered_data()
    except Exception as ex:
      g_logger.print(f"TCPSender: exception while sending data: {ex}")
    return False
