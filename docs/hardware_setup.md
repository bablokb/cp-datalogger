Setup
=====

/All references to the jumper below can be ignored for v2-boards. The
v2-boards don't use jumpers./

1. CircuitPython
----------------

First step is to install CircuitPython on the board. Be sure to select
the version 8.0.5 (note that this is not the most current version!).

Sources:
  - If you have a Pico, install  
    <https://circuitpython.org/board/raspberry_pi_pico/>
  - If you have a Pico W, install  
    <https://circuitpython.org/board/raspberry_pi_pico_w/>


2. Software
-----------

Follow the instructions in [Software deployment](./deployment.md).


3. Hardware
-----------

Steps:

  - Connect AA batteries (or similar) via the battery port
  - Add a coin cell to maintain data on the RTC (CR2032)
  - Always remove the jumper if you plugin the USB-cable to the Pico, e.g.
    for software updates.
