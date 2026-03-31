#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Data parser for datalogger records.
#
# This script emits a JSON-structure for every record in the csv-file with
# the following structure (in a single line):
#{
#   "ts": "2024-01-09T09:58:05",
#   "id": "v2100",
#   "record": [
#     { "sensor": "battery",
#       "fields": [["voltage","V"]],
#       "data": [2.57]
#     }, {
#       "sensor": "aht20",
#       "fields": [["temp","°C"],["hum","%rH"]],
#       "data": [18.9,50]
#     }, {
#       "sensor": "bh1750",
#       "fields": [["lum","lx"]],
#       "data": [80]
#     }, {
#       "sensor": "pdm",
#       "fields": [["noise",""]],
#       "data": [79]
#     }
#   ]
# }
#
# To post-process the data, pipe the output to a script, read from stdin,
# load the data-records with `json.loads(line)` and do whatever is needed.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

DCODE_COLUMN = 2  # ts,id,dcode,...

import sys
import argparse
import json

from datalogger_shared import Tools

import sensor_meta

class DataParser:
  def __init__(self, filename, debug=False):
    """ constructor """
    self._tools = Tools(debug=debug)
    self.debug = self._tools.debug
    self._filename = filename

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- main processing loop   -----------------------------------------------

  def run(self):
    """ main processing loop """

    with open(self._filename,"rt") as file:
      i = 0
      for record in file:
        i += 1
        if not record or record[0] == "#":  # skip empty lines and comments
          continue
        # parse single record
        try:
          data = sensor_meta.split_csv(record.strip("\n"))
          print(json.dumps(data))
        except Exception as ex:
          self.debug(f"ignoring invalid record {i}: {record}", force=True)

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="DL Parser")
  parser.add_argument('-d', '--debug', action='store_true',
                      dest='debug', default=False,
                      help="debug-mode (writes to stderr)")
  parser.add_argument('infile', metavar='infile',help='input-file')

  args = parser.parse_args()    
  try:
    dl_parser = DataParser(filename=args.infile,
                           debug=args.debug)
    dl_parser.run()
    dl_parser.cleanup()
  except BaseException as ex:
    dl_parser.cleanup()
    if not isinstance(ex,(BrokenPipeError,KeyboardInterrupt)):
      dl_parser.debug(f"exception: {ex}")
      raise
