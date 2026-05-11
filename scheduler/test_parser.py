import os
import tempfile
import unittest

from parser import parse_file


class TestParser(unittest.TestCase):
    def test_parse_file_returns_parameters_and_processes(self):
        content = """
# sample simulator input
PROCESSORS 2
MEMORY 8
TIME_SLICE 1
SYSCALL_PERIOD 5
DISK_TRANSFER_RATE 2

PROCESS 10 0 3
BURSTS 2 4 1 2
PROCESS 11 1 4
BURSTS 1 3
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as fh:
            fh.write(content)
            path = fh.name

        try:
            params, processes = parse_file(path)

            self.assertEqual(params["processors"], 2)
            self.assertEqual(params["memory"], 8.0)
            self.assertEqual(params["time_slice"], 1.0)
            self.assertEqual(params["syscall_period"], 5.0)
            self.assertEqual(params["disk_transfer_rate"], 2.0)
            self.assertEqual(len(processes), 2)
            self.assertEqual(processes[0].pid, 10)
            self.assertEqual(processes[0].bursts, [4.0, 2.0])
            self.assertEqual(processes[0].syscall_times, [1.0])
            self.assertEqual(processes[1].bursts, [3.0])
            self.assertEqual(processes[1].syscall_times, [])
        finally:
            os.remove(path)

    def test_missing_required_parameter_raises(self):
        content = """
PROCESSORS 1
MEMORY 5
TIME_SLICE 1
DISK_TRANSFER_RATE 2
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as fh:
            fh.write(content)
            path = fh.name

        try:
            with self.assertRaises(AssertionError):
                parse_file(path)
        finally:
            os.remove(path)

    def test_bursts_without_process_raises(self):
        content = """
PROCESSORS 1
MEMORY 5
TIME_SLICE 1
SYSCALL_PERIOD 2
DISK_TRANSFER_RATE 1
BURSTS 1 3
"""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as fh:
            fh.write(content)
            path = fh.name

        try:
            with self.assertRaises(AssertionError):
                parse_file(path)
        finally:
            os.remove(path)


if __name__ == "__main__":
    unittest.main()
