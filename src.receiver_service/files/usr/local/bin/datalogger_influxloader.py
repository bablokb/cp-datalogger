#!/usr/bin/python3
#-----------------------------------------------------------------------------
# This program translates the output from datalogger_parser.py to Influxdb line
# protocol.
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
import subprocess
from datetime import datetime as dt

from datalogger_shared import Tools

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
    self._curl  = None

  # --- read input and convert to line protocol   ----------------------------

  def convert_input(self, infile):
    """ process infile """

    for line_json in map(str.rstrip, infile):
      try:
        measurement = json.loads(line_json)
        self._tools.debug(f"{measurement=}")
      except:
        self._tools.debug(f"skipping corrupt record: {line_json}")
        continue
      # every measurement contains 1..n values (individual sensor-outputs)
      for values in measurement["record"]:
        ifx_lp = f'{values["sensor"]},id={measurement["id"]} '
        for i, field in enumerate(values["fields"]):
          ifx_lp += f'{field[0]}={values["data"][i]},'
        ifx_lp = ifx_lp.rstrip(',')
        ifx_lp += f' {int(dt.fromisoformat(measurement["ts"]).timestamp())}\n'
        yield ifx_lp

  # --- post data to InfluxDB using curl   -----------------------------------

  def post_data(self, record, curl_output=sys.stdout):
    """ post data to InfluxDB """

    # read InfluxDB configuration/credentials and create subprocess
    if not self._ifxdb:
      self._ifxdb = IfxDB(self._tools)

      curl_args = ['curl','-v',
         '--header',
         f'Authorization: Token {self._ifxdb.token}',
         '--header',
         'Content-Type: text/plain; charset=utf-8',
         '--header',
         'Accept: application/json',
         '--data-binary', '@-',
         self._ifxdb.endpoint
         ]
      self._tools.debug(f"{curl_args=}")
      self._curl = subprocess.Popen(
        curl_args,
        stdin=subprocess.PIPE,
        stdout=curl_output,
        encoding='utf-8')

    self._curl.stdin.write(record)

  # --- flush data and close process   ---------------------------------------

  def flush(self):
    """ flush pipes """
    if self._curl:
      self._curl.stdin.flush()
      self._curl.stdin.close()
      # Wait for process completion
      self._curl.wait()

  # --- main loop   ----------------------------------------------------------

  def run(self, infile, outfile):
    """ process all data """
    for data in self.convert_input(infile):
      if outfile is None:
        self.post_data(data)
      else:
        outfile.write(data)
    if outfile is None:
      self.flush()
    else:
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
                      default=None, nargs='?',
                      help='output-file (default: curl, use - for stdout')

  args = parser.parse_args()
  loader = None
  try:
    if args.infile == '-':
      infile = sys.stdin
    else:
      infile = open(args.infile,"rt")

    if args.outfile == '-':
      outfile = sys.stdout
    elif not args.outfile is None:
      outfile = open(args.outfile,"wt")
    else:
      outfile = None

    loader = DataLoader(args)
    #loader.convert_input(infile, outfile)
    loader.run(infile, outfile)

  except BaseException as ex:
    raise
    if not isinstance(ex,(BrokenPipeError,KeyboardInterrupt)):
      raise

  finally:
    if loader:
      loader.flush()
