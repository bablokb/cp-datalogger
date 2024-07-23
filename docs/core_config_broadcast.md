Configuration of Broadcast-Mode
===============================

Broadcast mode needs a few configuration variables in `config.py`.

| Name          | Type | O/M | Description                           |
|---------------|------|-----|---------------------------------------|
| HAVE_OLED     | str  |  O  | support I2C-OLED (default: None)      |
| BROADCAST_INT | int  |  O  | broadcast-interval (10)               |

Valid values for `HAVE_OLED` is `None` or `"width,height,addr"`, e.g.:

  - `"128,32,0x3c"` or `"128,32,0x3d"`
  - `"128,64,0x3c"` or `"128,64,0x3d"`

The `BROADCAST_INT` configures the interval of LoRa-messages sent to
the gateway-address. If no OLED is connected, this will fall back to
60s to protect the main (e-ink) display.
