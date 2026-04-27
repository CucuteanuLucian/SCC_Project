"""
Process representation and state management.
"""
from typing import List


class ProcessState:
    """Process state constants."""
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    ON_DISK = "on_disk"
    TERMINATED = "terminated"


class Process:
    """Represents a process in the system."""
    
    def __init__(self, process_id: str, release_time: int, memory_required: int, 
                 bursts: List[int]):
        """
        Initialize a process.
        
        Args:
            process_id: Unique process identifier (e.g., "P1")
            release_time: Time when process enters the system
            memory_required: Memory requirement in units
            bursts: List of alternating CPU and system call times
        """
        self.id = process_id
        self.release_time = release_time
        self.memory_required = memory_required
        self.bursts = bursts
        self.current_burst_index = 0
        self.remaining_burst_time = bursts[0] if bursts else 0
        self.state = ProcessState.NEW
        self.last_processor = None
        self.last_access_time = 0
        self.memory_location = None  # Physical memory address or None if on disk
        self.creation_time = release_time
        
    def get_current_burst_type(self) -> str:
        """
        Get type of current burst: CPU (even index) or SYS (odd index).
        """
        if self.current_burst_index >= len(self.bursts):
            return "NONE"
        return "CPU" if self.current_burst_index % 2 == 0 else "SYS"
    
    def advance_burst(self):
        """Move to next burst sequence."""
        self.current_burst_index += 1
        if self.current_burst_index < len(self.bursts):
            self.remaining_burst_time = self.bursts[self.current_burst_index]
        else:
            self.remaining_burst_time = 0
    
    def is_terminated(self) -> bool:
        """Check if process has completed all bursts."""
        return self.current_burst_index >= len(self.bursts)
    
    def __repr__(self) -> str:
        return f"Process({self.id}, state={self.state}, burst={self.current_burst_index}/{len(self.bursts)})"
