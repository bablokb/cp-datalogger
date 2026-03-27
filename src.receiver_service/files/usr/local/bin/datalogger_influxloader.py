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

import json
import sys
from datetime import datetime as dt

for line_json in map(str.rstrip, sys.stdin):
  line = json.loads(line_json)
  for values in line["record"]:
    ifx_lp = f'{values["sensor"]},id={line["id"]} '
    for i, field in enumerate(values["fields"]):
      ifx_lp += f'{field[0]}={values["data"][i]},'
    ifx_lp = ifx_lp.rstrip(',')
    ifx_lp += f' {int(dt.fromisoformat(line["ts"]).timestamp())}'
    print(ifx_lp)
