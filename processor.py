"""
Processor (CPU) representation and management.
"""


class Processor:
    """Represents a CPU processor in the system."""
    
    def __init__(self, processor_id: int):
        """
        Initialize a processor.
        
        Args:
            processor_id: Unique processor identifier (0, 1, 2, ...)
        """
        self.id = processor_id
        self.current_process = None
        self.time_slice_remaining = 0
        self.busy = False
        self.start_time = None  # When current process started on this processor
    
    def assign_process(self, process, time_slice: int, current_time: int):
        """
        Assign a process to this processor.
        
        Args:
            process: Process object to assign
            time_slice: Time slice allocated
            current_time: Current simulation time
        """
        self.current_process = process
        self.time_slice_remaining = time_slice
        self.busy = True
        self.start_time = current_time
        process.last_processor = self.id
    
    def tick(self) -> bool:
        """
        Decrement time slice by 1 unit.
        
        Returns:
            True if time slice expired, False otherwise
        """
        if self.busy and self.current_process:
            self.time_slice_remaining -= 1
            self.current_process.remaining_burst_time -= 1
            
            # Check if burst is complete
            if self.current_process.remaining_burst_time == 0:
                return "burst_complete"
            
            # Check if time slice expired
            if self.time_slice_remaining == 0:
                return "time_slice_expired"
        
        return False
    
    def release(self):
        """Release the current process from this processor."""
        self.current_process = None
        self.time_slice_remaining = 0
        self.busy = False
        self.start_time = None
    
    def __repr__(self) -> str:
        process_str = self.current_process.id if self.current_process else "idle"
        return f"Processor({self.id}, process={process_str}, time_slice={self.time_slice_remaining})"
