#-----------------------------------------------------------------------------
# Sensor definition for the LM66200 ideal diode (power-source indicator)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import pins

class LM66200:
  formats = ["PSRC:", "{0}"]
  headers = 'P-SRC'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """
    self._config = config
    self.ignore  = False

  def read(self,data,values):
    """ read power-source GPIO """

    pin_ps = getattr(pins,"PIN_PS",None)
    if not pin_ps:
      psrc = "U"
    else:
      import digitalio
      with digitalio.DigitalInOut(pin_ps) as di:
        di.pull = digitalio.Pull.UP
        psrc = "E" if di.value else "I"  # VIN1: external, VIN2: internal
    data["psrc"] = psrc
    if not self.ignore:
      values.extend([None,psrc])
    return psrc
