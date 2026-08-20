from __future__ import annotations

from dataclasses import dataclass

UINT32_MODULUS = 1 << 32
ROLLOVER_HIGH_WATER = 0xF0000000
ROLLOVER_LOW_WATER = 0x0FFFFFFF


@dataclass(frozen=True)
class Target:
    x_mm: int
    y_mm: int
    speed_raw: int

    @property
    def speed_mm_s(self) -> int:
        return self.speed_raw * 10

    @property
    def present(self) -> bool:
        return self.x_mm != 0 or self.y_mm != 0


@dataclass(frozen=True)
class Frame:
    t_ms: int
    targets: tuple[Target, Target, Target]

    @property
    def has_targets(self) -> bool:
        return any(target.present for target in self.targets)


def parse_payload(payload: str) -> Frame:
    if not isinstance(payload, str):
        raise TypeError("payload must be a string")

    parts = payload.split("|")
    if len(parts) != 4:
        raise ValueError("payload must contain one timestamp and three target slots")

    try:
        t_ms = int(parts[0])
    except ValueError as error:
        raise ValueError("timestamp must be an integer") from error

    if not 0 <= t_ms < UINT32_MODULUS:
        raise ValueError("timestamp must be an unsigned 32-bit value")

    targets = []
    for index, segment in enumerate(parts[1:], start=1):
        values = segment.split(",")
        if len(values) != 3:
            raise ValueError(f"target slot {index} must contain x,y,v")
        try:
            target = Target(*(int(value) for value in values))
        except ValueError as error:
            raise ValueError(f"target slot {index} contains a non-integer") from error
        targets.append(target)

    return Frame(t_ms=t_ms, targets=tuple(targets))


def frame_delta_ms(previous_t_ms: int | None, current_t_ms: int) -> int | None:
    if previous_t_ms is None:
        return None
    if current_t_ms >= previous_t_ms:
        return current_t_ms - previous_t_ms
    if previous_t_ms >= ROLLOVER_HIGH_WATER and current_t_ms <= ROLLOVER_LOW_WATER:
        return UINT32_MODULUS - previous_t_ms + current_t_ms
    return None