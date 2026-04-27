# OS Process Scheduling Simulator

A comprehensive Python implementation of an operating system process scheduling simulator with support for preemptive Round-Robin scheduling, memory management with LRU replacement, and system call handling.

## Features

✓ **Preemptive Round-Robin Scheduling** - Configurable time slice quantum
✓ **Multiple Processors** - Support for multi-CPU systems  
✓ **Virtual Memory** - RAM and disk swapping with LRU replacement policy
✓ **System Process** - Higher-priority system process for handling system calls
✓ **Discrete Event Simulation** - Accurate event-driven simulation engine
✓ **Comprehensive Logging** - Text logs and Gantt charts (ASCII and graphical)
✓ **Modular Architecture** - Easy to extend and test

## Project Structure

```
ProiectCSS/
├── main.py                  # Entry point and input parsing
├── process.py               # Process representation and state management
├── processor.py             # CPU processor simulation
├── scheduler.py             # Round-Robin scheduling algorithm
├── memory_manager.py        # RAM/disk management with LRU
├── system_call_manager.py   # System call and syscall process handling
├── simulator.py             # Core simulation engine with event queue
├── logger.py                # Text and graphical output generation
├── test_simulator.py        # Unit tests
├── requirements.txt         # Python dependencies
├── input.txt               # Sample input file (auto-generated)
└── output/                 # Generated output directory
    ├── simulation_log_*.txt
    ├── summary_*.txt
    ├── gantt_chart_*.txt
    └── gantt_chart_*.png
```

## Architecture Overview

### Core Components

1. **Simulator** (`simulator.py`)
   - Discrete event simulation engine
   - Maintains simulation clock and event queue
   - Coordinates all subsystems
   - Handles event dispatch and scheduling

2. **Scheduler** (`scheduler.py`)
   - Implements preemptive Round-Robin scheduling
   - Manages ready queue
   - Implements CPU affinity (process tries to return to last processor)
   - Enforces time slices and preemption

3. **Memory Manager** (`memory_manager.py`)
   - Simulates RAM and disk storage
   - Implements LRU (Least Recently Used) replacement policy
   - Calculates disk transfer times
   - Tracks process location (RAM or disk)

4. **System Call Manager** (`system_call_manager.py`)
   - Manages system process scheduling
   - Maintains syscall queue
   - Periodic system process release
   - Priority-based preemption

5. **Process** (`process.py`)
   - Represents individual processes
   - Tracks process state and burst sequences
   - Manages alternating CPU/syscall bursts

6. **Processor** (`processor.py`)
   - Represents individual CPUs
   - Tracks running process and time slice
   - Manages busy/idle state

7. **Logger** (`logger.py`)
   - Generates text execution logs
   - Creates ASCII Gantt charts
   - Generates graphical Gantt charts (with matplotlib)
   - Produces summary statistics

## Installation

### Prerequisites

- Python 3.7 or higher

### Setup

1. Clone or extract the project:

```bash
cd ProiectCSS
```

2. Install dependencies (optional, for graphical output):

```bash
pip install -r requirements.txt
```

## Usage

### Basic Simulation

Run with default or auto-generated input:

```bash
python main.py
```

This creates `input.txt` if it doesn't exist and runs the simulation.

### Custom Input File

Create an `input.txt` file and run:

```bash
python main.py input.txt
```

### Input File Format

```
# Configuration
processors=2
ram=512
timeslice=4
system_period=10
disk_rate=100

# Processes: ID ReleaseTime Memory (Burst1 Burst2 ...)
P1 0 256 (5 2 3 4 9)
P2 2 128 (4 3 6)
P3 1 192 (7 2 8)
```

**Configuration Parameters:**

- `processors`: Number of CPUs (default: 2)
- `ram`: Total RAM size in units (default: 1024)
- `timeslice`: Time slice for Round-Robin in units (default: 4)
- `system_period`: System process release period (default: 10)
- `disk_rate`: Disk transfer rate in units/time (default: 100)

**Process Definition:**

- `ID`: Process identifier (e.g., P1, P2)
- `ReleaseTime`: When process enters system
- `Memory`: Memory requirement in units
- `Bursts`: Alternating CPU and system call times
  - Even indices = CPU bursts
  - Odd indices = System call durations

Example burst sequence `(5 2 3 4 9 4 6)`:

```
CPU: 5 units
SYS: 2 units
CPU: 3 units
SYS: 4 units
CPU: 9 units
SYS: 4 units
CPU: 6 units
```

## Running Tests

Execute unit tests:

```bash
python test_simulator.py
```

Tests cover:

- Process creation and state management
- Processor assignment and tick mechanism
- Memory loading and LRU replacement
- Scheduling algorithm
- System call management
- Event simulation

## Output Files

The simulator generates the following in the `output/` directory:

1. **simulation*log*\*.txt**
   - Detailed execution trace
   - Events timestamped and timestamped
   - Process state changes
   - Memory operations

2. **summary\_\*.txt**
   - Simulation statistics
   - Total processes and completion count
   - System calls handled
   - Memory usage statistics

3. **gantt*chart*\*.txt**
   - ASCII Gantt chart
   - Shows process execution timeline per CPU
   - Useful for console output

4. **gantt*chart*\*.png**
   - Visual Gantt chart (requires matplotlib)
   - Color-coded process visualization
   - Time axis and legend
   - Professional publication-ready

## Example Output

### Execution Log

```
Time 0: === Simulation Started ===
Time 0: Process P1 released
Time 0: Loading P1 into RAM (transfer_time=3)
Time 3: P1 load complete
Time 3: P1 assigned to CPU0
Time 8: Time slice expired for P1 on CPU0
Time 8: P1 returned to ready queue
...
```

### Gantt Chart

```
=== Gantt Chart (ASCII) ===

CPU0 │ ████████░░P2░░P1░░░░░░░░░
CPU1 │ ░░░░░░░░P1████████░░░P3░░
Time │ 0        10       20      30
```

## Algorithm Details

### Round-Robin Scheduling

1. Processes in ready queue are scheduled in FIFO order
2. Each process gets configurable time slice (quantum)
3. If burst completes before time slice expires, process moves to syscall/termination
4. If time slice expires before burst completes, process preempted and returned to end of ready queue
5. System process has higher priority and preempts user processes

### LRU Memory Replacement

1. When RAM is full and new process needs to load:
   - Identify least recently used process in RAM
   - Swap it to disk
   - Load requested process
2. Access times updated on process execution
3. Disk transfer time calculated as: `memory_size / disk_transfer_rate`

### CPU Affinity

- Processes preferentially scheduled on the CPU where they last executed
- Improves cache locality (simulated benefit)
- Falls back to any free CPU if preferred CPU busy

## Extending the Project

### Adding New Scheduling Algorithms

1. Create new scheduler class inheriting from `Scheduler`
2. Override `schedule()` method with new algorithm
3. Update simulator to use new scheduler

Example:

```python
class PriorityScheduler(Scheduler):
    def schedule(self, current_time, system_process=None):
        # Your priority scheduling logic
        pass
```

### Adding Memory Replacement Policies

1. Modify `MemoryManager._evict_lru_process()`
2. Implement new replacement algorithm (FIFO, Optimal, etc.)

### Custom Visualization

Use the `Logger` class to extend output formats:

```python
logger.timeline_data[processor_id].append({
    "process": pid,
    "start": start_time,
    "end": end_time
})
```

## Performance Notes

- Simulation scales well up to ~100 processes
- Memory usage is O(n) where n = number of processes
- Event queue operations are O(log n)
- Suitable for educational purposes and small-to-medium workloads

## Limitations

- Simplified process model (alternating CPU/syscall)
- No inter-process communication
- No priority levels (except system process)
- Single system process (doesn't parallelize syscalls)
- Disk has infinite capacity
- No I/O operations beyond syscalls

## Future Enhancements

- Multiple priority levels with priority queues
- Process synchronization and deadlock detection
- Multiple system processes with I/O parallelization
- Paging simulation with page fault handling
- Advanced scheduling algorithms (Multilevel Feedback Queues, EDF)
- Performance metrics (response time, turnaround time, CPU utilization)
- Interactive visualization with real-time animation

## References

- Operating System Concepts (Silberschatz, Galvin, Gagne)
- The Design of the UNIX Operating System (Bach)
- Computer Systems: A Programmer's Perspective

## License

This project is provided as-is for educational purposes.

## Author

OS Process Scheduling Simulator - Python Implementation
