#-----------------------------------------------------------------------------
# TCP gateway sender class. This sender relays data to a central TCP-receiver.
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
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os
import time

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
    if self._config.HAVE_SD:
      self._buffer_file = "/sd/tx_buffer.csv"
    else:
      try:
        os.listdir("/saves")
        self._buffer_file = "/saves/tx_buffer.csv"
      except:
        self._buffer_file = None
    g_logger.print(f"TCPSender: using buffer file: {self._buffer_file}")

  # --- hardware-setup   -----------------------------------------------------

  def setup(self,i2c):
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

    if not self._buffer_file:  # no SD/save-partition, no buffered data
      g_logger.print("TCPSender: no buffer file")
      return True

    # check if buffer file exists
    try:
      status = os.stat(self._buffer_file)
      size = status[6]
      if size == 0:
        g_logger.print(f"TCPSender: empty file {self._buffer_file}")
        os.remove(self._buffer_file)
        os.sync()
        return True
      else:
        g_logger.print(f"TCPSender: size of buffered data: {size}")
    except:
      # file does not exist
      g_logger.print(f"TCPSender: no data file {self._buffer_file}")
      return True

    # send buffer file in line mode
    host = self._config.TCP_HOST
    port = self._config.TCP_PORT
    g_logger.print(f"TCPSender: sending buffered data to {host}:{port}...")
    socket = None
    buffer_file_new = None
    rc_all = True

    i = 0
    with open(self._buffer_file,"rt") as file:
      for record in file:
        if not rc_all:
          # we failed already, # so move records to BUFFER_FILE_NEW
          if not buffer_file_new:
            buffer_file_new = open(self._buffer_file+"new","at")
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
            if socket:
              socket.close()
            return False
          elif not buffer_file_new:
            buffer_file_new = open(self._buffer_file+"new","at")
          # keep this record in buffer_file_new
          buffer_file_new.write(record)
        i += 1

    # at this stage, BUFFER_FILE is processed
    if socket:
      socket.close()
    os.remove(self._buffer_file)
    if buffer_file_new:
      # move failed records to BUFFER_FILE, will be processed next time
      buffer_file_new.flush()
      buffer_file_new.close()
      os.rename(self._buffer_file+"new",self._buffer_file)
      os.sync()

    # return send-status
    return rc_all

  # --- process data   -------------------------------------------------------

  def process_data(self, msg_type, values):
    """ process data, single record  """

    start = time.monotonic()
    record = ','.join(values)+'\n'
    g_logger.print("TCPSender: processing sensor-data...")
    g_logger.print(f"TCPSender: sending data: {record}")

    # check for pending records
    if self._buffer_file and not self._send_buffered_data():
      # sending failed, so just append current record and stop processing
      g_logger.print("TCPSender: appending data to buffer-file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
      duration = time.monotonic()-start
      g_logger.print(f"TCPSender: duration: {duration}s")
      return

    # process current record: convert values to bytes and send them
    socket = None
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
    if socket:
      socket.close()
    duration = time.monotonic()-start
    if not rc and self._buffer_file:
      g_logger.print("TCPSender: appending data to buffer-file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
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
