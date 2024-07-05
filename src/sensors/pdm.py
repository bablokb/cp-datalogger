#-----------------------------------------------------------------------------
# Sensor definition for PDM.
#
# Naming convention:
#   - filenames in lowercase (pdm.py)
#   - class name the same as filename in uppercase (PDM)
#   - the constructor must take four arguments (config,i2c,addr,spi)
#     and probe for the device
#   - the read-method must update the data and return a string with the
#     values for the csv-record
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import board
import audiobusio
import array
import math

import pins

class PDM:
  formats = ["Noise:", "{0:0.0f}"]
  headers = 'Noise'

  def __init__(self,config,i2c,addr=None,spi=None):
    """ constructor """

    self.ignore = False
    self.mic = audiobusio.PDMIn(pins.PIN_PDM_CLK,pins.PIN_PDM_DAT,
                                sample_rate=16000, bit_depth=16)

  def read(self,data,values):
    samples = array.array('H', [0] * 160)
    self.mic.record(samples, len(samples))

    mean_samples = int(sum(samples)/len(samples))
    sum2_samples = sum(
        float(sample - mean_samples) * (sample - mean_samples)
        for sample in samples
    )
    mag = round(math.sqrt(sum2_samples / len(samples)),0)
    data["pdm"] = {
      "mag": mag
    }
    if not self.ignore:
      values.extend([None,mag])
    return f"{mag:0.0f}"
