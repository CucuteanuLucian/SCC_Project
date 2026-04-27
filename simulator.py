"""
Simulation engine: discrete event simulator with event queue.
"""
from typing import List, Dict, Optional, Tuple
from priority_queue import PriorityQueue
from process import Process, ProcessState
from scheduler import Scheduler
from memory_manager import MemoryManager
from system_call_manager import SystemCallManager
from processor import Processor


class EventType:
    """Types of events in the simulation."""
    PROCESS_RELEASE = "process_release"
    PROCESS_LOAD_COMPLETE = "process_load_complete"
    TIME_SLICE_EXPIRED = "time_slice_expired"
    BURST_COMPLETE = "burst_complete"
    SYSTEM_PROCESS_RELEASE = "system_process_release"
    SYSTEM_CALL_COMPLETE = "system_call_complete"
    SIM_END = "sim_end"


class Event:
    """Represents a simulation event."""
    
    def __init__(self, timestamp: int, event_type: EventType, 
                 process_id: str = None, processor_id: int = None, data: Dict = None):
        """
        Initialize event.
        
        Args:
            timestamp: Time when event occurs
            event_type: Type of event
            process_id: Associated process ID
            processor_id: Associated processor ID
            data: Additional event data
        """
        self.timestamp = timestamp
        self.event_type = event_type
        self.process_id = process_id
        self.processor_id = processor_id
        self.data = data or {}
    
    def __lt__(self, other):
        """Enable heap comparison by timestamp."""
        if self.timestamp != other.timestamp:
            return self.timestamp < other.timestamp
        # Break ties by event type priority
        type_priority = {
            EventType.PROCESS_RELEASE: 0,
            EventType.PROCESS_LOAD_COMPLETE: 1,
            EventType.BURST_COMPLETE: 2,
            EventType.TIME_SLICE_EXPIRED: 3,
            EventType.SYSTEM_PROCESS_RELEASE: 4,
            EventType.SYSTEM_CALL_COMPLETE: 5,
        }
        return type_priority.get(self.event_type, 6) < type_priority.get(other.event_type, 6)
    
    def __repr__(self) -> str:
        return f"Event(time={self.timestamp}, type={self.event_type}, " \
               f"process={self.process_id}, processor={self.processor_id})"


class Simulator:
    """Main simulation engine."""
    
    def __init__(self, num_processors: int, ram_size: int, time_slice: int,
                 system_period: int, disk_transfer_rate: int):
        """
        Initialize simulator.
        
        Args:
            num_processors: Number of CPUs
            ram_size: Total RAM size
            time_slice: Time slice for Round-Robin
            system_period: System process release period
            disk_transfer_rate: Disk transfer rate (units per time unit)
        """
        self.current_time = 0
        self.num_processors = num_processors
        self.ram_size = ram_size
        self.time_slice = time_slice
        self.system_period = system_period
        self.disk_transfer_rate = disk_transfer_rate
        
        # Components
        self.scheduler = Scheduler(num_processors, time_slice)
        self.memory = MemoryManager(ram_size, disk_transfer_rate)
        self.syscall_mgr = SystemCallManager(system_period)
        
        # Simulation state
        self.event_queue = PriorityQueue()
        self.processes: Dict[str, Process] = {}
        self.process_timeline: List[Dict] = []  # For Gantt chart
        self.log_entries: List[str] = []
        self.system_process_active = False
    
    def add_process(self, process: Process):
        """Add process to simulation."""
        self.processes[process.id] = process
        # Schedule process release event
        self._schedule_event(Event(
            process.release_time,
            EventType.PROCESS_RELEASE,
            process_id=process.id
        ))
    
    def _schedule_event(self, event: Event):
        """Add event to priority queue."""
        self.event_queue.push(event)
    
    def _log(self, message: str):
        """Log simulation event."""
        log_msg = f"Time {self.current_time}: {message}"
        self.log_entries.append(log_msg)
        print(log_msg)
    
    def run(self, end_time: int = 1000):
        """
        Run the simulation until end_time or event queue is empty.
        
        Args:
            end_time: Maximum simulation time
        """
        self._log("=== Simulation Started ===")
        
        while not self.event_queue.is_empty() and self.current_time < end_time:
            # Get next event
            event = self.event_queue.pop()
            self.current_time = event.timestamp
            
            # Handle event
            if event.event_type == EventType.PROCESS_RELEASE:
                self._handle_process_release(event)
            elif event.event_type == EventType.PROCESS_LOAD_COMPLETE:
                self._handle_process_load_complete(event)
            elif event.event_type == EventType.BURST_COMPLETE:
                self._handle_burst_complete(event)
            elif event.event_type == EventType.TIME_SLICE_EXPIRED:
                self._handle_time_slice_expired(event)
            elif event.event_type == EventType.SYSTEM_PROCESS_RELEASE:
                self._handle_system_process_release(event)
            elif event.event_type == EventType.SYSTEM_CALL_COMPLETE:
                self._handle_system_call_complete(event)
            
            # Try to schedule processes
            self._run_scheduler()
        
        self._log("=== Simulation Completed ===")
    
    def _handle_process_release(self, event: Event):
        """Handle process release event."""
        process = self.processes[event.process_id]
        self._log(f"Process {process.id} released")
        
        # Try to load into memory
        transfer_time = self.memory.load_process(process)
        
        if transfer_time > 0:
            # Schedule load complete event
            self._schedule_event(Event(
                self.current_time + transfer_time,
                EventType.PROCESS_LOAD_COMPLETE,
                process_id=process.id
            ))
            self._log(f"Loading {process.id} into RAM (transfer_time={transfer_time})")
        else:
            # Already in RAM
            self.scheduler.enqueue(process)
            self._log(f"{process.id} loaded into RAM")
    
    def _handle_process_load_complete(self, event: Event):
        """Handle process load completion."""
        process = self.processes[event.process_id]
        self._log(f"{process.id} load complete")
        self.scheduler.enqueue(process)
    
    def _handle_burst_complete(self, event: Event):
        """Handle CPU burst completion."""
        process = self.processes[event.process_id]
        processor = self.scheduler.get_processor(event.processor_id)
        
        if processor and processor.current_process == process:
            self._log(f"{process.id} CPU burst complete on CPU{event.processor_id}")
            
            # Advance to next burst
            process.advance_burst()
            
            # Check if process needs syscall or is done
            current_burst_type = process.get_current_burst_type()
            
            if current_burst_type == "SYS":
                # Request syscall
                self.syscall_mgr.request_syscall(process)
                self._log(f"{process.id} requested syscall (duration={process.remaining_burst_time})")
            elif current_burst_type == "CPU":
                # More bursts, enqueue
                self.scheduler.enqueue(process)
                self._log(f"{process.id} returned to ready queue")
            else:
                # Process terminated
                process.state = ProcessState.TERMINATED
                self._log(f"{process.id} terminated")
            
            processor.release()
    
    def _handle_time_slice_expired(self, event: Event):
        """Handle time slice expiration."""
        process = self.processes[event.process_id]
        processor = self.scheduler.get_processor(event.processor_id)
        
        if processor and processor.current_process == process:
            self._log(f"Time slice expired for {process.id} on CPU{event.processor_id}")
            
            # Preempt and return to ready queue
            self.scheduler.enqueue(process)
            processor.release()
    
    def _handle_system_process_release(self, event: Event):
        """Handle system process release."""
        self._log(f"System process released")
        
        # System process will be scheduled in next scheduling pass
        syscall_count = self.syscall_mgr.get_syscall_queue_length()
        self._log(f"System process: {syscall_count} syscalls waiting")
    
    def _handle_system_call_complete(self, event: Event):
        """Handle system call completion."""
        process = self.syscall_mgr.handle_syscall_complete()
        
        if process:
            self._log(f"Syscall completed for {process.id}")
            self.scheduler.enqueue(process)
    
    def _run_scheduler(self):
        """Run scheduling algorithm."""
        # Check if system process should be released
        if self.syscall_mgr.should_release_system_process(self.current_time):
            system_process = self.syscall_mgr.release_system_process(self.current_time)
            
            # Schedule when system process finishes
            self._schedule_event(Event(
                self.current_time + system_process.remaining_burst_time,
                EventType.SYSTEM_CALL_COMPLETE
            ))
        else:
            system_process = None
        
        # Run scheduler
        assignments = self.scheduler.schedule(self.current_time, system_process)
        
        # Schedule time-related events for assigned processes
        for processor_id, process in assignments:
            processor = self.scheduler.get_processor(processor_id)
            
            self._log(f"{process.id} assigned to CPU{processor_id}")
            
            # Determine which event will occur first
            if isinstance(process, type(process)) and hasattr(process, 'is_system') and process.is_system:
                # System process: just runs for burst duration
                completion_time = self.current_time + process.remaining_burst_time
                self._schedule_event(Event(
                    completion_time,
                    EventType.BURST_COMPLETE,
                    process_id=process.id,
                    processor_id=processor_id
                ))
            else:
                # User process: check time slice vs burst duration
                burst_complete_time = self.current_time + process.remaining_burst_time
                time_slice_expire_time = self.current_time + self.time_slice
                
                if process.remaining_burst_time <= self.time_slice:
                    # Burst completes first
                    self._schedule_event(Event(
                        burst_complete_time,
                        EventType.BURST_COMPLETE,
                        process_id=process.id,
                        processor_id=processor_id
                    ))
                else:
                    # Time slice expires first
                    self._schedule_event(Event(
                        time_slice_expire_time,
                        EventType.TIME_SLICE_EXPIRED,
                        process_id=process.id,
                        processor_id=processor_id
                    ))
    
    def get_statistics(self) -> Dict:
        """Get simulation statistics."""
        terminated_processes = sum(1 for p in self.processes.values() 
                                   if p.state == ProcessState.TERMINATED)
        return {
            "current_time": self.current_time,
            "total_processes": len(self.processes),
            "terminated_processes": terminated_processes,
            "memory": self.memory.get_statistics(),
            "syscalls_handled": self.syscall_mgr.total_syscalls_handled,
            "log_entries": len(self.log_entries)
        }
