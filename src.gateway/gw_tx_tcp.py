#-----------------------------------------------------------------------------
# TCP gateway sender class. This sender relays data to a central TCP-receiver.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os
import time

BUFFER_FILE     = "/sd/tx_buffer.csv"
BUFFER_FILE_NEW = "/sd/tx_buffer_new.csv"

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

    # check if buffer file exists
    try:
      status = os.stat(BUFFER_FILE)
      size = status[6]
      if size == 0:
        g_logger.print(f"TCPSender: empty file {BUFFER_FILE}")
        os.remove(buffer_file)
        os.sync()
        return
      else:
        g_logger.print(f"TCPSender: size of buffered data: {size}")
    except:
      # file does not exist
      g_logger.print(f"TCPSender: no data file {BUFFER_FILE}")
      return

    # send buffer file in line mode
    host = self._config.TCP_HOST
    port = self._config.TCP_PORT
    g_logger.print(f"TCPSender: sending buffered data to {host}:{port}...")
    socket = None
    buffer_file_new = None
    rc_all = True

    i = 0
    with open(BUFFER_FILE,"rt") as file:
      for record in file:
        if not rc_all:
          # we failed already, # so move records to BUFFER_FILE_NEW
          if not buffer_file_new:
            buffer_file_new = open(BUFFER_FILE_NEW,"at")
          buffer_file_new.write(record)
          continue

        # convert values to bytes and send them
        g_logger.print(f"TCPSender: sending: {record} ...")
        try:
          socket, n = self._wifi.send(
            bytes(record,"UTF-8"),
            self._config.TCP_HOST,self._config.TCP_PORT,
            socket=socket)
          g_logger.print(f"TCPSender: ... sent {n} bytes")
          rc = n == len(record)
        except Exception as ex:
          g_logger.print(f"TCPSender: ... failed with exception: {ex}")
          rc = False

        # check result
        rc_all = rc and rc_all
        if not rc:
          if i == 0:
            # failed at the first record, bail out
            return False
          elif not buffer_file_new:
            buffer_file_new = open(BUFFER_FILE_NEW,"at")
          # keep this record in buffer_file_new
          buffer_file_new.write(record)
        i += 1

    # at this stage, BUFFER_FILE is processed
    if socket:
      socket.close()
    os.remove(BUFFER_FILE)
    if buffer_file_new:
      # move failed records to BUFFER_FILE, will be processed next time
      buffer_file_new.flush()
      buffer_file_new.close()
      os.rename(BUFFER_FILE_NEW,BUFFER_FILE)
      os.sync()

    # return send-status
    return rc_all

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data, single record  """

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
