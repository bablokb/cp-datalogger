#!/usr/bin/python3
#-----------------------------------------------------------------------------
# Shared methods for datalogger-programs.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import sys
import configparser

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
