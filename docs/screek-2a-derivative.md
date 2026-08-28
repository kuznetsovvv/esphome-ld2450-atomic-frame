# SCREEK 2A full derivative

`examples/screek-2a/esp32-c3.yaml` is a full SCREEK Human Sensor 2A firmware example derived from SCREEK's stable YAML and licensed under MIT.

It is much closer to the firmware used to exercise this project than the small clean-room examples. It retains SCREEK's UART parser, entities, software zones, illuminance support, and PCB LED wiring, then adds:

- coherent, device-timestamped LD2450 atomic frames
- direct LD2450 Bluetooth, target-mode, region, query, restart, and factory-reset commands
- chip state and region read-back without publishing the LD2450 MAC
- runtime frame-publish throttling
- passive ESP32 iBeacon presence and RSSI for two configurable beacons
- loop, heap, restart-recovery, temperature, uptime, and Wi-Fi diagnostics
- unique API encryption, OTA, recovery AP, and web credentials

## Provenance

The pinned upstream base is SCREEK stable commit `396e597e99a4ab9902e3fc09df515a892b38e3ef`:

https://github.com/screekworkshop/screek-human-sensor/blob/396e597e99a4ab9902e3fc09df515a892b38e3ef/2a/yaml/human-sensor-2a-stable-github.yaml

SCREEK added an MIT license after the redistribution request in issue #46 and explicitly welcomed modified builds:

https://github.com/screekworkshop/screek-human-sensor/issues/46

The upstream copyright and MIT text are preserved in `LICENSES/SCREEK-MIT.txt`. Modifications are covered by the repository's MIT license.

## Validation boundary

The feature lineage was exercised on physical SCREEK 2A hardware through private firmware. The public file is mechanically based on that firmware, but privacy and security sanitization changed identifiers, credentials, project identity, MAC publication, safe mode, and dangerous-control visibility. Therefore:

- this exact sanitized file compiles in CI but still needs a physical flash test
- it is unofficial and is not supported or endorsed by SCREEK Workshop
- it is not an OTA patch over the vendor image
- it may reset preferences or require Home Assistant re-adoption
- adding BLE can require a different flash partition layout

Use USB/serial for the first installation unless OTA compatibility has been verified. Keep a known-good recovery image and record your existing zones/settings first.

## Configure

1. Copy `examples/screek-2a/secrets.yaml.example` to `examples/screek-2a/secrets.yaml`.
2. Replace every placeholder with unique values. Beacon identifiers are persistent tracking identifiers; do not publish them.
3. Review the two optional beacon substitutions near the top of `esp32-c3.yaml`. Delete both `ble_presence` and `ble_rssi` entries if they are not needed.
4. Review the 50% passive BLE scan duty (100 ms window per 200 ms interval) and the 30-second presence timeout. Advertisements can be missed by design.
5. Validate and compile with ESPHome 2026.6.1 or later:

   ```shell
   esphome config examples/screek-2a/esp32-c3.yaml
   esphome compile examples/screek-2a/esp32-c3.yaml
   ```

## Hardware-specific warnings

SCREEK's upstream firmware intentionally drives PCB LEDs on GPIO12 and GPIO13. ESPHome flags these pins for a generic ESP32-C3, so the inherited configuration uses explicit validation overrides. Do not copy those pin assignments to an unrelated ESP32-C3 board.

## LD2450 Bluetooth

The ESP32 BLE scanner and LD2450 configuration radio are independent. Turn off `LD2450 Bluetooth` after setup. The derivative provides state read-back plus separate enable/disable commands; the enable button is disabled by default.

An LD2450 factory reset re-enables its Bluetooth. The factory-reset button is disabled by default and should remain hidden unless recovery consequences are understood.

See the security guide:

https://community.home-assistant.io/t/psa-disable-the-ld2450s-open-bluetooth-after-setup/1021895

## Regions and state

SCREEK software zones and the LD2450 chip's native regions are separate systems. The native region mode is global across three rectangles:

- `Disabled`: chip reports all targets
- `Detection`: chip reports only targets in configured regions
- `Filter`: chip omits targets in configured regions

Start with all-zero regions and `Disabled`. Snapshot settings before experimentation. Native region changes persist in the LD2450 module; ESP-side values live in ESP preferences.

## Resource use

The first sanitized local build with ESPHome 2026.6.1 used approximately:

- 67,300 bytes RAM (20.5%)
- 1,524,450 bytes flash (83.1% of the application partition)

Leave headroom for future ESPHome growth and recompile before every update.
