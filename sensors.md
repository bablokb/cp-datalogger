Sensors
=======

AHT20
-----

  - Measures temperature and humidity.
  - Status: implemented
  - I2C-Breakout: (Adafruit  4566)[https://adafru.it/4566]
  - Address: 0x38
  - Guide: <https://learn.adafruit.com/adafruit-aht20>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_AHTx0>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/091/676/original/AHT20-datasheet-2020-4-16.pdf?1591047915)


AM2301B
-------

  - Measures temperature and humidity (is an AHT20 in an enclosure)
  - Status: implemented
  - I2C-Breakout: (Adafruit  5181)[https://adafru.it/5181]
  - Address: 0x38
  - Guide: <https://learn.adafruit.com/adafruit-aht20>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_AHTx0>
  - [datasheet](https://cdn-shop.adafruit.com/product-files/5181/5181_AM2301B.pdf)
  - Note: non-standard wiring:  
    Red: 3V3, Black: GND, White: SCL, Yellow: SDA


SHT45
-----

  - Measures temperature and humidity
  - Status: implemented
  - I2C-Breakout: (Adafruit  5665)[https://adafru.it/5665]
  - Address: 0x44
  - Guide: <https://learn.adafruit.com/adafruit-sht40-temperature-humidity-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_SHT4x>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/117/503/original/Datasheet_SHT4x.pdf?1673387912)


MCP9808
-------

  - Measures temperature
  - Status: implemented
  - I2C-Breakout: (Adafruit  5027)[https://adafru.it/5027]
  - Address: 0x18-0x20
  - Guide: <https://learn.adafruit.com/adafruit-mcp9808-precision-i2c-temperature-sensor-guide>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_MCP9808>
  - [datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/25095A.pdf)


ENS160
------

  - Measures TVOC and calculates eCO2 and AQI ("air quality index")
  - Status: implemented
  - I2C-Breakout: (Adafruit  ????)[https://adafru.it/????] and  
    (DFRobot SEN0515)[]
  - Address: 0x53 (default) and 0x52
  - Guide: <https://learn.adafruit.com/adafruit-ens160-mox-gas-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_ENS160>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/115/331/original/SC_001224_DS_1_ENS160_Datasheet_Rev_0_95-2258311.pdf?1663951433)


BH1750
------

  - Measures Light
  - Status: implemented
  - I2C-Breakout: (Adafruit  4681)[https://adafru.it/4681]
  - Address: 0x23 (default) or 0x5C (addr-pin high)
  - Guide: <https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_BH1750>
  - [datasheet](https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf)


LTR-559
-------

  - Measures Light
  - Status: implemented
  - I2C-Breakout: (Pimoroni PIM413)[https://shop.pimoroni.com/products/ltr-559-light-proximity-sensor-breakout)]
  - Address: 0x23
  - Guide: n.a.
  - CircuitPython-driver: <https://github.com/pimoroni/Pimoroni_CircuitPython_LTR559>
  - [datasheet](https://optoelectronics.liteon.com/upload/download/DS86-2013-0003/LTR-559ALS-01_DS_V1.pdf)


PDM-Micro
---------

  - Measures 
  - Status: implemented
  - Breakout: (Adafruit  ????)[https://adafru.it/????]
  - Address: n.a.
  - Guide: 
  - CircuitPython-driver:
  - [datasheet]()


Please note that many of the Adafruit versions of the above sensors are
fitted with an LED. For some sensors, this can be disabled by cutting
a track, but for others you just have to destroy them.
