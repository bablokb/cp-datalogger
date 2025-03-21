#-----------------------------------------------------------------------------
# Restart into bootloader.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/pcb-pico-datalogger
#-----------------------------------------------------------------------------

import microcontroller

microcontroller.on_next_reset(microcontroller.RunMode.BOOTLOADER)
microcontroller.reset()
