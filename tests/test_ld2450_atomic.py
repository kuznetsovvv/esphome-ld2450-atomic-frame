import unittest

from tools.ld2450_atomic import frame_delta_ms, parse_payload


class ParsePayloadTests(unittest.TestCase):
    def test_parses_three_slots_and_speed_units(self):
        frame = parse_payload("123|-400,1200,25|300,1800,-10|0,0,0")

        self.assertEqual(frame.t_ms, 123)
        self.assertEqual(frame.targets[0].x_mm, -400)
        self.assertEqual(frame.targets[0].speed_mm_s, 250)
        self.assertTrue(frame.targets[1].present)
        self.assertEqual(frame.targets[1].speed_mm_s, -100)
        self.assertFalse(frame.targets[2].present)
        self.assertTrue(frame.has_targets)

    def test_accepts_empty_frame(self):
        frame = parse_payload("0|0,0,0|0,0,0|0,0,0")
        self.assertFalse(frame.has_targets)

    def test_rejects_wrong_slot_count(self):
        with self.assertRaisesRegex(ValueError, "three target slots"):
            parse_payload("1|0,0,0")

    def test_rejects_non_integer_slot(self):
        with self.assertRaisesRegex(ValueError, "non-integer"):
            parse_payload("1|a,0,0|0,0,0|0,0,0")

    def test_rejects_timestamp_outside_uint32(self):
        with self.assertRaisesRegex(ValueError, "unsigned 32-bit"):
            parse_payload("4294967296|0,0,0|0,0,0|0,0,0")


class FrameDeltaTests(unittest.TestCase):
    def test_normal_delta(self):
        self.assertEqual(frame_delta_ms(100, 175), 75)

    def test_rollover_delta(self):
        self.assertEqual(frame_delta_ms(0xFFFFFFF0, 0x20), 48)

    def test_probable_reboot_returns_none(self):
        self.assertIsNone(frame_delta_ms(500_000, 10_000))

    def test_first_frame_returns_none(self):
        self.assertIsNone(frame_delta_ms(None, 100))


if __name__ == "__main__":
    unittest.main()