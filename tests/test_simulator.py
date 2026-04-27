"""
Unit tests for OS Process Scheduling Simulator.
Phase 2+ testing (not included in Phase 1).
"""
import unittest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from process import Process, ProcessState
from processor import Processor
from scheduler import Scheduler
from memory_manager import MemoryManager
from system_call_manager import SystemCallManager
from simulator import Simulator, Event, EventType


class TestProcess(unittest.TestCase):
    """Test Process class."""
    
    def test_process_creation(self):
        """Test process initialization."""
        p = Process("P1", 0, 256, [5, 2, 3])
        self.assertEqual(p.id, "P1")
        self.assertEqual(p.release_time, 0)
        self.assertEqual(p.memory_required, 256)
        self.assertEqual(p.bursts, [5, 2, 3])
    
    def test_burst_types(self):
        """Test burst type detection."""
        p = Process("P1", 0, 256, [5, 2, 3, 4])
        self.assertEqual(p.get_current_burst_type(), "CPU")  # index 0
        p.advance_burst()
        self.assertEqual(p.get_current_burst_type(), "SYS")  # index 1
        p.advance_burst()
        self.assertEqual(p.get_current_burst_type(), "CPU")  # index 2
    
    def test_process_termination(self):
        """Test process termination detection."""
        p = Process("P1", 0, 256, [5, 2])
        self.assertFalse(p.is_terminated())
        p.advance_burst()
        self.assertFalse(p.is_terminated())
        p.advance_burst()
        self.assertTrue(p.is_terminated())


class TestProcessor(unittest.TestCase):
    """Test Processor class."""
    
    def test_processor_creation(self):
        """Test processor initialization."""
        cpu = Processor(0)
        self.assertEqual(cpu.id, 0)
        self.assertFalse(cpu.busy)
        self.assertIsNone(cpu.current_process)
    
    def test_process_assignment(self):
        """Test assigning process to processor."""
        cpu = Processor(0)
        p = Process("P1", 0, 256, [5])
        cpu.assign_process(p, 4, 0)
        
        self.assertTrue(cpu.busy)
        self.assertEqual(cpu.current_process, p)
        self.assertEqual(cpu.time_slice_remaining, 4)
    
    def test_processor_tick(self):
        """Test processor tick mechanism."""
        cpu = Processor(0)
        p = Process("P1", 0, 256, [5])
        cpu.assign_process(p, 3, 0)
        
        result = cpu.tick()
        self.assertEqual(p.remaining_burst_time, 4)
        self.assertEqual(cpu.time_slice_remaining, 2)


class TestMemoryManager(unittest.TestCase):
    """Test MemoryManager class."""
    
    def test_memory_initialization(self):
        """Test memory manager setup."""
        mem = MemoryManager(512, 100)
        self.assertEqual(mem.ram_size, 512)
        self.assertEqual(mem.disk_transfer_rate, 100)
        self.assertEqual(mem.ram_free, 512)
    
    def test_process_loading(self):
        """Test loading process into memory."""
        mem = MemoryManager(512, 100)
        p = Process("P1", 0, 256, [5])
        
        transfer_time = mem.load_process(p)
        self.assertTrue(mem.is_in_ram(p.id))
        self.assertEqual(mem.ram_free, 256)
    
    def test_transfer_time_calculation(self):
        """Test transfer time calculation."""
        mem = MemoryManager(512, 100)
        
        # 100 units with rate 100 = 1 time unit
        self.assertEqual(mem.calculate_transfer_time(100), 1)
        
        # 150 units with rate 100 = 2 time units
        self.assertEqual(mem.calculate_transfer_time(150), 2)


class TestScheduler(unittest.TestCase):
    """Test Scheduler class."""
    
    def test_scheduler_creation(self):
        """Test scheduler initialization."""
        sched = Scheduler(2, 4)
        self.assertEqual(sched.num_processors, 2)
        self.assertEqual(sched.time_slice, 4)
        self.assertEqual(len(sched.processors), 2)
    
    def test_ready_queue(self):
        """Test enqueuing processes."""
        sched = Scheduler(2, 4)
        p1 = Process("P1", 0, 256, [5])
        p2 = Process("P2", 0, 128, [3])
        
        sched.enqueue(p1)
        sched.enqueue(p2)
        
        self.assertEqual(sched.get_ready_queue_length(), 2)
    
    def test_process_scheduling(self):
        """Test process scheduling to processors."""
        sched = Scheduler(2, 4)
        p = Process("P1", 0, 256, [5])
        sched.enqueue(p)
        
        assignments = sched.schedule(0)
        
        self.assertEqual(len(assignments), 1)
        self.assertEqual(assignments[0][1].id, "P1")


class TestSystemCallManager(unittest.TestCase):
    """Test SystemCallManager class."""
    
    def test_syscall_manager_creation(self):
        """Test system call manager initialization."""
        scm = SystemCallManager(10)
        self.assertEqual(scm.system_period, 10)
        self.assertEqual(scm.get_syscall_queue_length(), 0)
    
    def test_syscall_request(self):
        """Test requesting syscall."""
        scm = SystemCallManager(10)
        p = Process("P1", 0, 256, [5, 2, 3])
        
        scm.request_syscall(p)
        
        self.assertEqual(scm.get_syscall_queue_length(), 1)
        self.assertEqual(p.state, ProcessState.WAITING)


class TestSimulator(unittest.TestCase):
    """Test Simulator class."""
    
    def test_simulator_creation(self):
        """Test simulator initialization."""
        sim = Simulator(2, 512, 4, 10, 100)
        self.assertEqual(sim.num_processors, 2)
        self.assertEqual(sim.ram_size, 512)
    
    def test_add_process(self):
        """Test adding process to simulator."""
        sim = Simulator(2, 512, 4, 10, 100)
        p = Process("P1", 0, 256, [5, 2, 3])
        
        sim.add_process(p)
        
        self.assertIn("P1", sim.processes)
        self.assertTrue(len(sim.event_queue) > 0)
    
    def test_simple_simulation(self):
        """Test simple simulation run."""
        sim = Simulator(2, 512, 4, 10, 100)
        
        p1 = Process("P1", 0, 256, [5])
        sim.add_process(p1)
        
        sim.run(end_time=20)
        
        self.assertTrue(len(sim.log_entries) > 0)


def run_tests():
    """Run all tests."""
    unittest.main(argv=[''], exit=False, verbosity=2)


if __name__ == '__main__':
    run_tests()
