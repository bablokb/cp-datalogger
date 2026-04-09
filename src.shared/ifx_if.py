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

  # --- convert record to line-protocol   ------------------------------------

  def _convert_record(self, record):
    """ process record """

    try:
      measurement = sensor_meta.split_csv(record)
    except Exception as ex:
      g_logger.print(f"IFX_If: skipping corrupt record: {record}")
      return None

    # every measurement contains 1..n values (individual sensor-outputs)
    #g_logger.print(f"IFX_If: {measurement=}")
    ifx_lp = ""
    for values in measurement["record"]:
      ifx_lp += f'{values["sensor"]},id={measurement["id"]} '
      for i, field in enumerate(values["fields"]):
        ifx_lp += f'{field[0]}={values["data"][i]},'
      ifx_lp = ifx_lp.rstrip(',')
      ifx_lp += f' {self._unix_from_ts(measurement["ts"])}\n'
    return bytes(ifx_lp,"utf-8")

  # --- post data to InfluxDB   ----------------------------------------------

  def _post_data(self, data):
    """ post data to InfluxDB

    infile: open file or list of strings
    """

    if data is None:
      return (204,"ignoring empty data")

    headers = {
      'Authorization': f'Token {self._token}',
      'Accept': 'application/json',
      "Content-Type":"text/plain; charset=utf-8",
      }

    start = time.monotonic()
    response = self._wifi.post(self._endpoint,
                             headers=headers,
                             data=data
                             )
    duration = time.monotonic()-start
    status_code = response.status_code
    g_logger.print(f"IFX_If: HTTP-Code: {status_code}")
    g_logger.print(f"IFX_If: duration: {duration}s")
    try:
      response.socket.close()
    except Exception as ex:
      g_logger.print(f"could not close socket: {ex}")
    try:
      response.close()
    except Exception as ex2:
      g_logger.print(f"could not close response: {ex2}")
    return status_code

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
    rc = True
    i = 1
    with open(self._buffer_file,"rt") as infile:
      for record in infile:
        try:
          code = self._post_data(self._convert_record(record))
          if code != 204:
            g_logger.print(f"record {i}: post to InfluxDB failed with {code}")
          rc = rc and code == 204
        except Exception as ex:
          g_logger.print(f"IFX_If: failed with {ex}")
          rc = False
          break
        i += 1

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
      code = self._post_data(self._convert_record(record))
      if code != 204:
        raise RuntimeError(f"IFX_If: post to InfluxDB failed with {code}")
    except Exception as ex:
      g_logger.print(f"IFX_If: failed with {ex}")
      g_logger.print(f"IFX_If: appending current data to buffer file")
      with open(self._buffer_file,"at") as file:
        file.write(record)
