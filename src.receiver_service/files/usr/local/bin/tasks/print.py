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
  def __init__(self, tools):
    """ constructor """
    super().__init__(tools)
    self._printfile = self.tools.get_value("PRINT",
                                           "filename","/dev/stderr")
  def run(self, record):
    """ print record """
    rec = record.decode()
    end = '' if rec[-1] == '\n' else None
    with open(self._printfile,'w') as file:
      print(rec,file=file,flush=True,end=end)
