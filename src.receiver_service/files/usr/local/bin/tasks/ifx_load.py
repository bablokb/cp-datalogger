#-----------------------------------------------------------------------------
# Receiver task: ifx_load
# 
# This task loads the record to an Influx-DB
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import os

from .base_task import BaseTask
from datalogger_shared import IfxDB

class IFX_LOAD(BaseTask):
  def __init__(self, tools):
    """ constructor """
    super().__init__(tools)
    self._ifxdb = IfxDB(tools)
    self._buffer_file =  self.tools.get_value(
      "INFLUXDB",
      "buffer_file","/var/lib/datalogger/ifx_buffer.csv")

  def _send_pending(self):
    """ send pending data """

    # check if buffer file exists
    try:
      status = os.stat(self._buffer_file)
      size = status[6]
      if size == 0:
        self.tools.debug(f"ifx_load: empty file {self._buffer_file}")
        os.remove(self._buffer_file)
        os.sync()
        return True
      else:
        self.tools.debug(f"ifx_load: size of buffered data: {size}")
    except:
      # file does not exist
      self.tools.debug(f"ifx_load: no data file {self._buffer_file}")
      return True

    # send buffer file. Since InfluxDB can handle identical data,
    # we don't bother about partly successful transfers
    with open(self._buffer_file,"rt") as infile:
      try:
        code,text,duration = self._ifxdb.post_data(infile)
        self.tools.debug(f"HTTP-Code: {code}\nText: {text}")
        self.tools.debug(f"duration: {duration}s")
        if code != 204:
          raise RuntimeError(f"post to InfluxDB failed with {code}")
        rc = True
      except Exception as ex:
        self.tools.debug(f"ifx_load: failed with {ex}")
        rc = False

    # remove buffer file if transfer was successful
    if rc:
      os.remove(self._buffer_file)
    return rc

  def run(self, record):
    """ print record """

    if not self._send_pending():
      # send of pending data failed, so just add current record
      self.tools.debug(f"ifx_load: appending current data to buffer file")
      with open(self._buffer_file,"at") as file:
        file.write(record.decode())
      return

    try:
      code,text,duration = self._ifxdb.post_data([record.decode()])
      self.tools.debug(f"HTTP-Code: {code}\nText: {text}")
      self.tools.debug(f"duration: {duration}s")
      if code != 204:
        raise RuntimeError(f"post to InfluxDB failed with {code}")
    except Exception as ex:
      self.tools.debug(f"ifx_load: failed with {ex}")
      self.tools.debug(f"ifx_load: appending current data to buffer file")
      with open(self._buffer_file,"at") as file:
        file.write(record.decode())
