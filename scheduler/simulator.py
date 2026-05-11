"""
Event-driven Round-Robin scheduler with virtual memory.

Key design decisions
---------------------
* The disk is a serial resource: only one SWAP_OUT or SWAP_IN at a time.
  _disk_busy tracks this; _disk_queue holds processes waiting to be loaded.
* in_memory is only set True after complete_load() (transfer done).
  Eviction only picks processes that are fully in RAM.
* System process has higher priority: when WAITING it gets the first free CPU
  before any user process.
* Scheduling is triggered after every event that could free a processor or
  make a process ready.
"""

from models import Processor, SystemProcess
from memory import MemoryManager


class Simulator:
    def __init__(self, params, processes):
        self.time_slice      = params["time_slice"]
        self.processors      = [Processor(i) for i in range(params["processors"])]
        self.mem             = MemoryManager(params["memory"], params["disk_transfer_rate"])
        self.sys_proc        = SystemProcess(params["syscall_period"])
        self.processes       = processes
        self.event_log       = []
        self.current_time    = 0.0
        self.ready_queue     = []   # FIFO of READY user processes
        self._events         = []   # sorted (time, seq, type, data)
        self._seq            = 0
        self._disk_busy      = False
        self._next_cpu       = 0    # next CPU id to try for round-robin

    # ------------------------------------------------------------------
    # event queue
    # ------------------------------------------------------------------

    def _push(self, t, etype, data=None):
        self._events.append((t, self._seq, etype, data))
        self._seq += 1
        self._events.sort(key=lambda e: (e[0], e[1]))

    # ------------------------------------------------------------------
    # helpers
    # ------------------------------------------------------------------

    def _free_processors(self):
        return [p for p in self.processors if p.current_process is None]

    # ------------------------------------------------------------------
    # system-process (high priority)
    # ------------------------------------------------------------------

    def _try_run_syscall(self):
        """Start a pending system call if the sys-proc is waiting and a CPU is free."""
        if self.sys_proc.state != "WAITING":
            return
        if not self.sys_proc.pending_syscalls:
            return
        free = self._free_processors()
        if not free:
            return

        # pick a free processor using round-robin starting at self._next_cpu
        free_map = {p.proc_id: p for p in free}
        n = len(self.processors)
        processor = None
        for offset in range(n):
            pid = (self._next_cpu + offset) % n
            if pid in free_map:
                processor = free_map[pid]
                self._next_cpu = (pid + 1) % n
                break
        if processor is None:
            processor = free[0]
            self._next_cpu = (processor.proc_id + 1) % n
        proc, syscall_dur = self.sys_proc.pending_syscalls.pop(0)
        self.sys_proc.state = "RUNNING"
        self.sys_proc.assigned_processor = processor
        processor.current_process = "__system__"
        processor.busy_until = self.current_time + syscall_dur

        self.event_log.append({
            "time": self.current_time,
            "end_time": self.current_time + syscall_dur,
            "type": "SYS_RUN",
            "pid": proc.pid,
            "processor": processor.proc_id,
            "duration": syscall_dur,
        })
        self._push(self.current_time + syscall_dur, "SYSCALL_DONE", (proc, processor))

    # ------------------------------------------------------------------
    # memory loading
    # ------------------------------------------------------------------

    def _start_load(self, process):
        """
        Evict LRU processes as needed (serially) then load `process`.
        Sets _disk_busy = True and pushes a MEM_READY event.
        `process` must not be in_memory already.
        """
        """Attempts to load a process. Returns True if successful, False if OOM."""
        # Calculate how much we need to evict
        needed = (self.mem.used_ram + process.memory_required) - self.mem.total_ram

        if needed > 0:
            # Check if we even have enough 'evictable' memory
            # (Oldest to newest, non-busy processes)
            evictable_mem = sum(p.memory_required for p in self.mem._in_memory
                                if p.state not in ["RUNNING", "SYSCALL", "WAITING_MEM"])

            if evictable_mem < needed:
                return False  # Not enough safe space right now!

        # If we get here, we have enough space (or can make it)
        self._disk_busy = True
        elapsed = self.current_time

        while self.mem.used_ram + process.memory_required > self.mem.total_ram:
            victim = self.mem.evict_lru()
            save_time = victim.memory_required / self.mem.disk_transfer_rate
            self.event_log.append({
                "time": elapsed, "end_time": elapsed + save_time,
                "type": "SWAP_OUT", "pid": victim.pid, "duration": save_time,
            })
            elapsed += save_time

        load_time = process.memory_required / self.mem.disk_transfer_rate
        self.event_log.append({
            "time": elapsed, "end_time": elapsed + load_time,
            "type": "SWAP_IN", "pid": process.pid, "duration": load_time,
        })
        elapsed += load_time

        process.state = "WAITING_MEM"
        self._push(elapsed, "MEM_READY", process)
        return True

    # ------------------------------------------------------------------
    # user-process scheduling
    # ------------------------------------------------------------------

    def _schedule(self):
        """
        Assign READY user processes to free processors.
        Handles virtual memory loading and processor affinity.
        """
        # We continue as long as there are processes to run and CPUs to run them on
        while self.ready_queue and self._free_processors():
            # 1. Get the next process in line
            process = self.ready_queue.pop(0)

            # Safety check: if the process isn't READY (e.g. still in SYSCALL), skip it
            if process.state != "READY":
                continue

            # 2. Virtual Memory Management
            if not process.in_memory:
                # If the disk is already moving another process, we must wait
                if self._disk_busy:
                    self.ready_queue.insert(0, process)
                    break

                # Attempt to load the process from disk.
                # If _start_load returns False, it means RAM is full of busy processes.
                # We stop scheduling and wait for a CPU_DONE or SYSCALL_DONE event.
                if self._start_load(process):
                    # Load started successfully; disk is now busy.
                    # We break because only one load can happen at a time.
                    break
                else:
                    # OOM: No safe victims to evict right now.
                    self.ready_queue.insert(0, process)
                    break

            # 3. Processor selection: prefer affinity, else round-robin
            free_cpus = self._free_processors()
            free_map = {p.proc_id: p for p in free_cpus}
            processor = None

            # affinity: if this process ran on a processor previously and that
            # processor is currently free, schedule it there (spec requirement)
            if process.last_processor is not None and process.last_processor in free_map:
                processor = free_map[process.last_processor]
                # advance _next_cpu to avoid repeatedly picking same after affinity
                n = len(self.processors)
                self._next_cpu = (processor.proc_id + 1) % n
            else:
                # fallback: pick by round-robin to balance across CPUs
                n = len(self.processors)
                for offset in range(n):
                    pid = (self._next_cpu + offset) % n
                    if pid in free_map:
                        processor = free_map[pid]
                        self._next_cpu = (pid + 1) % n
                        break
                if processor is None:
                    processor = free_cpus[0]
                    self._next_cpu = (processor.proc_id + 1) % n

            # 4. Execute the Process (Round-Robin)
            run_time = min(self.time_slice, process.burst_remaining)

            # Update States
            process.state = "RUNNING"
            process.last_processor = processor.proc_id
            self.mem.touch(process) # Update LRU position

            processor.current_process = process
            processor.busy_until = self.current_time + run_time

            # 5. Logging and Event Queue
            self.event_log.append({
                "time": self.current_time,
                "end_time": self.current_time + run_time,
                "type": "RUN",
                "pid": process.pid,
                "processor": processor.proc_id,
                "duration": run_time,
            })

            # Schedule the event for when the CPU burst/slice finishes
            self._push(self.current_time + run_time, "CPU_DONE", (process, processor))

    # ------------------------------------------------------------------
    # main loop
    # ------------------------------------------------------------------

    def run(self):
        for proc in self.processes:
            self._push(proc.release_time, "PROCESS_RELEASE", proc)
        self._push(self.sys_proc.next_release, "SYS_RELEASE")

        while self._events:
            t, _, etype, data = self._events.pop(0)
            self.current_time = t

            # ---- process released ----
            if etype == "PROCESS_RELEASE":
                proc = data
                proc.state = "READY"
                self.ready_queue.append(proc)
                self.event_log.append({
                    "time": t, "end_time": t,
                    "type": "RELEASE", "pid": proc.pid,
                })

            # ---- CPU time-slice finished ----
            elif etype == "CPU_DONE":
                process, processor = data
                processor.current_process = None
                run_time = min(self.time_slice, process.burst_remaining)
                process.burst_remaining -= run_time

                if process.burst_remaining > 0:
                    # preempted: back to ready queue
                    process.state = "READY"
                    self.ready_queue.append(process)
                elif process.burst_index < len(process.bursts) - 1:
                    # burst done, system call next
                    syscall_dur = process.syscall_times[process.burst_index]
                    process.state = "SYSCALL"
                    self.sys_proc.pending_syscalls.append((process, syscall_dur))
                    self.event_log.append({
                        "time": t, "end_time": t,
                        "type": "SYSCALL_QUEUED",
                        "pid": process.pid, "duration": syscall_dur,
                    })
                else:
                    process.state = "DONE"
                    self.event_log.append({
                        "time": t, "end_time": t,
                        "type": "DONE", "pid": process.pid,
                    })

            # ---- periodic system-process release ----
            elif etype == "SYS_RELEASE":
                self.event_log.append({
                    "time": t, "end_time": t, "type": "SYS_RELEASE",
                })
                if self.sys_proc.pending_syscalls:
                    self.sys_proc.state = "WAITING"
                else:
                    self.sys_proc.state = "IDLE"
                self.sys_proc.next_release = t + self.sys_proc.period
                self._push(self.sys_proc.next_release, "SYS_RELEASE")

            # ---- system call finished ----
            elif etype == "SYSCALL_DONE":
                proc, processor = data
                processor.current_process = None
                proc.burst_index += 1
                proc.burst_remaining = proc.bursts[proc.burst_index]
                proc.state = "READY"
                self.ready_queue.append(proc)
                self.event_log.append({
                    "time": t, "end_time": t,
                    "type": "SYSCALL_DONE", "pid": proc.pid,
                })

                # If there are more calls waiting, keep processing; otherwise, wait for next period
                if self.sys_proc.pending_syscalls:
                    self.sys_proc.state = "WAITING"
                else:
                    self.sys_proc.state = "IDLE"

            # ---- memory transfer complete ----
            elif etype == "MEM_READY":
                process = data
                self._disk_busy = False
                self.mem.complete_load(process)
                process.state = "READY"
                self.ready_queue.insert(0, process)   # high priority: front of queue
                self.event_log.append({
                    "time": t, "end_time": t,
                    "type": "MEM_READY", "pid": process.pid,
                })

            # after every event: sys calls first (higher priority), then user procs
            self._try_run_syscall()
            self._schedule()

            if all(p.is_done() for p in self.processes):
                break

        self.event_log.append({
            "time": self.current_time, "end_time": self.current_time,
            "type": "SIMULATION_END", "final_time": self.current_time,
        })
        return self.event_log
