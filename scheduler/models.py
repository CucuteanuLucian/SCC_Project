"""
Data models for the process scheduling simulator.
"""


class Process:
    def __init__(self, pid, release_time, memory_required, bursts, syscall_times):
        """
        pid            : unique process identifier
        release_time   : time at which the process becomes available
        memory_required: amount of RAM needed
        bursts         : list of CPU burst durations  [b0, b1, ..., bn]
        syscall_times  : list of system-call durations [s0, s1, ..., sn-1]
                         len(syscall_times) == len(bursts) - 1
        """
        assert isinstance(pid, int) and pid >= 0, "pid must be a non-negative int"  # precondition
        assert release_time >= 0, "release_time must be non-negative"  # precondition
        assert memory_required > 0, "memory_required must be positive"  # precondition
        assert isinstance(bursts, (list, tuple)), "bursts must be a list or tuple"  # precondition
        assert isinstance(syscall_times, (list, tuple)), "syscall_times must be a list or tuple"  # precondition
        assert len(syscall_times) == max(0, len(bursts) - 1), "syscall_times length mismatch"  # precondition

        self.pid = pid
        self.release_time = release_time
        self.memory_required = memory_required
        self.bursts = list(bursts)
        self.syscall_times = list(syscall_times)

        # --- runtime state ---
        self.burst_index = 0          # which burst we are currently in
        self.burst_remaining = bursts[0] if bursts else 0  # time left in current burst
        self.state = "NEW"            # NEW | READY | RUNNING | SYSCALL | WAITING_MEM | DONE
        self.last_processor = None    # processor it ran on most recently
        self.in_memory = False        # is it currently loaded in RAM?
        self.last_used_time = -1      # for LRU replacement

    def is_done(self):
        return self.state == "DONE"

    def __repr__(self):
        return f"Process(pid={self.pid}, state={self.state})"


class Processor:
    def __init__(self, proc_id):
        self.proc_id = proc_id
        self.current_process = None   # Process object or None
        self.busy_until = 0           # simulation time when it becomes free

    def is_free(self, current_time):
        assert current_time >= 0, "current_time must be non-negative"  # precondition
        return self.current_process is None or current_time >= self.busy_until

    def __repr__(self):
        return f"Processor({self.proc_id}, busy_until={self.busy_until})"


class SystemProcess:
    """
    The high-priority system process that handles system calls.
    Released periodically; executes one pending system call at a time.
    """
    def __init__(self, period):
        self.period = period
        self.next_release = period    # first release at t=period
        self.state = "IDLE"           # IDLE | WAITING | RUNNING
        self.assigned_processor = None
        self.busy_until = 0
        self.pending_syscalls = []    # list of (process, syscall_duration)

    def __repr__(self):
        return f"SystemProcess(state={self.state}, next_release={self.next_release})"
