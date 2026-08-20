# ESPHome LD2450 Atomic Frames

This repository demonstrates two modifications developed for and applied to a
privately customized **SCREEK Human Sensor 2A** firmware build:

- publishing all three LD2450 target slots as one coherent, device-timestamped
   Home Assistant state for trajectory analysis
- using the SCREEK 2A's ESP32-C3 radio for optional passive BLE presence while
   keeping that radio distinct from the LD2450 module's own Bluetooth radio

The private modified SCREEK firmware is not included here. Instead, this
repository reimplements those capabilities from scratch with ESPHome's public
native components. The result is a minimal, buildable demonstration of what the
SCREEK 2A and similar ESP32-C3 + LD2450 hardware can do, not a redistribution of
SCREEK firmware.

The atomic frame modification publishes:

```text
t_ms|x1,y1,v1|x2,y2,v2|x3,y3,v3
```

This avoids reconstructing a radar frame from separately delivered X, Y, and
speed entities. The package uses ESPHome's native `ld2450.on_data` callback,
which runs after a complete periodic frame has been parsed.

## Status

Experimental release candidate. The capabilities have been exercised on physical
SCREEK 2A hardware through the author's private customized firmware. The
independently written clean-room examples in this repository both compile with
ESPHome 2026.6.1, but those examples have not yet been flashed to physical
hardware. Results from the private derivative do not replace that validation.

## Important warning

This is unofficial community demonstration firmware. It is not produced,
supported, or warranted by Hi-Link, SCREEK Workshop, ESPHome, or Home Assistant.

Flashing firmware can make a device unavailable and may require USB/serial
recovery. The examples are not official SCREEK updates, patches to apply over a
vendor image, or drop-in replacements for the full SCREEK firmware. They may omit
LEDs, illuminance, vendor zones, calibration, entity names, and recovery features.
Review the configuration and keep a known-good recovery image before flashing
anything.

The software is provided without warranty. See [LICENSE](LICENSE).

## Why an atomic frame?

Separate Home Assistant entities can introduce:

- X/Y tearing when one coordinate arrives before the other
- receive-time jitter instead of device-frame timing
- locale unit conversion before downstream analysis
- state deduplication that discards repeated dwell frames

The atomic text payload includes a changing device timestamp, raw millimeter
coordinates, and all three slots in one state update.

## Clean-room provenance

The functionality documented here was first developed and exercised in a private
modification of the SCREEK 2A firmware. That derivative remains private. The
packages in this repository were separately written from scratch against
ESPHome's public native components. They do not contain SCREEK YAML, source
snippets, or firmware binaries.

The modified SCREEK build cannot be published under an assumed license because
the upstream repository currently has no LICENSE file. Explicit redistribution
permission has been requested in
[screekworkshop/screek-human-sensor#46](https://github.com/screekworkshop/screek-human-sensor/issues/46).

This separation is intentional: the private build shows how the modifications
behave on the actual product, while this repository provides independently
reviewable examples of the underlying hardware capabilities.

## Project scope

This repository deliberately stops at the firmware and atomic-frame transport
boundary. It contains the ESPHome producer, frame specification, parser,
optional generic CSV logger, an optional ESP32 BLE presence package, and tests.

Radar-lab analytics such as target association, ghost rejection, trajectory
classification, and geometry tuning belong in a separate repository. They have
different dependencies and release cycles, and real captures or room geometry
can reveal private movement patterns. Home Assistant rules and entity mappings
are deployment-specific and also stay separate; a reusable adapter can be
extracted later around a neutral, versioned analytics output format.

## Demo firmware quick start

1. Install ESPHome 2026.6.1 or later.
2. Copy `examples/secrets.yaml.example` to `examples/secrets.yaml` and replace
   every placeholder.
3. Review the board and UART pins in `examples/esp32-c3.yaml`. GPIO5/GPIO4 are
   example wiring and are not universal.
4. Validate and build:

   ```shell
   esphome config examples/esp32-c3.yaml
   esphome compile examples/esp32-c3.yaml
   ```

5. Use serial installation for a new or vendor-flashed device unless you have
   verified OTA compatibility and credentials.

These steps build the clean-room demonstration firmware. They do not modify an
existing SCREEK image in place or recreate all features of the vendor firmware.

The package owns the native component's X/Y/speed sensor slots so it can read a
coherent state inside `on_data`. Those high-rate sensors are internal by default.
Set this substitution to `"false"` if you also want them exposed to Home Assistant:

```yaml
substitutions:
  atomic_target_sensors_internal: "false"
```

Exposing high-rate target entities can significantly increase Recorder growth.

## Optional BLE presence

`packages/ble-presence.yaml` adds passive ESP32 iBeacon observation as a separate,
composable package. The combined example is
`examples/ble-presence/esp32-c3.yaml`.

This demonstrates the second modification used in the private customized SCREEK
2A firmware without including its device-specific implementation or identifiers.

BLE presence uses seconds-scale timeouts, so Home Assistant arrival time is
adequate; it does not need the radar stream's source-timestamp precision. The
example listens during a 100 ms window every 200 ms and therefore misses some
advertisements by design. The ESP32-C3 also shares its radio between BLE and
Wi-Fi.

See [docs/ble-presence.md](docs/ble-presence.md) for configuration, missed-packet
behavior, privacy guidance, and the distinction between ESP32 scanning and the
LD2450's separate Bluetooth radio.

## Home Assistant Recorder

The frame entity can update several times per second. Exclude it from Recorder
when a live consumer is sufficient:

```yaml
recorder:
  exclude:
    entities:
      - sensor.ld2450_atomic_frame
```

Entity IDs depend on the device and friendly names. Confirm the actual ID in
Developer Tools.

## Optional CSV logger

The `pyscript/` directory contains a configurable Pyscript app that batches
frames and appends them to a CSV outside Home Assistant's event loop.

1. Install the Pyscript custom integration.
2. Copy `pyscript/apps/ld2450_atomic_logger/` to
   `/config/pyscript/apps/ld2450_atomic_logger/`.
3. Merge `pyscript/config.example.yaml` into your Pyscript YAML configuration.
4. Add the output CSV to the Git ignore rules for your HA configuration. If you
   configure a nested output path, create its parent directory first.
5. Reload Pyscript.

Frame logs reveal movement patterns. Treat them as sensitive data; do not commit
or publish real captures.

## Frame format

See [docs/frame-format.md](docs/frame-format.md). The `v` field deliberately
uses the same raw protocol quanta as the original experimental stream:

```text
speed_mm_s = v_raw * 10
```

## Tests

No third-party Python packages are required:

```shell
python -m unittest discover -s tests -t . -v
```

The ESPHome example should also be compiled before each release.

## Security

The examples enable API encryption and password-protected native OTA. Keep unique
secrets per device, avoid an unauthenticated web server, segment IoT devices, and
disable the LD2450's own Bluetooth after setup when it is not needed. That radio
is separate from the optional ESP32 BLE scanner.

See the related Home Assistant Community guide:
[PSA: disable the LD2450's open Bluetooth after setup](https://community.home-assistant.io/t/psa-disable-the-ld2450s-open-bluetooth-after-setup/1021895).