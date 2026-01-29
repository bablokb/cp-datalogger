#-----------------------------------------------------------------------------
# Restart into bootloader.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

import microcontroller

microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
microcontroller.reset()
