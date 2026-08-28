# Provenance and third-party notice

Most code and documentation in this repository were written as a clean-room
implementation against ESPHome's public native component APIs, including
`ld2450`, `esp32_ble_tracker`, `ble_presence`, and `ble_rssi`.

The exception is `examples/screek-2a/esp32-c3.yaml`, which is derived from
SCREEK Workshop's Human Sensor 2A YAML at commit
`396e597e99a4ab9902e3fc09df515a892b38e3ef`. SCREEK licensed that source under
MIT after the clarification in issue #46. The upstream copyright and permission
notice are preserved in `LICENSES/SCREEK-MIT.txt`.

This repository does **not** contain:

- SCREEK firmware binaries or unlicensed SCREEK source
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

SCREEK's license clarification and permission history are recorded in:
https://github.com/screekworkshop/screek-human-sensor/issues/46