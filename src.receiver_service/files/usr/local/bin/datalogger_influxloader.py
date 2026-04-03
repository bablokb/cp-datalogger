#!/usr/bin/python3
#-----------------------------------------------------------------------------
# This program reads raw csv-data or output from datalogger_parser.py, converts
# it to the Influxdb line protocol and saves or posts it.
#
# Output format:
#   <sensor>,id=<id> <fname>=<data>... timestamp
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import argparse
import json
import sys
import time
from datetime import datetime as dt

import requests

from datalogger_shared import Tools
import sensor_meta

# --- helper class for InfluxDB parameters   ---------------------------------

class IfxDB:
  def __init__(self,tools):
    """ constructor """
    self.url = tools.get_value("INFLUXDB","url",
                               "http://localhost:8086")
    self.api = tools.get_value("INFLUXDB","api",
                               "api/v2/write")
    self.org = tools.get_value("INFLUXDB","org",
                               "def_org")
    self.bucket = tools.get_value("INFLUXDB","bucket",
                                  "def_bucket")
    self.token = tools.get_value("INFLUXDB","token",
                                  "whatever")
    self.endpoint = (f'{self.url}/{self.api}?org={self.org}&' +
                     f'bucket={self.bucket}&precision=s')

# --- DataLoader class   -----------------------------------------------------

class DataLoader:
  """ load data into InfluxDB """

  def __init__(self,args):
    """ constructor """
    self._tools = Tools(debug=args.debug)
    self._ifxdb = None

  # --- read input and convert to line protocol   ----------------------------

  def convert_input(self, infile):
    """ process infile """

    for line in map(str.rstrip, infile):
      try:
        # try csv first
        measurement = sensor_meta.split_csv(line)
      except:
        # try json (output from datalogger_parser.py)
        try:
          measurement = json.loads(line)
          if not isinstance(measurement,dict):
            raise ValueError()
        except:
          self._tools.debug(f"skipping corrupt record: {line}")
          continue
      # every measurement contains 1..n values (individual sensor-outputs)
      self._tools.debug(f"{measurement=}")
      for values in measurement["record"]:
        ifx_lp = f'{values["sensor"]},id={measurement["id"]} '
        for i, field in enumerate(values["fields"]):
          ifx_lp += f'{field[0]}={values["data"][i]},'
        ifx_lp = ifx_lp.rstrip(',')
        ifx_lp += f' {int(dt.fromisoformat(measurement["ts"]).timestamp())}\n'
        yield bytes(ifx_lp,"utf-8")

  # --- post data to InfluxDB   ----------------------------------------------

  def post_data(self, infile):
    """ post data to InfluxDB

    infile: a generator
    outfile: an open file
    """

    headers = {
      'Authorization': f'Token {self._ifxdb.token}',
      'Accept': 'application/json',
      "Content-Type":"application/octet-stream",
      }

    try:
      start = time.monotonic()
      response = requests.post(self._ifxdb.endpoint,
                               headers=headers,
                               data=infile
                               )
      duration = time.monotonic()-start
      print(f"HTTP-Code: {response.status_code}\nText: {response.text}")
      print(f"duration: {duration}s")
    except Exception as ex:
      print(f"HTTP-POST failed with exception: {ex}")

  # --- main loop   ----------------------------------------------------------

  def run(self, infile, outfile):
    """ process all data """
    if outfile is None:
      # read InfluxDB configuration/credentials
      self._ifxdb = IfxDB(self._tools)
      self.post_data(self.convert_input(infile))
    else:
      for data in self.convert_input(infile):
        outfile.write(data)
    if outfile:
      outfile.flush()

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="DL InfluxDb-Loader")
  parser.add_argument('-d', '--debug', action='store_true',
                      dest='debug', default=False,
                      help="debug-mode (writes to stderr)")
  parser.add_argument('infile', metavar='infile',
                      help='input-file (use - for stdin')
  parser.add_argument('outfile', metavar='outfile',
                      default='HTTP-POST', nargs='?',
                      help='output-file (default: HTTP-POST, use - for stdout')

  args = parser.parse_args()
  loader = None
  try:
    if args.infile == '-':
      infile = sys.stdin
    else:
      infile = open(args.infile,"rt")

    if args.outfile == '-':
      outfile = sys.stdout
    elif args.outfile == 'HTTP-POST':
      outfile = None
    else:
      outfile = open(args.outfile,"wt")

    loader = DataLoader(args)
    loader.run(infile, outfile)

  except BaseException as ex:
    if not isinstance(ex,(BrokenPipeError,KeyboardInterrupt)):
      raise
