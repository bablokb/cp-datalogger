#-----------------------------------------------------------------------------
# Setup and operation of TCP transmission. This class is used by
# the tasks send_tcp and the gateway transmitter gw_tx_tcp.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os
import time

from log_writer import Logger
g_logger = Logger()
from singleton import singleton
from wifi_impl_builtin import WifiImpl

@singleton
class TCP_If:
  """ Low-level TCP transmission """

  # --- constructor   --------------------------------------------------------

  def __init__(self,config):
    """ constructor """

    # Calling the constructor with None will return the singleton, if it
    # exists. If not, bail out: the app has to retry and provide all arguments.
    if config is None:
      raise ValueError("config is None")

    self._config = config
    self._wifi = WifiImpl()

    if self._config.HAVE_SD:
      self._buffer_file = "/sd/tx_buffer.csv"
    else:
      try:
        os.listdir("/saves")
        self._buffer_file = "/saves/tx_buffer.csv"
      except:
        self._buffer_file = None
    g_logger.print(f"TCP_If: using buffer file: {self._buffer_file}")

  # --- send buffered data   -------------------------------------------------

  def send_buffered_data(self):
    """ send buffered data """

    if not self._buffer_file:  # no SD/save-partition, no buffered data
      g_logger.print("TCP_If: no buffer file")
      return True

    # check if buffer file exists
    try:
      status = os.stat(self._buffer_file)
      size = status[6]
      if size == 0:
        g_logger.print(f"TCP_If: empty file {self._buffer_file}")
        os.remove(self._buffer_file)
        os.sync()
        return True
      else:
        g_logger.print(f"TCP_If: size of buffered data: {size}")
    except:
      # file does not exist
      g_logger.print(f"TCP_If: no data file {self._buffer_file}")
      return True

    # send buffer file in line mode
    host = self._config.TCP_HOST
    port = self._config.TCP_PORT
    g_logger.print(f"TCP_If: re-sending buffered data to {host}:{port}...")
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
        g_logger.print(f"TCP_If: re-sending: {record} ...")
        try:
          socket, n = self._wifi.send(
            bytes(record,"UTF-8"),
            self._config.TCP_HOST,self._config.TCP_PORT,
            socket=socket)
          g_logger.print(f"TCP_If: ... sent {n} bytes")
          rc = n == len(record)
        except Exception as ex:
          g_logger.print(f"TCP_If: ... failed with exception: {ex}")
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

  def send_data(self, record):
    """ process data, single record  """

    start = time.monotonic()

    # check for pending records
    if self._buffer_file and not self.send_buffered_data():
      # sending failed, so just append current record and stop processing
      g_logger.print("TCP_If: appending current data to buffer-file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
      duration = time.monotonic()-start
      g_logger.print(f"TCP_If: duration: {duration}s")
      return

    # process current record: convert values to bytes and send them
    g_logger.print(f"TCP_If: sending current data: {record}")
    socket = None
    try:
      socket, n = self._wifi.send(
        bytes(record,"UTF-8"),
        self._config.TCP_HOST,self._config.TCP_PORT,
        socket=socket)
      g_logger.print(f"TCP_If: ... sent {n} bytes")
      rc = n == len(record)
    except Exception as ex:
      g_logger.print(f"TCP_If: ... failed with exception: {ex}")
      rc = False
    if socket:
      socket.close()
    duration = time.monotonic()-start
    if not rc and self._buffer_file:
      g_logger.print("TCP_If: appending current data to buffer-file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
    g_logger.print(f"TCP_If: duration: {duration}s")
