# Security policy

## Supported versions

Only the latest tagged release is supported.

## Reporting a vulnerability

Use GitHub's private vulnerability reporting for this repository. Do not include
real radar captures, Bluetooth identifiers, Wi-Fi credentials, API keys, device
addresses, or household geometry in a public issue.

Vulnerabilities in ESPHome or Home Assistant should be reported through those
projects' security policies, not here.

## Deployment guidance

- Use unique ESPHome API encryption keys and OTA passwords per device.
- Do not expose ESPHome API, OTA, or web ports to the Internet.
- Keep IoT devices on a trusted, restricted network.
- Disable the LD2450's Bluetooth radio after setup when it is not required. It
  is separate from the optional ESP32 BLE scanner.
- Treat iBeacon UUID/major/minor tuples and BLE presence history as tracking
  data. Keep real identifiers in secrets and out of issues and captures.
- Treat CSV frame logs as sensitive movement data.
- Keep USB/serial access physically controlled.