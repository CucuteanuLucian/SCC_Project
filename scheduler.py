"""
Round-Robin scheduler implementation.
"""
from typing import List, Optional
from queue import Queue
from process import Process, ProcessState
from processor import Processor


class Scheduler:
    """Implements Round-Robin scheduling policy."""
    
    def __init__(self, num_processors: int, time_slice: int):
        """
        Initialize scheduler.
        
        Args:
            num_processors: Number of CPUs available
            time_slice: Time slice for Round-Robin (quantum)
        """
        self.num_processors = num_processors
        self.time_slice = time_slice
        self.ready_queue = Queue()
        self.processors = [Processor(i) for i in range(num_processors)]
        self.processes_scheduled = {}  # {process_id: processor_id}
    
    def enqueue(self, process: Process):
        """
        Add process to ready queue.
        
        Args:
            process: Process to enqueue
        """
        if process.state != ProcessState.TERMINATED:
            self.ready_queue.append(process)
            process.state = ProcessState.READY
    
    def schedule(self, current_time: int, system_process: Optional[Process] = None) -> List[tuple]:
        """
        Run scheduling algorithm to assign processes to CPUs.
        
        Args:
            current_time: Current simulation time
            system_process: System process (higher priority)
            
        Returns:
            List of (processor_id, process) tuples for new assignments
        """
        assignments = []
        
        # First, schedule system process if available (highest priority)
        if system_process and not system_process.state == ProcessState.TERMINATED:
            processor = self._find_best_processor(system_process, current_time)
            if processor:
                processor.assign_process(system_process, system_process.remaining_burst_time, current_time)
                system_process.state = ProcessState.RUNNING
                assignments.append((processor.id, system_process))
        
        # Schedule user processes with affinity preference
        for processor in self.processors:
            if not processor.busy and self.ready_queue:
                # Try to schedule process with last processor affinity
                scheduled = False
                
                # Check if any process in queue has affinity for this processor
                for process in self.ready_queue:
                    if process.last_processor == processor.id:
                        self.ready_queue.remove(process)
                        processor.assign_process(process, self.time_slice, current_time)
                        process.state = ProcessState.RUNNING
                        assignments.append((processor.id, process))
                        scheduled = True
                        break
                
                # If no affinity match, take first process from queue
                if not scheduled and self.ready_queue:
                    process = self.ready_queue.popleft()
                    processor.assign_process(process, self.time_slice, current_time)
                    process.state = ProcessState.RUNNING
                    assignments.append((processor.id, process))
        
        return assignments
    
    def _find_best_processor(self, process: Process, current_time: int) -> Optional[Processor]:
        """
        Find best processor for process assignment.
        
        Prefers: (1) Last processor if free, (2) Any free processor
        
        Args:
            process: Process to schedule
            current_time: Current simulation time
            
        Returns:
            Processor or None if all busy
        """
        # Try last processor first
        if process.last_processor is not None:
            proc = self.processors[process.last_processor]
            if not proc.busy:
                return proc
        
        # Find first free processor
        for proc in self.processors:
            if not proc.busy:
                return proc
        
        return None
    
    def preempt(self, process: Process):
        """
        Preempt a process and return to ready queue.
        
        Args:
            process: Process to preempt
        """
        for processor in self.processors:
            if processor.current_process == process:
                processor.release()
                if not process.is_terminated():
                    self.ready_queue.append(process)
                    process.state = ProcessState.READY
                break
    
    def get_free_processors(self) -> List[Processor]:
        """Get list of free processors."""
        return [p for p in self.processors if not p.busy]
    
    def get_ready_queue_length(self) -> int:
        """Get number of processes in ready queue."""
        return len(self.ready_queue)
    
    def get_processor(self, processor_id: int) -> Processor:
        """Get processor by ID."""
        if 0 <= processor_id < len(self.processors):
            return self.processors[processor_id]
        return None
    
    def __repr__(self) -> str:
        free_count = sum(1 for p in self.processors if not p.busy)
        return f"Scheduler(processors={self.num_processors}, free={free_count}, " \
               f"ready_queue={len(self.ready_queue)}, time_slice={self.time_slice})"
