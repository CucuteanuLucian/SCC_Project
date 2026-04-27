# Quick Reference Guide

## File Structure

```
ProiectCSS/
├── main.py                  # Entry point
├── process.py              # Process state & management
├── processor.py            # CPU simulation
├── scheduler.py            # Round-Robin algorithm
├── memory_manager.py       # RAM/disk with LRU
├── system_call_manager.py  # Syscall handling
├── simulator.py            # Event-driven engine
├── logger.py               # Output generation
├── config_manager.py       # Configuration profiles
├── result_analyzer.py      # Result analysis tools
├── test_simulator.py       # Unit tests
├── input.txt              # Default input (auto-generated)
├── input_advanced.txt     # Advanced example
├── requirements.txt       # Dependencies
├── README.md              # Full documentation
├── TUTORIAL.md            # Step-by-step guide
└── output/                # Generated outputs
```

## Command Cheat Sheet

### Running Simulations

```bash
# Default simulation
python main.py

# Custom input
python main.py input.txt

# Advanced example
python main.py input_advanced.txt
```

### Testing & Analysis

```bash
# Run unit tests
python test_simulator.py

# Analyze latest results
python result_analyzer.py

# Analyze specific log
python result_analyzer.py output/simulation_log_*.txt
```

### Configuration Management

```bash
# Create light workload profile
python config_manager.py light

# Create medium workload profile
python config_manager.py medium

# Create heavy workload profile
python config_manager.py heavy

# Create I/O intensive profile
python config_manager.py io

# Create CPU intensive profile
python config_manager.py cpu
```

## Input File Format

### Configuration Section

```
processors=2          # Number of CPUs (default: 2)
ram=512              # RAM size in units (default: 1024)
timeslice=4          # Time quantum (default: 4)
system_period=10     # Syscall handler period (default: 10)
disk_rate=100        # Disk speed (units/time) (default: 100)
```

### Process Section

```
ID ReleaseTime Memory (Burst1 Burst2 Burst3...)

Examples:
P1 0 256 (5 2 3 4)
P2 2 128 (4 3 6)
P3 1 192 (7 2 8)
```

**Format Notes:**

- Even indices = CPU bursts
- Odd indices = System call durations
- Total of all bursts = total execution time

## Process States

```
NEW
  ↓ (released)
READY
  ↓ (assigned to CPU)
RUNNING
  ├→ TERMINATED (no more bursts)
  ├→ WAITING (syscall requested)
  │   ↓ (system process handles)
  │   → READY (return to queue)
  └→ READY (time slice expires)
     ↑ (re-assigned to CPU)
     └─────────────────┘
```

## Memory Management

```
Process arrives
  ↓
Load into RAM?
  ├─ YES: Process in RAM
  └─ NO: Enough space?
      ├─ YES: Allocate & load
      └─ NO: Evict LRU process to disk
            Load requested process

Transfer time = Memory / DiskRate (rounded up)
```

## Output Files

Generated in `output/` directory:

| File                   | Contents             |
| ---------------------- | -------------------- |
| `simulation_log_*.txt` | Detailed event trace |
| `summary_*.txt`        | Statistics summary   |
| `gantt_chart_*.txt`    | ASCII Gantt chart    |
| `gantt_chart_*.png`    | Visual Gantt chart   |
| `*_analysis.json`      | Detailed metrics     |

## Key Algorithms

### Round-Robin Scheduling

```
while ReadyQueue not empty:
    process = ReadyQueue.dequeue()
    Assign to free CPU with time_slice
    Wait for:
        - Burst completion → CPU returns, process continues or waits
        - Time slice expiration → Preempt, return to end of queue
```

### LRU Replacement

```
if RAM full and need space:
    lru_process = find_least_recently_used()
    Move lru_process to disk
    Free its memory
    Load requested process
```

### Discrete Event Simulation

```
event_queue = PriorityQueue()
while event_queue not empty:
    event = event_queue.pop()  // Earliest time
    current_time = event.time
    handle_event(event)
    schedule_resulting_events()
```

## Performance Tuning

### For Better Interactivity

- Decrease `timeslice` (more context switches)
- Increase `processors` (less waiting)
- Increase `ram` (less disk swapping)

### For Better Throughput

- Increase `timeslice` (fewer context switches)
- Increase `disk_rate` (faster swapping)
- Decrease `system_period` (syscalls handled faster)

### For Low Memory Usage

- Decrease `ram` to simulate constraint
- Watch for LRU evictions in logs
- Observe impact on performance

## Debugging Checklist

- [ ] Can you run `python main.py`?
- [ ] Do output files appear in `output/`?
- [ ] Can you run `python test_simulator.py`?
- [ ] All 17 tests pass?
- [ ] Can you run `python result_analyzer.py`?
- [ ] Do Gantt charts display correctly?

## Common Issues

| Issue                 | Solution                                     |
| --------------------- | -------------------------------------------- |
| No `input.txt`        | Run `python main.py` once to create it       |
| No output files       | Check `output/` directory exists             |
| Tests fail            | Check Python 3.7+ installed                  |
| No Gantt PNG          | Install matplotlib: `pip install matplotlib` |
| Simulation takes long | Reduce burst times or increase `end_time`    |

## Performance Benchmarks

### System: Typical Machine (i5, 8GB RAM)

| Scenario             | Time | Processes | Output Size |
| -------------------- | ---- | --------- | ----------- |
| Light (4 processes)  | <1s  | 4         | 10 KB       |
| Medium (7 processes) | ~1s  | 7         | 25 KB       |
| Heavy (10 processes) | ~2s  | 10        | 50 KB       |

## Environment Setup

### Minimal Setup

```bash
# Python 3.7+ required
python main.py
```

### Full Setup with Visualization

```bash
pip install -r requirements.txt
python main.py input.txt
python result_analyzer.py
```

## Python Version Compatibility

- ✅ Python 3.7+
- ✅ Python 3.8
- ✅ Python 3.9
- ✅ Python 3.10
- ✅ Python 3.11

## Common Parameters Reference

### Conservative (Batch Processing)

```
timeslice=8, system_period=20, disk_rate=50
```

### Balanced (General Purpose)

```
timeslice=4, system_period=10, disk_rate=100
```

### Responsive (Interactive Systems)

```
timeslice=2, system_period=5, disk_rate=200
```

## Testing Checklist

- Unit tests: `python test_simulator.py`
- Sample input: `python main.py input.txt`
- Analysis: `python result_analyzer.py`
- JSON export: Check `*_analysis.json` file
- Gantt chart: Visual inspection of output

---

**For detailed information, see [README.md](README.md) and [TUTORIAL.md](TUTORIAL.md)**
