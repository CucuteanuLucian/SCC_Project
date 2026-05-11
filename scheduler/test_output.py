import os
import tempfile
import unittest

from output import write_text_report, write_gantt


class TestOutput(unittest.TestCase):
    def test_write_text_report_contains_each_event(self):
        event_log = [
            {"time": 0.0, "end_time": 1.0, "type": "RUN", "pid": 1, "processor": 0},
            {"time": 1.0, "end_time": 1.0, "type": "DONE", "pid": 1},
        ]

        with tempfile.NamedTemporaryFile(mode="r", delete=False, suffix=".txt") as fh:
            path = fh.name

        try:
            write_text_report(event_log, path)
            with open(path, "r") as read_fh:
                contents = read_fh.read()

            self.assertIn("TIME", contents)
            self.assertIn("RUN", contents)
            self.assertIn("DONE", contents)
            self.assertIn("pid", contents.lower())
        finally:
            os.remove(path)

    def test_write_gantt_produces_processor_rows(self):
        event_log = [
            {"time": 0.0, "end_time": 2.0, "type": "RUN", "pid": 3, "processor": 0},
            {"time": 2.0, "end_time": 3.0, "type": "SYS_RUN", "processor": 1},
            {"time": 3.0, "end_time": 4.0, "type": "SWAP_IN", "processor": 0},
        ]

        with tempfile.NamedTemporaryFile(mode="r", delete=False, suffix=".txt") as fh:
            path = fh.name

        try:
            write_gantt(event_log, 2, path)
            with open(path, "r") as read_fh:
                contents = read_fh.read()

            self.assertIn("CPU", contents)
            self.assertIn("P0", contents)
            self.assertIn("P1", contents)
            self.assertIn("Legend", contents)
            self.assertIn("S", contents)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
