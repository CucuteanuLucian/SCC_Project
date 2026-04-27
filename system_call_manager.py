"""
System call management and system process handling.
"""
from typing import List
from queue import Queue
from process import Process, ProcessState


class SystemCallManager:
    """Manages system calls and the system process."""
    
    def __init__(self, system_period: int):
        """
        Initialize system call manager.
        
        Args:
            system_period: Period of system process release in time units
        """
        self.system_period = system_period
        self.syscall_queue = Queue()  # Queue of processes waiting for syscalls
        self.system_process_ready = False
        self.next_system_release = system_period
        self.system_process = None
        self.current_syscall = None
        self.total_syscalls_handled = 0
    
    def request_syscall(self, process: Process):
        """
        Request a system call for a process.
        
        Args:
            process: Process requesting syscall
        """
        self.syscall_queue.append(process)
        process.state = ProcessState.WAITING
    
    def get_next_system_release_time(self, current_time: int) -> int:
        """
        Get the next scheduled system process release time.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Next release time
        """
        if current_time >= self.next_system_release:
            return current_time
        return self.next_system_release
    
    def should_release_system_process(self, current_time: int) -> bool:
        """
        Check if system process should be released at current time.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            True if system process should be released
        """
        if current_time >= self.next_system_release and self.syscall_queue:
            return True
        return False
    
    def release_system_process(self, current_time: int) -> Process:
        """
        Release the system process to handle pending syscalls.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            System process object
        """
        # System process executes for duration of oldest syscall
        if self.syscall_queue:
            syscall_time = self.syscall_queue[0].remaining_burst_time
        else:
            syscall_time = 1
        
        # Create system process (transient)
        self.system_process = SystemProcess(current_time, syscall_time)
        self.next_system_release = current_time + self.system_period
        
        return self.system_process
    
    def handle_syscall_complete(self):
        """Handle completion of a system call."""
        if self.syscall_queue:
            process = self.syscall_queue.popleft()
            process.advance_burst()  # Move to next burst
            process.state = ProcessState.READY
            self.total_syscalls_handled += 1
            return process
        return None
    
    def get_syscall_queue_length(self) -> int:
        """Get number of processes waiting for syscalls."""
        return len(self.syscall_queue)
    
    def __repr__(self) -> str:
        return f"SystemCallManager(pending_syscalls={len(self.syscall_queue)}, " \
               f"next_release={self.next_system_release})"


class SystemProcess(Process):
    """Special system process for executing system calls."""
    
    def __init__(self, release_time: int, duration: int):
        """
        Initialize system process.
        
        Args:
            release_time: When system process is released
            duration: How long to execute
        """
        # System process has special ID and single CPU burst
        super().__init__("SYS", release_time, 0, [duration])
        self.state = ProcessState.RUNNING
        self.is_system = True
    
    def __repr__(self) -> str:
        return f"SystemProcess(release_time={self.release_time}, duration={self.remaining_burst_time})"
