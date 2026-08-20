# Optional ESP32 BLE presence

The optional `packages/ble-presence.yaml` package observes one iBeacon with the
ESP32 radio. It exposes a presence binary sensor, an RSSI sensor, and a switch
that starts or stops scanning. It is intended for coarse presence corroboration,
not frame-level motion analysis.

## Timing model

BLE presence operates on repeated advertisements and seconds-scale timeouts. For
that use case, Home Assistant arrival time is sufficient; the package does not
add a source timestamp to each RSSI update.

Radar trajectories are different. Velocity, heading, and association depend on
small inter-frame intervals, so the atomic radar payload keeps its ESP `millis()`
timestamp. BLE scanning does not change that format. The source timestamp makes
radar cadence measurable despite Wi-Fi delivery jitter, but it cannot recreate a
radar frame or BLE advertisement that was never received.

For sensor fusion, calculate the trajectory or passage event from device-timed
radar frames first, then correlate that event with coarse BLE arrival-time
observations over a seconds-scale window.

## Missed advertisements

The example uses passive scanning with a 200 ms interval and a 100 ms window.
That is 50 percent nominal scan duty: the ESP32 is deliberately not listening
for BLE during the other half of each interval. An advertisement sent outside a
scan window can be missed.

The ESP32-C3 also shares one 2.4 GHz radio between Wi-Fi and BLE. Radio
coexistence can delay or lose additional receptions. Repeated beacon broadcasts
and the default 30-second presence timeout make occasional misses acceptable for
coarse presence, but they do not provide a delivery guarantee.

- Do not treat one RSSI sample as distance or identity proof.
- Do not use this signal alone for safety, security, or access control.
- Increasing the scan window may improve discovery while increasing contention
  with Wi-Fi. Keep the window no larger than the interval and test ESPHome API
  stability plus radar `dt_ms` under the intended load.
- Tune any RSSI proximity threshold for the actual beacon, enclosure, placement,
  and RF environment. This package intentionally has no default RSSI gate.

## Two separate Bluetooth radios

This setup contains two independent Bluetooth surfaces:

1. The **ESP32 BLE radio** passively receives iBeacon advertisements for this
   optional presence feature. The `ESP32 BLE Scan` switch controls this scanner.
2. The **LD2450 Bluetooth radio** is built into the radar module and exists for
   radar configuration. It is not used by the presence package.

Disabling the LD2450 radio does not disable ESP32 beacon scanning, and enabling
the ESP32 scanner does not secure the LD2450. Disable the LD2450's own Bluetooth
after setup when it is not needed. See
[PSA: disable the LD2450's open Bluetooth after setup](https://community.home-assistant.io/t/psa-disable-the-ld2450s-open-bluetooth-after-setup/1021895).

## Configure and build

1. Copy `examples/ble-presence/secrets.yaml.example` to
   `examples/ble-presence/secrets.yaml`.
2. Replace every placeholder, including the iBeacon UUID, major, and minor
   values. Do not publish those identifiers.
3. Review the board, UART pins, scan duty, and timeout.
4. Validate and compile:

   ```shell
   esphome config examples/ble-presence/esp32-c3.yaml
   esphome compile examples/ble-presence/esp32-c3.yaml
   ```

The scan switch defaults on after boot and is optimistic: it commands scanning
but does not report independent controller feedback.

Adding the ESP32 BLE stack can increase firmware size enough to change the flash
partition layout relative to a vendor image. Treat the first installation as a
serial/USB flash unless OTA compatibility has been verified, and keep a known-good
recovery image.

## Privacy

An iBeacon UUID/major/minor tuple is a persistent tracking identifier. Keep it in
`secrets.yaml`, use a unique value, and avoid publishing real identifiers, RSSI
history, or presence logs.