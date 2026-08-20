# pyright: reportUndefinedVariable=false

import datetime

APP_CONFIG = pyscript.app_config
FRAME_ENTITY = str(APP_CONFIG.get("frame_entity", "sensor.ld2450_atomic_frame"))
OUTPUT_CSV = str(APP_CONFIG.get("output_csv", "/config/ld2450_frames.csv"))
FLUSH_SECONDS = int(APP_CONFIG.get("flush_seconds", 5))
MAX_BUFFER_ROWS = int(APP_CONFIG.get("max_buffer_rows", 5000))

HEADER = "wall_iso,t_ms,dt_ms,x1,y1,v1,x2,y2,v2,x3,y3,v3\n"
UINT32_MODULUS = 1 << 32
ROLLOVER_HIGH_WATER = 0xF0000000
ROLLOVER_LOW_WATER = 0x0FFFFFFF

_last_t_ms = None
_pending_rows = []
_frame_trigger_refs = []


if not FRAME_ENTITY.startswith("sensor."):
    raise ValueError("frame_entity must be in the sensor domain")
if not OUTPUT_CSV.startswith("/config/") or "/../" in OUTPUT_CSV:
    raise ValueError("output_csv must be an absolute path below /config")
if not 1 <= FLUSH_SECONDS <= 300:
    raise ValueError("flush_seconds must be between 1 and 300")
if not 100 <= MAX_BUFFER_ROWS <= 100000:
    raise ValueError("max_buffer_rows must be between 100 and 100000")


def _parse_payload(value):
    parts = value.split("|")
    if len(parts) != 4:
        return None

    try:
        t_ms = int(parts[0])
    except ValueError:
        return None

    if t_ms < 0 or t_ms >= UINT32_MODULUS:
        return None

    slots = []
    for segment in parts[1:]:
        values = segment.split(",")
        if len(values) != 3:
            return None
        try:
            slots.append([int(values[0]), int(values[1]), int(values[2])])
        except ValueError:
            return None

    return t_ms, slots


def _frame_delta_ms(previous_t_ms, current_t_ms):
    if previous_t_ms is None:
        return None
    if current_t_ms >= previous_t_ms:
        return current_t_ms - previous_t_ms
    if previous_t_ms >= ROLLOVER_HIGH_WATER and current_t_ms <= ROLLOVER_LOW_WATER:
        return UINT32_MODULUS - previous_t_ms + current_t_ms
    return None


@pyscript_executor
def _append_rows(output_csv, header, rows):
    with open(output_csv, "a+", encoding="utf-8", newline="") as output:
        needs_header = output.tell() == 0
        if needs_header:
            output.write(header)
        output.writelines(rows)


def _flush_pending_rows():
    global _pending_rows

    if len(_pending_rows) == 0:
        return

    rows = _pending_rows
    _pending_rows = []
    try:
        _append_rows(OUTPUT_CSV, HEADER, rows)
    except Exception as error:
        _pending_rows = rows + _pending_rows
        log.error(f"failed to append atomic frame CSV: {error}")


def _install_frame_trigger(entity_id):
    @state_trigger(entity_id)
    def on_atomic_frame(value=None, **kwargs):
        global _last_t_ms
        global _pending_rows
        _ = kwargs

        if value is None or value in ("unknown", "unavailable"):
            return

        parsed = _parse_payload(value)
        if parsed is None:
            return

        t_ms, slots = parsed
        delta = _frame_delta_ms(_last_t_ms, t_ms)
        _last_t_ms = t_ms

        wall_iso = datetime.datetime.now().astimezone().isoformat(timespec="milliseconds")
        values = [wall_iso, str(t_ms), "" if delta is None else str(delta)]
        for target in slots:
            values.append(str(target[0]))
            values.append(str(target[1]))
            values.append(str(target[2]))
        _pending_rows.append(",".join(values) + "\n")

        if len(_pending_rows) > MAX_BUFFER_ROWS:
            dropped = len(_pending_rows) - MAX_BUFFER_ROWS
            _pending_rows = _pending_rows[dropped:]
            log.error(f"atomic frame buffer full; dropped {dropped} oldest rows")

    return on_atomic_frame


_frame_trigger_refs.append(_install_frame_trigger(FRAME_ENTITY))


@time_trigger(f"period(now, {FLUSH_SECONDS}s)")
def flush_atomic_frames():
    _flush_pending_rows()


@time_trigger("shutdown")
def flush_atomic_frames_on_shutdown():
    _flush_pending_rows()