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
import sys

from datalogger_shared import Tools, IfxDB

# --- DataLoader class   -----------------------------------------------------

class DataLoader:
  """ load data into InfluxDB """

  def __init__(self,args):
    """ constructor """
    self._tools = Tools(debug=args.debug)

  # --- main loop   ----------------------------------------------------------

  def run(self, infile, outfile):
    """ process all data """
    ifxdb = IfxDB(self._tools)
    if outfile is None:
      # read InfluxDB configuration/credentials
      code,text,duration = ifxdb.post_data(infile)
      print(f"HTTP-Code: {code}\nText: {text}")
      print(f"duration: {duration}s")
    else:
      for data in ifxdb.convert_input(infile,encode=False):
        outfile.write(data)
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
