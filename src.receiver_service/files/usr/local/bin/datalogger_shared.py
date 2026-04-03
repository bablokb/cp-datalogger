#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Shared methods for datalogger-programs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import configparser
from datetime import datetime as dt
import json
import sys
import time

import requests

import sensor_meta

# --- helper class for generic methods   -------------------------------------

class Tools:
  def __init__(self,config_file='/etc/datalogger.conf',debug=False):
    """ constructor """

    self._cparser = configparser.RawConfigParser(inline_comment_prefixes=(';',))
    self._cparser.optionxform = str
    self._cparser.read(config_file)

    # debug setting - override options from config-file
    if debug is not None:
      self._debug = debug
    else:
      self._debug = self.get_value("GLOBAL","debug","0") == "1"

  # --- print debug messages to stderr   -------------------------------------

  def debug(self, message, force=False):
    """ print debug-messages to stderr """
    if self._debug or force:
      print(message,file=sys.stderr,flush=True)

  # --- read configuration value   --------------------------------------------

  def get_value(self,section,option,default):
    """ get value of config-variables and return given default if unset """

    if self._cparser.has_section(section):
      try:
        value = self._cparser.get(section,option)
      except:
        value = default
    else:
      value = default
    return value

# --- helper class for InfluxDB parameters   ---------------------------------

class IfxDB:
  def __init__(self,tools):
    """ constructor """
    self._tools = tools
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

  # --- read input and convert to line protocol   ----------------------------

  def convert_input(self, infile, encode=True):
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
          self._tools.debug(f"skipping corrupt record: {line}", force=True)
          continue
      # every measurement contains 1..n values (individual sensor-outputs)
      self._tools.debug(f"{measurement=}")
      for values in measurement["record"]:
        ifx_lp = f'{values["sensor"]},id={measurement["id"]} '
        for i, field in enumerate(values["fields"]):
          ifx_lp += f'{field[0]}={values["data"][i]},'
        ifx_lp = ifx_lp.rstrip(',')
        ifx_lp += f' {int(dt.fromisoformat(measurement["ts"]).timestamp())}\n'
        yield bytes(ifx_lp,"utf-8") if encode else ifx_lp

  # --- post data to InfluxDB   ----------------------------------------------

  def post_data(self, infile):
    """ post data to InfluxDB

    infile: open file or list of strings
    """

    headers = {
      'Authorization': f'Token {self.token}',
      'Accept': 'application/json',
      "Content-Type":"application/octet-stream",
      }

    start = time.monotonic()
    response = requests.post(self.endpoint,
                             headers=headers,
                             data=self.convert_input(infile)
                             )
    duration = time.monotonic()-start
    return (response.status_code,response.text,duration)
