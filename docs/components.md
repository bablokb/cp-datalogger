Components
==========

Overview
--------

Currently, two iterations of the datalogger (v1, v2) exist. The v2 has
been produced in two sub-versions with slightly different pcb-sizes and
differences in connectors.

In addition to the dataloggers ("base-PCBs"), there is a sensor-PCB
(also in two iterations) and two adapter-PCBs for the display and
the LoRa breakout.

Unless otherwise noted, components are shared between iterations.


Microcontroller-Board
---------------------

The dataloggers use the Pico-W both for price and functionality. The
v1-datalogger will also work with the Pico but with limited functionality.

Basically, the software will also run with other MCUs as long as it is
supported by CircuitPython and as long as it provides the required
interfaces (this depends on the sensors and displays used).


Power-Management
----------------

The datalogger boards operate the MCU in on/off mode for low-power
consumption using the following components

  - PCF8523: This RTC will keep time and wakeup the system with it's
    programmable alarm
  - CR2032: backup coin-cell for the RTC
  - SN74HC74 (v1): Double D-type flip-flop driving the enable-pin of the Pico-W
  - 74LVC2G74 (v2): Single D-type flip-flop driving the p-mosfet
  - AO3401A (v2): P-channel mosfet

For details, see [Hardware Architecture](./hw_architecture.md).


Storage
-------

For data storage, the v1-pcb uses a micro-sd card socket. The v2-pcb has
an integrated flash chip emulating a micro-sd card (XTSD). This chip is
available in 1,2, 4 and 8GBit versions. The v2-pcb uses the 1GBit version,
since 128MB of storage are sufficient.

The XTSD-chip is more expensive than the card socket, but cheaper than
an additional micro sd card. Also, it is more robust (no mechanical parts).
From the viewpoint of power-efficiency, the XTSD-chip is also better
because mount-time is much shorter.

Drawback of the integrated SD-chip is the need for a special program
to readout the collected data. For this reason, the software provides
a web-interfaces ([admin mode](./admin_mode.md)).


Sensor-PCB
----------

The sensor-PCB has three sensors for noise, temperature/humidity and light:

  - MP34DT05TR: PDM microphone
  - AHT20: temperature and humidity
  - BH1750: light

Besides the sensors, the PCB has some control buttons and LEDs.

The sensor-PCB connects to the datalogger-v2 with JST-SURS cables (8-pin).
As an alternate, THT connections are also supported (starting with
v2-PCB 2.10).

A separate sensor-PCB has a few advantages:

  - no heat creap from other components
  - flexible assembly options (panel mount possible)
  - independent development of base-PCB and sensor-PCB


Adapters
--------

The datalogger v1 connects directly to a display (back to back with
stacking headers). Also, there are THT-connectors for then LoRa-breakout
from Adafruit.

The datalogger v2 has cable connectors (8-pin JST-SURS) instead. They
connect to small adapter-PCBs that have the SURS-connectors on one side
and THT connectors for the display and the LoRa.


LoRa
----

Dataloggers optionally connect to a central gateway using LoRa.
Currently, the software supports the LoRa-RFM9x breakout from
Adafruit. A special PCB with SURS-connector and builtin
RFM9x-chip is in preparation.


Datasheets
----------

Note: some of the components can be replaced with similar components
but this might need some rework on the pcb.

- PCF8523: <https://www.nxp.com/docs/en/data-sheet/PCF8523.pdf>
- SN74HC74: <https://www.ti.com/lit/ds/symlink/sn74hc74.pdf>
- Micro-SD Card Reader/connector/socket: <https://datasheet.lcsc.com/lcsc/1912111437_SHOU-HAN-TF-PUSH_C393941.pdf>
- Oscillator: <https://datasheet.lcsc.com/lcsc/1810171817_Seiko-Epson-Q13FC1350000400_C32346.pdf>
- CR2032-Holder: <https://datasheet.lcsc.com/lcsc/2012121836_MYOUNG-BS-08-B2AA001_C964777.pdf>
- 74LVC2G74: <https://assets.nexperia.com/documents/data-sheet/74LVC2G74.pdf>
- AO3401A: <https://datasheet.lcsc.com/lcsc/1810171817_Alpha---Omega-Semicon-AO3401A_C15127.pdf>
- MP34DT05TR: https://www.st.com/resource/en/datasheet/mp34dt05-a.pdf
- AHT20: <https://cdn-learn.adafruit.com/assets/assets/000/091/676/original/AHT20-datasheet-2020-4-16.pdf?1591047915>
- BH1750: <https://www.mouser.com/datasheet/2/348/bh1750fvi-e-186247.pdf>
