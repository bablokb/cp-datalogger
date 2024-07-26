Configuration of Broadcast-Mode
===============================

Broadcast mode needs a few configuration variables in `config.py`.

| Name          | Type | O/M | Description                           |
|---------------|------|-----|---------------------------------------|
| HAVE_OLED     | str  |  O  | support I2C-OLED (default: None)      |
| BROADCAST_INT | int  |  O  | broadcast-interval (10)               |

For valid values of `HAVE_OLED`, see task "update_oled" in
[task-configuration](./core_config_tasks.md).

The `BROADCAST_INT` configures the interval of LoRa-messages sent to
the gateway-address. If no OLED is connected, this will fall back to
60s to protect the main (e-ink) display.
