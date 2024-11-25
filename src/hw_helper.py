#-----------------------------------------------------------------------------
# Module with helper functions to setup the hardware. This module is
# reused by datacollector.py, admin.py, broadcast.py and gateway.py.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import busio
import sdcardio
import storage

from rtc_ext.ext_base import ExtBase

# --- initialize I2C-busses   ----------------------------------------------

def init_i2c(pins,config,logger):
  """ create and return list of I2C-busses """

  # Standard busses 0 and 1. Bus 0 is shared with UART, so we check
  # the configuration before creating it.
  try:
    i2c = [None,busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)]
  except Exception as ex:
    logger.print(f"could not create i2c1: {ex}")
    i2c = [None,None]
  if getattr(config,"HAVE_I2C0",False):
    try:
      i2c[0] = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
    except:
      logger.print("could not create i2c0 although configured, check wiring!")

  # create busses behind a multiplexer
  if getattr(config,"HAVE_I2C_MP",False):
    import adafruit_tca9548a
    for spec in config.HAVE_I2C_MP.split():
      name,loc = spec.rstrip(')').split('(')
      try:
        bus,addr = loc.split(',')
      except:
        bus = loc
        addr = '0x70'
      bus = i2c[int(bus)]
      addr = int(addr,16)
      if name[-2:] == '46' or name[-3:] == '46A':
        i2c_mp = adafruit_tca9548a.PCA9546A(bus,addr)
      else:
        i2c_mp = adafruit_tca9548a.TCA9548A(bus,addr)
      logger.print(f"adding {len(i2c_mp)} I2C-busses from {name}")
      for i2cbus in i2c_mp:
        i2c.append(i2cbus)

  # return result
  return i2c

# --- initialize SD-card   ---------------------------------------------------

def init_sd(pins,config,logger):
  """ initialize SD-card and return SPI-object """

  spi = None
  if getattr(config,"HAVE_SD",False):
    try:
      spi    = busio.SPI(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO)
      sdcard = sdcardio.SDCard(spi,pins.PIN_SD_CS,1_000_000)
      vfs    = storage.VfsFat(sdcard)
      storage.mount(vfs, "/sd")
      logger.print("SD-card mounted on /sd")
    except Exception as ex:
      if spi:
        spi.deinit()
      raise from ex
  return spi

# --- initialize RTC   -------------------------------------------------------

def init_rtc(config,i2c):
  """ initialize RTC and return RTC-object """

  if getattr(config,"HAVE_RTC",None):
    rtc_spec = config.HAVE_RTC.split('(')
    rtc_name = rtc_spec[0]
    rtc_bus  = int(rtc_spec[1][0])
  else:
    rtc_name = None
    rtc_bus  = 0

  # don't care about exceptions, must be handled by caller
  rtc = ExtBase.create(rtc_name,i2c[rtc_bus],
                                  net_update=getattr(config,"NET_UPDATE",True))
  if rtc_name == "PCF8523":
    if pins.PCB_VERSION > 0:
      rtc.rtc_ext.high_capacitance = True  # uses a 12.5pF capacitor
    if config.HAVE_LIPO:
      rtc.rtc_ext.power_managment = 0b001  # direct switchover Vdd<Vbat
    else:
      rtc.rtc_ext.power_managment = 0b000  # Vdd<Vbat and Vdd < Vth
  return rtc

# --- initialize OLED   ------------------------------------------------------

def init_oled(i2c,config,logger):
  """ init OLED display """

  if getattr(config,'HAVE_OLED',None):
    try:
      from oled import OLED
      odisp = OLED(config,i2c)
      display = odisp.get_display()
      logger.print(
        f"OLED created with size {display.width}x{display.height}")
      return odisp
    except Exception as ex:
      logger.print(f"could not initialize OLED: {ex}")
      raise from ex
  return None
