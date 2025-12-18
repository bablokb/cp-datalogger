Pins
====


Reserved Pins on Raspberry Pi Pico
----------------------------------

Note that the default I2C-bus is I2C1. The UART-header could also
be used for I2C0.

If LoRa is not used, the LoRa pins GP12/GP13 also provide I2C0.


|                     | Pin  | Pin  |                         |
|---------------------|------|------|-------------------------|
| UART-TX / I2C0-SDA  | GP0  | VBUS |
| UART-RX / I2C0-SCL  | GP1  | VSYS |
|                     | GND  | GND  |
| I2C1-SDA (RTC)      | GP2  | EN   |
| I2C1-SCL (RTC)      | GP3  | 3V3  |
| DONE                | GP4  | VREF |
| Front-LED           | GP5  | GP28 | PS_STATUS LM66200
|                     | GND  | GND  |
| SWB                 | GP6  | GP27 | ext (ADC/1-Wire)
| LoRa-RST            | GP7  | GP26 | Display Busy
| SWA                 | GP8  | RUN  | RUN
| LoRa-CS             | GP9  | GP22 | SD-CS
|                     | GND  | GND  |
| SCLK1, LoRa         | GP10 | GP21 | Display Reset
| MOSI1, LoRa         | GP11 | GP20 | Display D/C
| MISO1, LoRa         | GP12 | GP19 | MOSI0 (Display, SD-Card)
| SWC                 | GP13 | GP18 | SCLK0 (Display, SD-Card)
|                     | GND  | GND  |
| n.a.                | GP14 | GP17 | Display CS
| LoRa-DIO0           | GP15 | GP16 | MISO0 (Display, SD-Card)
