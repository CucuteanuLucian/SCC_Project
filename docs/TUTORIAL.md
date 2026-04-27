# OS Process Scheduling Simulator - Tutorial

## Quick Start

### 1. Run with Default Configuration

```bash
python main.py
```

This will:

- Create `input.txt` (if it doesn't exist) with sample processes
- Run the simulation
- Generate output files in the `output/` directory

### 2. Run with Custom Configuration

```bash
python main.py input.txt
```

### 3. Analyze Results

```bash
python result_analyzer.py
```

This displays:

- Event counts
- Response times per process
- Preemption statistics

---

## Understanding the Configuration

### System Parameters

- **processors**: Number of CPUs
  - Example: 2 CPUs can run 2 processes simultaneously
- **ram**: Total RAM in units
  - If process memory exceeds RAM, process is swapped to disk
  - Example: RAM=512 with processes needing 256 units each
- **timeslice**: Time quantum for Round-Robin
  - Each process gets this much CPU time before preemption
  - Smaller value = more context switches, better interactivity
  - Larger value = fewer switches, better throughput
- **system_period**: How often system process is released
  - System process handles pending system calls
  - Higher priority than user processes
- **disk_rate**: Disk transfer speed
  - Higher value = faster disk I/O
  - Transfer time = memory_needed / disk_rate

### Process Definition

Format: `ID ReleaseTime Memory (Bursts...)`

Example: `P1 0 256 (5 2 3 4 9)`

Breaking down:

- **ID**: Process name (P1, P2, etc.)
- **ReleaseTime**: When process enters system (time 0 = immediate)
- **Memory**: Memory requirement in units
- **Bursts**: Alternating CPU and syscall durations
  - Index 0 (value 5): CPU burst for 5 units
  - Index 1 (value 2): System call for 2 units
  - Index 2 (value 3): CPU burst for 3 units
  - Index 3 (value 4): System call for 4 units
  - Index 4 (value 9): CPU burst for 9 units

---

## Understanding the Output

### Text Log Example

```
Time 0: === Simulation Started ===
Time 0: Process P1 released
Time 0: Loading P1 into RAM (transfer_time=3)
Time 3: P1 load complete
Time 3: P1 assigned to CPU0
Time 7: Time slice expired for P1 on CPU0
Time 7: P1 assigned to CPU0
Time 11: P1 assigned to CPU0
```

Key events:

- **Process released**: Process enters system
- **Loading**: Process is being transferred to RAM
- **Assigned to CPU**: Process starts running
- **Time slice expired**: Process preempted due to time limit
- **Burst complete**: CPU or syscall finished

### Gantt Chart

ASCII representation showing which process runs on each CPU at each time:

```
CPU0 │ P1│P1│P3│P3│P2│...
CPU1 │ P2│P2│P1│P1│P3│...
```

Visual representation (PNG) shows colored bars for each process.

---

## Common Scenarios

### Scenario 1: Light Load

```
processors=1
ram=256
timeslice=4

P1 0 64 (3 1 2)
P2 1 64 (2 1 3)
```

Expected behavior:

- Processes load quickly
- Sequential execution on single CPU
- No memory swapping
- Low number of preemptions

### Scenario 2: Memory Pressure

```
processors=2
ram=256
timeslice=4

P1 0 256 (5 2 3)
P2 1 256 (4 1 3)
```

Expected behavior:

- Both processes need 256 units but RAM is only 256
- One process stays in RAM, other on disk
- LRU swapping occurs
- Disk transfer delays visible in log

### Scenario 3: I/O Heavy

```
processors=2
ram=512
timeslice=2
system_period=5

P1 0 128 (2 3 2 3 2)
P2 1 128 (2 3 2 3 2)
```

Expected behavior:

- Frequent system calls (many syscall requests)
- System process released regularly
- High context switch rate
- More preemptions due to small time slice

### Scenario 4: CPU Intensive

```
processors=4
ram=512
timeslice=8

P1 0 256 (20 1 20)
P2 1 256 (18 1 18)
```

Expected behavior:

- Long CPU bursts
- Few system calls
- Processes less likely to block on I/O
- Better CPU utilization
- Fewer preemptions (longer time slice)

---

## Using Configuration Profiles

Pre-built profiles for common workloads:

```bash
python config_manager.py light      # Few small processes
python config_manager.py medium     # Balanced mix
python config_manager.py heavy      # Many large processes
python config_manager.py io         # I/O intensive
python config_manager.py cpu        # CPU intensive
```

Each generates a JSON file (`profile_*.json`) that can be customized.

---

## Advanced Usage

### 1. Loading JSON Configuration

```python
from config_manager import ConfigManager
config, processes = ConfigManager.load_from_json("my_config.json")
```

### 2. Analyzing Results Programmatically

```python
from result_analyzer import ResultAnalyzer

analyzer = ResultAnalyzer("output/simulation_log_*.txt")
analyzer.print_summary()

# Get specific metrics
response_times = analyzer.calculate_response_times()
preemptions = analyzer.count_preemptions()
```

### 3. Custom Simulation Script

```python
from simulator import Simulator
from process import Process

# Create simulator
sim = Simulator(
    num_processors=2,
    ram_size=512,
    time_slice=4,
    system_period=10,
    disk_transfer_rate=100
)

# Add processes
p1 = Process("P1", 0, 256, [5, 2, 3])
sim.add_process(p1)

# Run
sim.run(end_time=50)

# Analyze
stats = sim.get_statistics()
print(stats)
```

---

## Performance Metrics

### Response Time

- **Definition**: Time from process release to first CPU execution
- **Calculation**: first_cpu_time - release_time
- **Meaning**: How quickly system responds to process arrival
- **Lower is better**: Indicates good interactivity

### Turnaround Time

- **Definition**: Total time from release to completion
- **Calculation**: completion_time - release_time
- **Meaning**: Total time process spends in system
- **Lower is better**: Indicates efficient throughput

### CPU Utilization

- **Definition**: Percentage of time CPUs are executing user processes
- **High value**: CPUs running productively
- **Low value**: CPUs idle (I/O wait, other reasons)

### Context Switches

- **Definition**: Number of times process preemption occurs
- **More switches**: More overhead, better interactivity
- **Fewer switches**: Less overhead, better throughput

---

## Debugging Tips

### Process Not Progressing

Check:

1. Is process memory > RAM? May be stuck on disk
2. Look for syscalls - may be waiting for system process
3. Check event log for "Time slice expired" - preemption happening

### Unexpected Memory Usage

Check:

1. Process memory requirements in input file
2. LRU evictions in event log
3. Disk swaps and loads

### Long Simulation Time

Check:

1. Is end_time too large?
2. Many processes or long bursts?
3. Try reducing time in `main.py: run(end_time=...)`

---

## Extending the Simulator

### Adding a New Scheduling Algorithm

1. Subclass `Scheduler` in `scheduler.py`
2. Override `schedule()` method
3. Update `simulator.py` to use new scheduler

### Adding Memory Replacement Policy

1. Modify `MemoryManager._evict_lru_process()` in `memory_manager.py`
2. Implement your replacement algorithm

### Custom Output Format

1. Extend `Logger` class in `logger.py`
2. Add methods like `generate_custom_output()`
3. Call from `main.py`

---

## Example: Step-by-Step Walkthrough

### Input File: `example.txt`

```
processors=2
ram=512
timeslice=4
system_period=10
disk_rate=100

P1 0 256 (4 1 4)
P2 2 128 (3 2 3)
```

### Execution Trace

1. **Time 0**: P1 released, starts loading (256 units / 100 rate = 3 time units)
2. **Time 2**: P2 released, starts loading (128 units / 100 rate = 2 time units)
3. **Time 3**: P1 load complete, assigned to CPU0
4. **Time 3**: P2 still loading
5. **Time 4**: P2 load complete, assigned to CPU1
6. **Time 7**: P1's first time slice expires (ran for 4 units), back to queue
7. **Time 7**: P1 assigned to CPU1 (back), P2 continues on CPU0
8. **Time 7**: P1's burst completes (actually at 4), wait...

The trace shows how the scheduler interleaves process execution across CPUs with preemption.

---

## Key Concepts Review

### Round-Robin Scheduling

- Fair allocation of CPU time
- Each process gets equal time slice
- Process preempted if slice expires
- Returned to end of queue

### Memory Management

- Limited RAM requires virtual memory
- Processes can be on disk or in RAM
- LRU eviction: remove least recently used
- Disk transfer takes time

### System Calls

- Processes can request OS services
- System process handles syscalls (higher priority)
- Released periodically (system_period)

### CPU Affinity

- Process prefers returning to last CPU
- Improves cache locality (simulated)
- Falls back to any free CPU

---

## Further Reading

- [Scheduler.py](scheduler.py): Round-Robin implementation
- [MemoryManager.py](memory_manager.py): LRU replacement
- [Simulator.py](simulator.py): Event-driven engine
- [README.md](README.md): Architecture details
