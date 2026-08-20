# Atomic frame format

This document describes format version 1. The payload has no inline version
field; an incompatible future format must use a new entity name or an explicit
out-of-band version.

## Payload

```text
t_ms|x1,y1,v1|x2,y2,v2|x3,y3,v3
```

Synthetic example:

```text
123456789|-400,1200,25|300,1800,-10|0,0,0
```

Observed LD2450 output packs occupied targets into the leading slots, so the
example follows that convention. Consumers should still parse all three slots
independently rather than treating dense packing as a format guarantee.

## Fields

- `t_ms`: unsigned 32-bit ESP `millis()` value captured in the frame callback.
  It wraps about every 49.7 days and resets when the ESP reboots.
- `xN`: signed target X coordinate in raw millimeters.
- `yN`: target Y coordinate in raw millimeters.
- `vN`: signed LD2450 protocol speed quantum. Multiply by 10 for millimeters
  per second.
- `0,0,0`: empty target slot.

The producer is present-gated: it holds the last Home Assistant state when all
three slots are empty instead of generating idle rows.

## Guarantees

- All nine target values come from one successfully parsed LD2450 periodic frame.
- The callback executes after native ESPHome has updated the internal target
  sensor states.
- Coordinates are serialized before Home Assistant can apply locale conversion.
- `t_ms` changes every frame, so repeated coordinates are still delivered.

## Non-guarantees

- Target slot numbers are assigned by the LD2450 and are not stable person IDs.
- The timestamp is not wall-clock time.
- A timestamp decrease can mean either ESP reboot or 32-bit rollover.
- The stream does not authenticate a target or classify a trajectory.

## CSV logger schema

The optional logger writes:

```text
wall_iso,t_ms,dt_ms,x1,y1,v1,x2,y2,v2,x3,y3,v3
```

- `wall_iso` is the Home Assistant host time at receipt.
- `dt_ms` is the device timestamp delta. It is blank for the first frame and
  after a probable reboot; rollover is handled explicitly.

CSV captures are movement data. Keep them private by default.