#-----------------------------------------------------------------------------
# Read configuration and set defaults.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import gc

class Settings:
  def __init__(self,logger):
    """ constructor """
    self._logger = logger

  def import_config(self):
    """ import config-module and make variables attributes """
    import config

    # set defaults
    self.HAVE_PM       = True
    self.SHUTDOWN_HIGH = True
    self.HAVE_RTC      = "PCF8523(1)"
    self.HAVE_SD       = True
    self.HAVE_I2C0     = False
    self.HAVE_I2C_MP   = None
    self.HAVE_LIPO     = False
    self.HAVE_DISPLAY  = None
    self.HAVE_LORA     = False
    self.HAVE_OLED     = None

    # RTC related
    self.NET_UPDATE  = False   # update RTC from time-server if time is invalid
    self.SAVE_WAKEUP = False   # save wakup-time on SD (workaround for buggy batteries)

    #sample-mode and interval/time-table
    self.STROBE_MODE = True      # strobe-mode or continuous-mode
    self.INTERVAL    = 900       # interval (in seconds)
    self.TIME_TABLE  = None      # no time-table

    # test (dev) mode settings
    self.TEST_MODE        = False
    self.BLINK_START      = 3      # blink n times  before sensor-readout
    self.BLINK_TIME_START = 0.5    # blink duration before sensor-readout
    self.BLINK_END        = 5      # blink n times  after  sensor-readout
    self.BLINK_TIME_END  = 0.25    # blink duration after  sensor-readout

    # various
    self.CSV_FILENAME        = "/sd/log_{ID}_{YMD}.csv"
    self.CSV_HEADER_EXTENDED = False
    self.SENSORS_CSV_ONLY    = ""
    self.SHOW_UNITS          = True   # show units in dump_data
    self.SIMPLE_UI           = False  # use tabular UI
    self.FONT_DISPLAY        = 'DejaVuSansMono-Bold-18-subset'

    # update configuration variables from imported config.py
    for var in dir(config):
      if var[0] != '_':
        self._logger.print(f"{var}={getattr(config,var)}")
        setattr(self,var,getattr(config,var))
    config = None

    # in case we are running within a gateway context:
    if not hasattr(self,"LOGGER_ID"):
      self.LOGGER_ID = "NOID"
    if not hasattr(self,"LOGGER_NAME"):
      self.LOGGER_NAME = "NONAME"
    if not hasattr(self,"LOGGER_TITLE"):
      self.LOGGER_TITLE = f"{self.LOGGER_ID}: {self.LOGGER_NAME}"

    if hasattr(self,"HAVE_PCB"):   # compatibility to old configurations
      self.HAVE_PM = self.HAVE_PCB
      if not self.HAVE_PCB and not hasattr(config,"HAVE_RTC"):
        # HAVE_PCB==False and HAVE_RTC not set
        self.HAVE_RTC = None

    gc.collect()
