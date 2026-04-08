#-----------------------------------------------------------------------------
# A support class for loading data directly to an InfluxDB.
# This class is used by the tasks send_ifx and the gateway transmitter gw_tx_ifx.
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
from secrets import secrets
import sensor_meta

@singleton
class IFX_If:
  """ Low-level transport interface for InfluxDB """

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
      self._buffer_file = "/sd/ifx_buffer.csv"
    else:
      try:
        os.listdir("/saves")
        self._buffer_file = "/saves/ifx_buffer.csv"
      except:
        self._buffer_file = None
    g_logger.print(f"IFX_If: using buffer file: {self._buffer_file}")

    url = config.INFLUXDB_URL
    api = getattr(config,"INFLUXDB_API","api/v2/write")
    org = config.INFLUXDB_ORG
    bucket = config.INFLUXDB_BUCKET
    self._token = secrets.influxdb_token

    self._endpoint = (f'{url}/{api}?org={org}&' +
                     f'bucket={bucket}&precision=s')

  # --- convert timestamp to unix-time   -------------------------------------

  def _unix_from_ts(self,ts):
    """ convert timestamp to unxi-time """

    the_date, the_time = ts.split("T")
    year, month, mday = [int(x) for x in the_date.split("-")]
    the_time = the_time.split(".")[0]
    hours, minutes, seconds = [int(x) for x in the_time.split(":")]

    year_day = -1
    week_day = -1
    week_day = -1
    is_dst   = 0

    return time.mktime(
      (year, month, mday, hours, minutes, seconds, week_day, year_day, is_dst))

  # --- read input and convert to line protocol   ----------------------------

  def convert_input(self, infile, encode=True):
    """ process infile """

    for line in map(str.rstrip, infile):
      try:
        measurement = sensor_meta.split_csv(line)
      except Exception as ex:
        g_logger.print(f"IFX_If: skipping corrupt record: {line}")
        continue
      # every measurement contains 1..n values (individual sensor-outputs)
      #g_logger.print(f"IFX_If: {measurement=}")
      for values in measurement["record"]:
        ifx_lp = f'{values["sensor"]},id={measurement["id"]} '
        for i, field in enumerate(values["fields"]):
          ifx_lp += f'{field[0]}={values["data"][i]},'
        ifx_lp = ifx_lp.rstrip(',')        
        ifx_lp += f' {self._unix_from_ts(measurement["ts"])}\n'
        g_logger.print(f"IFX_If: sending: {ifx_lp}")
        yield bytes(ifx_lp,"utf-8") if encode else ifx_lp

  # --- post data to InfluxDB   ----------------------------------------------

  def _post_data(self, infile):
    """ post data to InfluxDB

    infile: open file or list of strings
    """

    headers = {
      'Authorization': f'Token {self._token}',
      'Accept': 'application/json',
      "Content-Type":"application/octet-stream",
      }

    start = time.monotonic()
    response = self._wifi.post(self._endpoint,
                             headers=headers,
                             data=self.convert_input(infile)
                             )
    duration = time.monotonic()-start
    status_code = response.status_code
    text = response.text
    g_logger.print(f"IFX_If: HTTP-Code: {status_code}\nText: {text}")
    g_logger.print(f"IFX_If: duration: {duration}s")
    try:
      response.socket.close()
      response.close()
    except:
      pass
    return (status_code,text,duration)

  # --- send pending data   --------------------------------------------------

  def _send_pending(self):
    """ send pending data """

    # check if buffer file exists
    try:
      status = os.stat(self._buffer_file)
      size = status[6]
      if size == 0:
        g_logger.print(f"IFX_If: empty file {self._buffer_file}")
        os.remove(self._buffer_file)
        os.sync()
        return True
      else:
        g_logger.print(f"IFX_If: size of buffered data: {size}")
    except:
      # file does not exist
      g_logger.print(f"IFX_If: no pending data file {self._buffer_file}")
      return True

    # send buffer file. Since InfluxDB can handle identical data,
    # we don't bother about partly successful transfers
    with open(self._buffer_file,"rt") as infile:
      try:
        code,text,duration = self._post_data(infile)
        g_logger.print(f"IFX_If: HTTP-Code: {code}\nText: {text}")
        g_logger.print(f"IFX_If: duration: {duration}s")
        if code != 204:
          raise RuntimeError(f"post to InfluxDB failed with {code}")
        rc = True
      except Exception as ex:
        g_logger.print(f"IFX_If: failed with {ex}")
        rc = False

    # remove buffer file if transfer was successful
    if rc:
      os.remove(self._buffer_file)
    return rc

  # --- send single data record   --------------------------------------------

  def send_data(self, record):
    """ send single record (try pending first)  """

    if not self._send_pending():
      # send of pending data failed, so just add current record
      g_logger.print(f"IFX_If: appending current data to buffer file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
      return

    try:
      code,text,duration = self._post_data([record])
      g_logger.print(f"IFX_If: HTTP-Code: {code}\nText: {text}")
      g_logger.print(f"IFX_If: duration: {duration}s")
      if code != 204:
        raise RuntimeError(f"IFX_If: post to InfluxDB failed with {code}")
    except Exception as ex:
      g_logger.print(f"IFX_If: failed with {ex}")
      g_logger.print(f"IFX_If: appending current data to buffer file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
