Sensors
=======

AHT20
-----

  - Measures temperature and humidity.
  - Status: implemented
  - I2C-Breakout: [Adafruit  4566](https://adafru.it/4566)
  - Address: 0x38
  - Guide: <https://learn.adafruit.com/adafruit-aht20>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_AHTx0>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/091/676/original/AHT20-datasheet-2020-4-16.pdf?1591047915)


AM2301B
-------

  - Measures temperature and humidity (is an AHT20 in an enclosure)
  - Status: implemented
  - I2C-Breakout: [Adafruit  5181](https://adafru.it/5181)
  - Address: 0x38
  - Guide: <https://learn.adafruit.com/adafruit-aht20>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_AHTx0>
  - [datasheet](https://cdn-shop.adafruit.com/product-files/5181/5181_AM2301B.pdf)
  - Note: non-standard wiring:  
    Red: 3V3, Black: GND, White: SCL, Yellow: SDA


AM2320
-------

  - Measures temperature and humidity
  - Status: implemented
  - I2C-Breakout: [Adafruit  3721](https://adafru.it/3721)
  - Address: 0x5C
  - Guide: <https://learn.adafruit.com/adafruit-am2320-temperature-humidity-i2c-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_AM2320>
  - [datasheet](https://cdn-shop.adafruit.com/product-files/3721/AM2320.pdf)
  - Notes: no-pullups! Pinout left to right (from front): : 3V3, SDA, GND, SCL


BH1750
------

  - Measures Light
  - Status: implemented
  - I2C-Breakout: [Adafruit  4681](https://adafru.it/4681)
  - Address: 0x23 (default) or 0x5C (addr-pin high)
  - Guide: <https://learn.adafruit.com/adafruit-bh1750-ambient-light-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_BH1750>
  - [datasheet](https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf)


BME280
------

  - Measures temperature, humidity and pressure
  - Status: implemented
  - Breakouts: China or [Adafruit 2652](https://adafru.it/2652)
  - Address: 0x76 or 0x77
  - Guide: <https://learn.adafruit.com/adafruit-bme280-humidity-barometric-pressure-temperature-sensor-breakout>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_BME280>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/115/588/original/bst-bme280-ds002.pdf?1664822559)
  - Note: supports I2C and SPI. Chinese breakouts often claim to be a  
    BME280 but are in fact only a BMP280 


BMP280
------

  - Measures temperature and pressure
  - Status: implemented
  - Breakouts: China or [Adafruit 2651](https://adafru.it/2651)
  - Address: 0x76 or 0x77
  - Guide: <https://learn.adafruit.com/adafruit-bmp280-barometric-pressure-plus-temperature-sensor-breakout/overview>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_BMP280>
  - [datasheet](http://www.adafruit.com/datasheets/BST-BMP280-DS001-11.pdf)
  - Note: supports I2C and SPI.


CPUTEMP
-------

  - Pseudo-sensor: returns the value of `microcontroller.cpu.temperature`
  - Status: implemented


DCODE
-----

  - Pseudo-sensor: returns configured sensors (data-code, see `src/sensors/dcode.py`)
  - Status: implemented


DS18B20
-------

  - Measures temperature
  - Status: implemented
  - Breakouts: IC [Adafruit 374](https://adafru.it/374) or shielded versions available
  - Address: n.a.
  - Guide: <https://learn.adafruit.com/using-ds18b20-temperature-sensor-with-circuitpython>>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_DS18X20>
  - [datasheet](https://cdn-shop.adafruit.com/datasheets/DS18B20.pdf)
  - Note: uses the 1-wire protocol


ENS160
------

  - Measures TVOC and calculates eCO2 and AQI ("air quality index")
  - Status: implemented
  - I2C-Breakouts:
      - [Adafruit  5606](https://adafru.it/5606)
      - [DFRobot SEN0515]()
  - Address: 0x53 (default) and 0x52
  - Guide: <https://learn.adafruit.com/adafruit-ens160-mox-gas-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_ENS160>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/115/331/original/SC_001224_DS_1_ENS160_Datasheet_Rev_0_95-2258311.pdf?1663951433)


HTU31D
------

  - Measures temperature and humidity
  - Status: implemented
  - I2C-Breakout: [Adafruit  4832](https://adafru.it/4832)
  - Address: 0x40 or 0x41
  - Guide: n.a.
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_HTU31D>
  - [datasheet](https://www.te.com/usa-en/product-CAT-HSC0007.datasheet.pdf)


ID
--

  - Pseudo-sensor: returns the ID of the logger (`LOGGER_ID` from the configuration)
  - Status: implemented


LOCATION
--------

  - Pseudo-sensor: returns the location of the logger
    (`LOGGER_LOCATION` from the configuration)
  - Status: implemented


LTR-559
-------

  - Measures Light
  - Status: implemented
  - I2C-Breakout: [Pimoroni PIM413](https://shop.pimoroni.com/products/ltr-559-light-proximity-sensor-breakout)
  - Address: 0x23
  - Guide: n.a.
  - CircuitPython-driver: <https://github.com/pimoroni/Pimoroni_CircuitPython_LTR559>
  - [datasheet](https://optoelectronics.liteon.com/upload/download/DS86-2013-0003/LTR-559ALS-01_DS_V1.pdf)


MCP9808
-------

  - Measures temperature
  - Status: implemented
  - I2C-Breakout: [Adafruit  5027](https://adafru.it/5027)
  - Address: 0x18-0x20
  - Guide: <https://learn.adafruit.com/adafruit-mcp9808-precision-i2c-temperature-sensor-guide>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_MCP9808>
  - [datasheet](https://ww1.microchip.com/downloads/en/DeviceDoc/25095A.pdf)


METEO
-----

  - Queries meteological data from Open-Meteo
  - Status: implemented
  - Needs internet-access
  - Configuration: METEO_LATITUDE and METEO_LONGITUDE in `config.py`
  - [API-Documentation](https://open-meteo.com/en/docs) 


PDM-Micro
---------

  - Measures noise
  - Status: implemented
  - Breakout: [Adafruit  3492](https://adafru.it/3492)
  - Address: n.a.
  - Guide: <http://learn.adafruit.com/adafruit-pdm-microphone-breakout/>
  - CircuitPython-driver: uses builtin module `audiobusio` and class `PDMin`.
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/049/977/original/MP34DT01-M.pdf)
  - Note: the sensor-PCB uses the similar [MP34DT05TR](https://www.st.com/resource/en/datasheet/mp34dt05-a.pdf)


PMS5003
-------

  - Measures particles
  - Status: implemented
  - Breakouts:
      - [Adafruit UART 3686](https://adafru.it/3686)
      - [Adafruit I2C 4632](https://adafru.it/4632)
      - [Pimoroni UART COM1707](https://shop.pimoroni.com/products/pms5003-particulate-matter-sensor-with-cable)
  - Address: 0x12 (I2C-version)
  - Guide: <https://learn.adafruit.com/pm25-air-quality-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_PM25>
  - [datasheet](https://cdn-shop.adafruit.com/product-files/3686/plantower-pms5003-manual_v2-3.pdf)
  - Note: UART-versions need 5V. The Adafruit I2C-version has an onboard regulator.


SCD40/SCD41
-----------

  - Measures CO2, temperature, humidity
  - Status: implemented
  - Breakouts:
      - [SCD40: Adafruit  5187](https://adafru.it/5187)
      - [SCD41: Adafruit  5190](https://adafru.it/5190)
      - [SCD40: M5Stack U103](https://shop.m5stack.com/products/co2-unit-with-temperature-and-humidity-sensor-scd40)
      - [SCD41: M5Stack U104](https://shop.m5stack.com/products/co2l-unit-with-temperature-and-humidity-sensor-scd41)
  - Address: 0x62
  - Guide: <https://learn.adafruit.com/adafruit-scd-40-and-scd-41>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_SCD4x>
  - [datasheet](https://www.sensirion.com/media/documents/48C4B7FB/64C134E7/Sensirion_SCD4x_Datasheet.pdf)


SHT45
-----

  - Measures temperature and humidity
  - Status: implemented
  - I2C-Breakout: [Adafruit  5665](https://adafru.it/5665)
  - Address: 0x44
  - Guide: <https://learn.adafruit.com/adafruit-sht40-temperature-humidity-sensor>
  - CircuitPython-driver: <https://github.com/adafruit/Adafruit_CircuitPython_SHT4x>
  - [datasheet](https://cdn-learn.adafruit.com/assets/assets/000/117/503/original/Datasheet_SHT4x.pdf?1673387912)


Please note that many of the Adafruit versions of the above sensors are
fitted with an LED. For some sensors, this can be disabled by cutting
a track, but for others you just have to destroy them.
