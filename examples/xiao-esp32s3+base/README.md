Datalogger with SeeedStudio XIAO-ESP32S3 and XIO-Base
=====================================================

To build, run

    make MAKEVARS=examples/xiao-esp32s3+base/makevars.mk

from the top-level directory. This will create the directory
`xiao-esp32s3+base.local` which contains the files to deploy.

Important files in this directory:

  - `makevars.mk`: make configuration
  - `pins.py`: hardware configuration (XIAO-specific pins)
  - `config.py`: application configuration
