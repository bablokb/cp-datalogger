Blues Setup
===========

Mainly follow setup quickstart-guide on <https://dev.blues.io>.

Hardware
--------

  - remove screw from carrier-board
  - insert notecard
  - reinsert screw
  - connect LTE and GPS antennas


Serial Test
-----------

  - connect with USB
  - use Chrome with webserial
  - send: {"req": "card.version"}
    ```> {"req":"card.version"}
    {
     "version": "notecard-5.3.1.16292",
     "device": "dev:860264054673802",
     "name": "Blues Wireless Notecard",
     "sku": "NOTE-WBEXW",
     "board": "5.13",
     "wifi": true,
     "cell": true,
     "gps": true,
     "api": 5,
     "body": {
       "org": "Blues Wireless",
       "product": "Notecard",
       "target": "u5",
       "version": "notecard-u5-5.3.1",
       "ver_major": 5,
       "ver_minor": 3,
       "ver_patch": 1,
       "ver_build": 16292,
       "built": "Sep 17 2023 20:32:47"
     }
    }```

Create Notehub-Account
----------------------

Goto <https://notehub.io/sign-up> and follow directions.


Create Notehub-Project
----------------------

After login to account, follow link and instructions.
This creates a "ProductUID".

ProductUID for development: de.gmx.bablokb:datalogger.dev

Link Notecard to ProductUID
---------------------------

Send

    > {"req":"hub.set", "product":"de.gmx.bablokb:datalogger.dev"}
    > {"req":"hub.sync"}
    > {"req":"hub.sync.status"}
    {
     "status": "idle {disconnected} {transport}",
     "mode": "{modem-on}",
     "requested": 29
    }
    > {"req":"hub.sync.status"}
      {
       "mode": "{modem-off}",
       "time": 1707124205,
       "completed": 16
      }


CircuitPython Libraries
-----------------------

Download from <https://github.com/blues/note-python>.
