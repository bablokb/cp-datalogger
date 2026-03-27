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
from datetime import datetime as dt

def process_input(infile=sys.stdin, outfile=sys.stdout):
  """ process infile """

  for line_json in map(str.rstrip, infile):
    line = json.loads(line_json)
    for values in line["record"]:
      ifx_lp = f'{values["sensor"]},id={line["id"]} '
      for i, field in enumerate(values["fields"]):
        ifx_lp += f'{field[0]}={values["data"][i]},'
      ifx_lp = ifx_lp.rstrip(',')
      ifx_lp += f' {int(dt.fromisoformat(line["ts"]).timestamp())}\n'
      outfile.write(ifx_lp)

# --- main program   ---------------------------------------------------------

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description="DL InfluxDb-Loader")
  parser.add_argument('-d', '--debug', action='store_true',
                      dest='debug', default=False,
                      help="debug-mode (writes to stderr)")
  parser.add_argument('infile', metavar='infile',
                      default='-', nargs='?', help='input-file (use - for stdin')
  parser.add_argument('outfile', metavar='outfile',
                      default='-', nargs='?', help='output-file (use - for stdout')

  args = parser.parse_args()
  try:
    if args.infile == '-':
      infile = sys.stdin
    else:
      infile = open(args.infile,"rt")
    if args.outfile == '-':
      outfile = sys.stdout
    else:
      outfile = open(args.outfile,"wt")
    process_input(infile,outfile)
  except BaseException as ex:
    dl_parser.cleanup()
    if not isinstance(ex,(BrokenPipeError,KeyboardInterrupt)):
      dl_parser.print_err(f"exception: {ex}")
      raise

process_input()
