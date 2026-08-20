import pathlib
import types
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "pyscript" / "apps" / "ld2450_atomic_logger" / "__init__.py"


def passthrough_decorator(*_args, **_kwargs):
    _ = (_args, _kwargs)

    def decorate(function):
        return function

    return decorate


class LogStub:
    def __init__(self):
        self.errors = []

    def error(self, message):
        self.errors.append(message)


class PyscriptAppTests(unittest.TestCase):
    def load_app(self):
        namespace = {
            "pyscript": types.SimpleNamespace(
                app_config={
                    "frame_entity": "sensor.test_atomic_frame",
                    "output_csv": "/config/test_frames.csv",
                    "flush_seconds": 5,
                    "max_buffer_rows": 100,
                }
            ),
            "state_trigger": passthrough_decorator,
            "time_trigger": passthrough_decorator,
            "pyscript_executor": lambda function: function,
            "log": LogStub(),
        }
        source = APP_PATH.read_text(encoding="utf-8")
        exec(compile(source, str(APP_PATH), "exec"), namespace)
        return namespace

    def test_trigger_buffers_and_flushes_rows(self):
        app = self.load_app()
        writes = []
        app["_append_rows"] = lambda output_csv, header, rows: writes.append(
            (output_csv, header, list(rows))
        )

        trigger = app["_frame_trigger_refs"][0]
        trigger(value="100|-10,20,3|0,0,0|0,0,0")
        trigger(value="175|-10,20,3|0,0,0|0,0,0")
        app["flush_atomic_frames"]()

        self.assertEqual(len(writes), 1)
        output_csv, header, rows = writes[0]
        self.assertEqual(output_csv, "/config/test_frames.csv")
        self.assertIn("dt_ms", header)
        self.assertEqual(len(rows), 2)
        self.assertIn(",100,,-10,20,3,", rows[0])
        self.assertIn(",175,75,-10,20,3,", rows[1])
        self.assertEqual(app["_pending_rows"], [])

    def test_executor_writes_one_header_and_appends(self):
        app = self.load_app()
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "frames.csv"
            app["_append_rows"](str(path), "header\n", ["one\n"])
            app["_append_rows"](str(path), "header\n", ["two\n"])

            self.assertEqual(path.read_text(encoding="utf-8"), "header\none\ntwo\n")

    def test_probable_reboot_blanks_delta(self):
        app = self.load_app()
        trigger = app["_frame_trigger_refs"][0]

        trigger(value="500000|1,2,3|0,0,0|0,0,0")
        trigger(value="10000|1,2,3|0,0,0|0,0,0")

        self.assertIn(",10000,,1,2,3,", app["_pending_rows"][1])

    def test_invalid_payload_is_ignored(self):
        app = self.load_app()
        trigger = app["_frame_trigger_refs"][0]

        trigger(value="not-a-frame")

        self.assertEqual(app["_pending_rows"], [])


if __name__ == "__main__":
    unittest.main()