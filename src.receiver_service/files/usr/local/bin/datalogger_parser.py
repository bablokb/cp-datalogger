#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Data parser for datalogger records.
#
# This script emits a JSON-structure for every record in the csv-file with
# the following structure (in a single line):
#{
#   "ts": "2024-01-09T09:58:05",
#   "id": "v2100",
#   "record:": [
#     { "sensor": "battery",
#       "data": [2.57]
#     }, {
#       "sensor": "aht20",
#       "data": [18.9,50]
#     }, {
#       "sensor": "bh1750",
#       "data": [80]
#     }, {
#       "sensor": "pdm",
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

import sensor_meta

class DataParser:
  def __init__(self, filename, debug=False):
    """ constructor """
    self._filename = filename
    self._debug = debug

  # --- cleanup   ------------------------------------------------------------

  def cleanup(self):
    """ cleanup ressources """
    pass

  # --- print error messages to stderr   -------------------------------------

  def print_err(self,*args):
    """ print to stderr """
    if self._debug:
      print(*args,file=sys.stderr,flush=True)

  # --- main processing loop   -----------------------------------------------

  def run(self):
    """ main processing loop """

    with open(self._filename,"rt") as file:
      for record in file:
        if not record or record[0] == "#":  # skip empty lines and comments
          continue
        # parse single record
        data = sensor_meta.split_csv(record.strip("\n"))
        print(json.dumps(data))

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
  except BaseException as ex:
    dl_parser.print_err(f"exception: {ex}")
    dl_parser.cleanup()
    if not isinstance(ex,KeyboardInterrupt):
      raise
