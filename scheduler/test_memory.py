import unittest

from models import Process
from memory import MemoryManager


class TestMemoryManager(unittest.TestCase):
    def setUp(self):
        self.manager = MemoryManager(total_ram=10.0, disk_transfer_rate=1.0)

    def test_complete_load_marks_process_in_memory(self):
        process = Process(1, 0.0, 3.0, [2.0], [])

        self.manager.complete_load(process)

        self.assertTrue(process.in_memory)
        self.assertEqual(self.manager.used_ram, 3.0)
        self.assertIn(process, self.manager._in_memory)

    def test_touch_moves_process_to_mru(self):
        a = Process(1, 0.0, 2.0, [1.0], [])
        b = Process(2, 0.0, 2.0, [1.0], [])
        self.manager.complete_load(a)
        self.manager.complete_load(b)

        self.manager.touch(a)

        self.assertEqual(self.manager._in_memory[-1], a)

    def test_evict_lru_returns_oldest_nonbusy(self):
        a = Process(1, 0.0, 2.0, [1.0], [])
        b = Process(2, 0.0, 2.0, [1.0], [])
        self.manager.complete_load(a)
        self.manager.complete_load(b)
        a.state = "READY"
        b.state = "RUNNING"

        victim = self.manager.evict_lru()

        self.assertIs(victim, a)
        self.assertFalse(victim.in_memory)
        self.assertEqual(self.manager.used_ram, 2.0)
        self.assertNotIn(victim, self.manager._in_memory)

    def test_evict_lru_raises_when_no_safe_process(self):
        a = Process(1, 0.0, 2.0, [1.0], [])
        self.manager.complete_load(a)
        a.state = "RUNNING"

        with self.assertRaises(RuntimeError):
            self.manager.evict_lru()


if __name__ == "__main__":
    unittest.main()
