#-----------------------------------------------------------------------------
# Module with helper functions to setup the hardware. This module is
# reused by datacollector.py, admin.py, broadcast.py and gateway.py.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import atexit
import busio
import digitalio
import displayio
import sdcardio
import storage

try:
  from log_config import g_logger
except:
  from log_writer import Logger
  g_logger = Logger('console')

import pins
from rtc_ext.ext_base import ExtBase

# --- atexit processing   ----------------------------------------------------

def at_exit_dio(dio,label):
  """ release digitalio """
  try:
    g_logger.print(f"releasing DIO for {label}")
  except:
    print(f"releasing DIO for {label}")
  try:
    dio.deinit()
  except:
    pass

def at_exit_spi(spi,label):
  """ release spi """
  try:
    # may fail if we want to log to SD
    g_logger.print(f"releasing SPI for {label}")
  except:
    print(f"releasing SPI for {label}")
  try:
    spi.deinit()
  except:
    pass

def at_exit_i2c(i2c):
  """ release i2c-busses """
  try:
    # may fail if we want to log to SD
    g_logger.print(f"releasing {i2c}")
  except:
    print(f"releasing {i2c}")
  for bus in reversed(i2c):
    try:
      bus.deinit()
    except:
      pass

# --- initialize I2C-busses   ----------------------------------------------

def init_i2c(config):
  """ create and return list of I2C-busses """

  # Standard busses 0 and 1. Bus 0 is shared with UART, so we check
  # the configuration before creating it.
  try:
    i2c = [None,busio.I2C(pins.PIN_SCL1,pins.PIN_SDA1)]
    g_logger.print(f"created i2c1")
  except Exception as ex:
    g_logger.print(f"could not create i2c1: {ex}")
    i2c = [None,None]
  if config.HAVE_I2C0:
    try:
      i2c[0] = busio.I2C(pins.PIN_SCL0,pins.PIN_SDA0)
      g_logger.print(f"created i2c0")
    except:
      g_logger.print("could not create i2c0 although configured, check wiring!")

  # create busses behind a multiplexer
  if config.HAVE_I2C_MP:
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
      g_logger.print(f"adding {len(i2c_mp)} I2C-busses from {name}")
      for i2cbus in i2c_mp:
        i2c.append(i2cbus)

  # return result
  atexit.register(at_exit_i2c,i2c)
  return i2c

# --- create dio and register at-exit processing   ---------------------------

_dios = {}
def get_dio(gpio,label):
  """ create digitialio """
  global _dios

  # DIOs are not shared like SPI-busses. But returning an existing DIOs
  # simplifies recreating SPI devices with the same set of pins.
  if gpio in _dios:
    g_logger.print(f"returning existing DIO, created for {_dios[gpio][1]}")
    return _dios[gpio][0]

  g_logger.print(f"creating DIO for {label}")
  dio = digitalio.DigitalInOut(gpio)
  atexit.register(at_exit_dio,dio,label)
  _dios[gpio] = (dio,label)
  return dio

# --- create spi and register at-exit processing   ---------------------------

_spi = {}
def get_spi(sck,mosi,miso,label):
  """ create spi """
  global _spi
  if sck in _spi:
    g_logger.print(f"returning existing SPI, created for {_spi[sck][1]}")
    return _spi[sck][0]
  try:
    g_logger.print(f"creating SPI for {label}")
    spi = busio.SPI(sck,mosi,miso)
    atexit.register(at_exit_spi,spi,label)
    _spi[sck] = (spi, label)
    return spi
  except:
    g_logger.print(f"SPI creation failed for pins {(sck,mosi,miso)}")
    raise

# --- initialize SD-card   ---------------------------------------------------

def init_sd(config):
  """ initialize SD-card and return SPI-object """

  spi = None
  if config.HAVE_SD:
    try:
      spi    = get_spi(pins.PIN_SD_SCK,pins.PIN_SD_MOSI,pins.PIN_SD_MISO,
                       "SD")
      sdcard = sdcardio.SDCard(spi,pins.PIN_SD_CS,1_000_000)
      vfs    = storage.VfsFat(sdcard)
      storage.mount(vfs, "/sd")
      g_logger.print("SD-card mounted on /sd")
    except Exception as ex:
      if spi:
        spi.deinit()
      raise
  return spi

# --- initialize RTC   -------------------------------------------------------

def init_rtc(config,i2c):
  """ initialize RTC and return RTC-object """

  if config.HAVE_RTC:
    rtc_spec = config.HAVE_RTC.split('(')
    rtc_name = rtc_spec[0]
    rtc_bus  = int(rtc_spec[1][0])
  else:
    rtc_name = None
    rtc_bus  = 0

  # don't care about exceptions, must be handled by caller
  rtc = ExtBase.create(rtc_name,i2c[rtc_bus],net_update=config.NET_UPDATE)
  if rtc_name == "PCF8523":
    if pins.PCB_VERSION > 0:
      rtc.rtc_ext.high_capacitance = True  # uses a 12.5pF capacitor
    if config.HAVE_LIPO:
      rtc.rtc_ext.power_managment = 0b001  # direct switchover Vdd<Vbat
    else:
      rtc.rtc_ext.power_managment = 0b000  # Vdd<Vbat and Vdd < Vth
  return rtc

# --- initialize OLED   ------------------------------------------------------

def init_oled(i2c,config):
  """ init OLED display """

  if config.HAVE_OLED:
    try:
      from oled import OLED
      odisp = OLED(config,i2c)
      display = odisp.get_display()
      g_logger.print(
        f"OLED created with size {display.width}x{display.height}")
      return odisp
    except Exception as ex:
      g_logger.print(f"could not initialize OLED: {ex}")
      raise
  return None

# --- initialize ETH for Wiznet   --------------------------------------------

def init_w5k():
  """ initialze ETH-chip """

  try:
    cs = None
    import board
    from adafruit_wiznet5k.adafruit_wiznet5k import WIZNET5K
    if board.board_id == "wiznet_w55rp20_evb_pico":
      import wiznet
      spi = wiznet.PIO_SPI(board.W5K_SCK,
                           MOSI=board.W5K_MOSI, MISO=board.W5K_MISO)
    elif board.board_id == "wiznet_w6300_evb_pico2":
      import wiznet
      spi = wiznet.PIO_SPI(board.W5K_SCK,
                           quad_io0=board.W5K_MOSI,
                           quad_io1=board.W5K_MISO,
                           quad_io2=board.W5K_IO2, quad_io3=board.W5K_IO3)
    else:
      spi = get_spi(pins.PIN_ETH_SCK,pins.PIN_ETH_MOSI,
                    pins.PIN_ETH_MISO,"ETH")
    cs = get_dio(pins.PIN_ETH_CS,"ETH")
    return WIZNET5K(spi,cs)
  except Exception as ex:
    g_logger.print(f"could not initialize ETH: {ex}")
    if cs:
      cs.deinit()
    import traceback
    traceback.print_exception(ex)
    raise
