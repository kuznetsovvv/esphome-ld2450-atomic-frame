# Provenance and third-party notice

The code and documentation in this repository were written as a clean-room
implementation against ESPHome's public native component APIs, including
`ld2450`, `esp32_ble_tracker`, `ble_presence`, and `ble_rssi`.

This repository does **not** contain:

- SCREEK Workshop YAML or firmware binaries
- Hi-Link firmware or app code
- vendor credentials or OTA passwords
- real Bluetooth identifiers or presence history
- real radar captures, floor plans, zones, or household geometry

ESPHome uses a split license: its C++/runtime code is licensed under GPL-3.0,
while its Python code and other portions are licensed under MIT:
https://github.com/esphome/esphome/blob/dev/LICENSE

This repository does not vendor ESPHome source code or generated firmware
binaries. Firmware built from these examples incorporates the ESPHome runtime;
any redistribution of those binaries must follow the applicable upstream
license terms.

Hi-Link, LD2450, SCREEK, Home Assistant, and ESPHome names may be trademarks of
their respective owners. This project is unofficial and is not affiliated with
or endorsed by those projects or vendors.

SCREEK-compatible derivative redistribution is being discussed separately in:
https://github.com/screekworkshop/screek-human-sensor/issues/46