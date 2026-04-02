#-----------------------------------------------------------------------------
# Receiver task: save
# 
# This task saves the record (default: stderr). The difference to "print" is
# that the data is processed as binary without decoding.
#
# Author: Bernhard Bablok
#
# Website: https://github.com/bablokb/cp-datalogger
#-----------------------------------------------------------------------------

from .base_task import BaseTask

class SAVE(BaseTask):
  def __init__(self, tools):
    """ constructor """
    super().__init__(tools)
    self._outfile = self.tools.get_value("SAVE",
                                         "filename","/dev/stderr")
    self._endl = bytes(self.tools.get_value("SAVE",
                                            "endl",'\n'),'utf-8')
  def run(self, record):
    """ save record """
    with open(self._outfile, "ab") as file:
      file.write(record)
      if self._endl and record[-1] != ord(self._endl):
        file.write(self._endl)
