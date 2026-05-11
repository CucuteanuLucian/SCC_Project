import unittest

from models import Process, Processor, SystemProcess


class TestProcess(unittest.TestCase):
    def test_initial_state(self):
        process = Process(1, 0.0, 10.0, [5.0, 3.0], [2.0])

        self.assertEqual(process.pid, 1)
        self.assertEqual(process.release_time, 0.0)
        self.assertEqual(process.memory_required, 10.0)
        self.assertEqual(process.burst_remaining, 5.0)
        self.assertEqual(process.state, "NEW")
        self.assertFalse(process.in_memory)
        self.assertFalse(process.is_done())

    def test_is_done_flag(self):
        process = Process(2, 1.0, 2.0, [1.0], [])
        process.state = "DONE"

        self.assertTrue(process.is_done())

    def test_repr_contains_pid(self):
        process = Process(3, 0.0, 1.0, [1.0], [])
        self.assertIn("Process(pid=3", repr(process))


class TestProcessor(unittest.TestCase):
    def test_is_free_when_idle(self):
        processor = Processor(0)
        self.assertTrue(processor.is_free(0.0))

    def test_is_free_after_busy(self):
        processor = Processor(1)
        processor.current_process = "x"
        processor.busy_until = 10.0
        self.assertFalse(processor.is_free(5.0))
        self.assertTrue(processor.is_free(10.0))

    def test_repr_contains_proc_id(self):
        processor = Processor(2)
        self.assertIn("Processor(2", repr(processor))


class TestSystemProcess(unittest.TestCase):
    def test_initial_values(self):
        system = SystemProcess(3.0)

        self.assertEqual(system.period, 3.0)
        self.assertEqual(system.next_release, 3.0)
        self.assertEqual(system.state, "IDLE")
        self.assertEqual(system.pending_syscalls, [])

    def test_repr_contains_state(self):
        system = SystemProcess(5.0)
        self.assertIn("SystemProcess(state=IDLE", repr(system))


if __name__ == "__main__":
    unittest.main()
