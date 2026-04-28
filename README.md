# Process Scheduling Simulator — Phase 1 Documentation

> **Language:** Python 3  
> **External libraries used:** none (GUI uses `tkinter`, Python standard library — permitted by spec)

---

## 1. System Overview

The simulator models an operating system scheduler with multiple processors, limited RAM, and a disk for virtual memory. It reads a single configuration file, executes all user processes to completion, and produces a timestamped event log and a Gantt chart (ASCII file and interactive graphical window).

---

## 2. Simulation Parameters

All parameters are provided in the input file:

| Parameter | Keyword | Description |
|---|---|---|
| Number of processors | `PROCESSORS` | How many CPUs are available |
| Total RAM | `MEMORY` | Memory units available |
| Time slice (quantum) | `TIME_SLICE` | Maximum CPU time per scheduling turn |
| System-call period | `SYSCALL_PERIOD` | How often the system process is released |
| Disk transfer rate | `DISK_TRANSFER_RATE` | Memory units transferred per time unit |

---

## 3. Scheduling Algorithm

### 3.1 User Processes — Preemptive Round-Robin

- All user processes have equal priority.
- Each scheduled process runs for at most one `TIME_SLICE`.
- If a burst is not finished at the end of the slice, the process is **preempted** and placed at the back of the ready queue.
- Scheduling is triggered whenever a processor becomes free or a new process becomes ready while a processor is free.

### 3.2 Processor Affinity

When multiple processors are free, the process is assigned to the **processor it last ran on**. If that processor is not free, any available processor is chosen.

### 3.3 System Process — High Priority

- A single system process handles all system calls from user processes.
- It is **released periodically** every `SYSCALL_PERIOD` time units (first release at `t = SYSCALL_PERIOD`).
- Once released, it waits for a free processor, then executes one pending system call at a time.
- It has **higher priority** than all user processes: after every event, the system process is offered a CPU before any user process.

---

## 4. Virtual Memory

- A process can only run if it is **loaded in RAM**.
- If RAM cannot hold all processes, **virtual memory** is used: processes not needed are saved to disk.
- **Replacement policy: LRU (Least Recently Used)** — when RAM is full, the process unused for the longest time is evicted first.
- **Disk is a serial resource** — only one transfer (save or load) happens at a time. Multiple evictions before a load happen sequentially.
- A process waiting for a disk load is in state `WAITING_MEM` and cannot run until the transfer completes.
- Transfer time = `memory_required / DISK_TRANSFER_RATE`.

---

## 5. Process Model

Each user process is defined by:
- A **release time** (when it first becomes available).
- A **memory requirement** (RAM units needed to run).
- An alternating sequence of **CPU bursts** and **system calls**.

### Burst sequence encoding

A sequence `(n  b0 s0 b1 s1 ... b_{n-1})` means `n` CPU bursts of durations `b0..b_{n-1}` separated by `n-1` system calls of durations `s0..s_{n-2}`.

**Example from the requirements spec:**  
`(5 2 3 4 9 4 6)` → 4 bursts (5, 3, 9, 6) and 3 system calls (2, 4, 4).  
Input file encoding: `BURSTS 4  5 2  3 4  9 4  6`

### Process states

```
NEW ──► READY ──► RUNNING ──► SYSCALL ──► READY ──► ... ──► DONE
                     │                       ▲
                     ▼                       │
                WAITING_MEM ────────────────►┘
          (if not in RAM when scheduled)
```

| State | Meaning |
|---|---|
| `NEW` | Not yet released |
| `READY` | Waiting for a free processor |
| `RUNNING` | Executing on a processor |
| `SYSCALL` | Waiting for the system process to handle a system call |
| `WAITING_MEM` | Waiting for a disk-to-RAM transfer to complete |
| `DONE` | All bursts finished |

---

## 6. Architecture

```
scheduler/
├── main.py          Entry point
├── models.py        Data classes: Process, Processor, SystemProcess
├── parser.py        Input file reader and validator
├── memory.py        LRU memory manager
├── simulator.py     Event-driven simulation core
├── output.py        Text report and ASCII Gantt chart writer
└── gui.py           Graphical Gantt chart (tkinter)
```

### `models.py`

Plain data classes with no simulation logic.

- **`Process`** — static data (bursts, syscall times, release time, memory requirement) and runtime state (`burst_index`, `burst_remaining`, `state`, `in_memory`, `last_processor`).
- **`Processor`** — tracks which process is assigned and `busy_until`.
- **`SystemProcess`** — tracks `next_release`, `period`, state (`IDLE`/`WAITING`/`RUNNING`), and a queue of pending `(process, syscall_duration)` pairs.

### `parser.py`

Reads the input file line by line, matching tokens by keyword. Comments (`#`) and blank lines are ignored. Uses `assert` for parameter presence and range validation. Returns a `params` dict and a list of `Process` objects.

### `memory.py` — `MemoryManager`

Maintains `_in_memory`: an ordered list of fully-loaded processes — front = LRU, back = MRU.

| Method | Description |
|---|---|
| `touch(process)` | Moves process to MRU end (called each time a process starts running) |
| `evict_lru()` | Removes and returns the front process; decrements `used_ram`; sets `in_memory = False` |
| `complete_load(process)` | Called when a disk transfer finishes; increments `used_ram`; sets `in_memory = True`; appends to MRU end |

### `simulator.py` — `Simulator`

Uses **discrete event simulation**: a sorted list `_events` holds future events as `(time, seq, type, data)`. The main loop pops the earliest event, advances `current_time`, handles it, then runs `_try_run_syscall()` followed by `_schedule()`.

**Event types:**

| Event | Trigger | Action |
|---|---|---|
| `PROCESS_RELEASE` | Release time reached | Process → READY, appended to ready queue |
| `CPU_DONE` | Time slice expires | Decrement burst; preempt → READY, or queue syscall, or mark DONE |
| `SYS_RELEASE` | Periodic timer | System process → WAITING; next release scheduled |
| `SYSCALL_DONE` | System process finishes a call | Process advances to next burst → READY |
| `MEM_READY` | Disk transfer completes | `complete_load()` called; process → READY (front of queue); disk freed |

**`_disk_busy` flag** — set when a load begins, cleared when `MEM_READY` fires. `_schedule()` will not start a new load while the disk is busy, enforcing serial transfers.

**`_start_load(process)`** — calculates all sequential eviction and load events up-front with correct timestamps, appends them to the event log, and pushes a single `MEM_READY` event.

### `output.py`

- `write_text_report()` — writes every event as a formatted row: `TIME`, `END_TIME`, `TYPE`, details.
- `write_gantt()` — builds a `processors × time` character grid; fills `digit` (process id), `S` (system call), `M` (memory transfer); writes as ASCII art with a legend.

### `gui.py`

Draws a `tkinter.Canvas` with one row per processor. Each event interval is a colour-coded rectangle. Each user process has a distinct colour; the system process is red; memory transfers are light blue. A time axis with tick marks is drawn at the top.

---

## 7. Input File Format

```
# Lines starting with # are comments; blank lines are ignored
PROCESSORS        <int>
MEMORY            <number>
TIME_SLICE        <number>
SYSCALL_PERIOD    <number>
DISK_TRANSFER_RATE <number>

PROCESS <pid> <release_time> <memory_required>
BURSTS  <count> b0 [s0 b1 s1 ... b_{count-1}]
```

Multiple `PROCESS` / `BURSTS` pairs follow after the parameter section.

---

## 8. Output Files

### `report.txt`

```
      TIME    END_TIME  TYPE                  DETAILS
----------------------------------------------------------------------
      0.00        0.00  RELEASE               {'pid': 1}
      0.00        4.00  SWAP_IN               {'pid': 1, 'duration': 4.0}
      4.00        7.00  RUN                   {'pid': 1, 'processor': 0, 'duration': 3.0}
      ...
```

### `gantt.txt`

```
CPU  0         10        20        ...
     -----------------------------------------
P0   |MMMMM111MMMM2MMMMM3MM1SS1MMMMM...|
P1   |......................................|

Legend: digit=process id  S=system call  M=memory transfer  .=idle
```

### Graphical window

Colour-coded Gantt chart rendered with `tkinter`. Opens when run without `--no-gui`.

---

## 9. Design Decisions

- **No external libraries** — all logic is hand-written; `tkinter` is the sole exception, explicitly permitted by the requirements.
- **Discrete event simulation** — jumps directly between meaningful events; handles fractional durations correctly; efficient (no idle time stepping).
- **Serial disk** — `_disk_busy` flag models a single-channel disk controller; only one transfer at a time.
- **`in_memory` set only on transfer completion** — prevents eviction accounting errors during loading.
- **`assert` statements** — used for parameter validation in `parser.py` and for internal invariants in `simulator.py` and `memory.py`.
- **Simplicity** — no features beyond the specification, keeping the codebase small and ready for testing in Phase 2.
