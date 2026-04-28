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

        processor = free[0]
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
        assert not self._disk_busy
        self._disk_busy = True
        elapsed = self.current_time

        # evict until there is enough free RAM
        while self.mem.used_ram + process.memory_required > self.mem.total_ram:
            victim = self.mem.evict_lru()
            save_time = victim.memory_required / self.mem.disk_transfer_rate
            self.event_log.append({
                "time": elapsed,
                "end_time": elapsed + save_time,
                "type": "SWAP_OUT",
                "pid": victim.pid,
                "duration": save_time,
            })
            elapsed += save_time

        # load the process
        load_time = process.memory_required / self.mem.disk_transfer_rate
        self.event_log.append({
            "time": elapsed,
            "end_time": elapsed + load_time,
            "type": "SWAP_IN",
            "pid": process.pid,
            "duration": load_time,
        })
        elapsed += load_time

        process.state = "WAITING_MEM"
        self._push(elapsed, "MEM_READY", process)

    # ------------------------------------------------------------------
    # user-process scheduling
    # ------------------------------------------------------------------

    def _schedule(self):
        """Assign READY user processes to free processors."""
        while self.ready_queue and self._free_processors():
            # peek at the first process
            process = self.ready_queue[0]

            if process.state != "READY":
                self.ready_queue.pop(0)
                continue

            if not self._free_processors():
                break

            # if not in memory, start a disk load (only one at a time)
            if not process.in_memory:
                if self._disk_busy:
                    break   # wait until current transfer finishes
                self.ready_queue.pop(0)
                self._start_load(process)
                break       # disk is now busy; only one load at a time

            # process is in memory and a CPU is free
            self.ready_queue.pop(0)
            free = self._free_processors()
            processor = free[0]
            for p in free:
                if p.proc_id == process.last_processor:
                    processor = p
                    break

            run_time = min(self.time_slice, process.burst_remaining)
            process.state = "RUNNING"
            process.last_processor = processor.proc_id
            self.mem.touch(process)
            processor.current_process = process
            processor.busy_until = self.current_time + run_time

            self.event_log.append({
                "time": self.current_time,
                "end_time": self.current_time + run_time,
                "type": "RUN",
                "pid": process.pid,
                "processor": processor.proc_id,
                "duration": run_time,
            })
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
                if self.sys_proc.state == "IDLE":
                    self.sys_proc.state = "WAITING"
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
                self.sys_proc.state = "WAITING" if self.sys_proc.pending_syscalls else "IDLE"

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
