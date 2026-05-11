import unittest

from models import Process
from simulator import Simulator


class FakeMemoryManager:
    def __init__(self, total_ram, disk_transfer_rate, used_ram=0.0, in_memory=None):
        self.total_ram = total_ram
        self.disk_transfer_rate = disk_transfer_rate
        self.used_ram = used_ram
        self._in_memory = list(in_memory or [])
        self.touched = []

    def touch(self, process):
        self.touched.append(process)
        if process in self._in_memory:
            self._in_memory.remove(process)
            self._in_memory.append(process)

    def evict_lru(self):
        for i, process in enumerate(self._in_memory):
            if process.state not in ["RUNNING", "SYSCALL", "WAITING_MEM"]:
                victim = self._in_memory.pop(i)
                victim.in_memory = False
                self.used_ram -= victim.memory_required
                return victim
        raise RuntimeError("Out of Memory: No safe processes available to evict.")

    def complete_load(self, process):
        self.used_ram += process.memory_required
        process.in_memory = True
        self._in_memory.append(process)


class TestSimulator(unittest.TestCase):
    def setUp(self):
        self.params = {
            "processors": 1,
            "memory": 4.0,
            "time_slice": 1.0,
            "syscall_period": 10.0,
            "disk_transfer_rate": 1.0,
        }

    def test_try_run_syscall_schedules_syscall_if_cpu_free(self):
        sim = Simulator(self.params, [])
        process = Process(5, 0.0, 1.0, [1.0], [])
        sim.sys_proc.state = "WAITING"
        sim.sys_proc.pending_syscalls = [(process, 0.5)]
        sim.current_time = 2.0

        sim._try_run_syscall()

        self.assertEqual(sim.sys_proc.state, "RUNNING")
        self.assertEqual(sim.processors[0].current_process, "__system__")
        self.assertEqual(sim.processors[0].busy_until, 2.5)
        self.assertEqual(len(sim.sys_proc.pending_syscalls), 0)
        self.assertEqual(sim._events[0][2], "SYSCALL_DONE")

    def test_start_load_returns_false_with_no_safe_evictions(self):
        sim = Simulator(self.params, [])
        busy_proc = Process(1, 0.0, 4.0, [2.0], [])
        busy_proc.in_memory = True
        busy_proc.state = "RUNNING"
        sim.mem = FakeMemoryManager(total_ram=4.0, disk_transfer_rate=1.0,
                                    used_ram=4.0, in_memory=[busy_proc])
        process = Process(2, 0.0, 3.0, [1.0], [])

        result = sim._start_load(process)

        self.assertFalse(result)
        self.assertFalse(sim._disk_busy)
        self.assertEqual(process.state, "NEW")

    def test_start_load_evicts_and_schedules_mem_ready(self):
        evictable = Process(3, 0.0, 3.0, [2.0], [])
        evictable.in_memory = True
        evictable.state = "READY"
        sim = Simulator(self.params, [])
        sim.mem = FakeMemoryManager(total_ram=4.0, disk_transfer_rate=1.0,
                                    used_ram=3.0, in_memory=[evictable])
        process = Process(4, 0.0, 3.0, [1.0], [])

        result = sim._start_load(process)

        self.assertTrue(result)
        self.assertTrue(sim._disk_busy)
        self.assertEqual(len(sim.event_log), 2)
        self.assertEqual(sim._events[0][2], "MEM_READY")
        self.assertEqual(sim._events[0][0], 6.0)
        self.assertEqual(process.state, "WAITING_MEM")

    def test_schedule_assigns_ready_process_to_free_processor(self):
        process = Process(5, 0.0, 1.0, [2.0], [])
        process.state = "READY"
        process.in_memory = True
        sim = Simulator(self.params, [process])
        sim.mem = FakeMemoryManager(total_ram=4.0, disk_transfer_rate=1.0,
                                    used_ram=1.0, in_memory=[process])
        sim.ready_queue = [process]

        sim._schedule()

        self.assertEqual(process.state, "RUNNING")
        self.assertEqual(sim.processors[0].current_process, process)
        self.assertEqual(sim.processors[0].busy_until, 1.0)
        self.assertEqual(len(sim.event_log), 1)
        self.assertEqual(sim._events[0][2], "CPU_DONE")

    def test_run_completes_process_with_fake_memory_manager(self):
        process = Process(6, 0.0, 2.0, [1.0], [])
        sim = Simulator(self.params, [process])
        sim.mem = FakeMemoryManager(total_ram=4.0, disk_transfer_rate=1.0,
                                    used_ram=0.0, in_memory=[])

        event_log = sim.run()

        self.assertTrue(process.is_done())
        self.assertEqual(event_log[-1]["type"], "SIMULATION_END")
        self.assertIn("DONE", [e["type"] for e in event_log])


if __name__ == "__main__":
    unittest.main()
