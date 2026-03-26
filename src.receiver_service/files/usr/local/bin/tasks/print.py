#-----------------------------------------------------------------------------
# Receiver task: print
# 
# This task prints the record (default: stderr)
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from .base_task import BaseTask

class PRINT(BaseTask):
  def __init__(self, cparser):
    """ constructor """
    self._printfile = self._get_value(cparser, "PRINT",
                                        "filename","/dev/stderr")
  def run(self, record):
    """ print record """
    with open(self._printfile,'w') as file:
      print(record.decode(),file=file,flush=True,end=None)
