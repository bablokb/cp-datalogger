Links
=====

This is a collection of links to products, datasheets, documentation and so on.


Datasheets for hardware used in conjunction with the board
----------------------------------------------------------

Required:

  - Raspberry Pi Pico or Pico W  
  (https://www.raspberrypi.com/products/raspberry-pi-pico/) or a
  pin-compatible device, such as the [Pico
  Lipo](https://shop.pimoroni.com/products/pimoroni-pico-lipo), is
  required for the operation of the board. Details on which device to
  chose are below.

Optional:

  - Adafruit RFM96W LoRa Radio Transceiver Breakout - 433 MHz - RadioFruit:  
  <https://www.adafruit.com/product/3073>
  This is optional. It is used for offloading data from the Pico to a
  'base station'. If you have public LoRa gateways where you are, you
  can also use one of those gateways.
  *Important:* We are selecting the 433 MHz version of this board, as
  this is the appropriate frequency for Tanzania. There is an 868 /
  915 MHz version available https://www.adafruit.com/product/3072.

  - Pico Inky Pack:  
  <https://shop.pimoroni.com/products/pico-inky-pack>
  Used to shows sensor data.

  - A micro-SD card


Datasheets for components used on the board
-------------------------------------------

Note: some of the components can be replaced with similar components but this might
need some rework on the pcb.

  - PCF8523: <https://www.nxp.com/docs/en/data-sheet/PCF8523.pdf>
  - SN74HC74: <https://www.ti.com/lit/ds/symlink/sn74hc74.pdf>
  - Micro-SD Card Reader/connector/socket:  
    <https://datasheet.lcsc.com/lcsc/1912111437_SHOU-HAN-TF-PUSH_C393941.pdf>
  - Oscillator:  
    <https://datasheet.lcsc.com/lcsc/1810171817_Seiko-Epson-Q13FC1350000400_C32346.pdf>
  - CR2032-Holder:  
    <https://datasheet.lcsc.com/lcsc/2012121836_MYOUNG-BS-08-B2AA001_C964777.pdf>
