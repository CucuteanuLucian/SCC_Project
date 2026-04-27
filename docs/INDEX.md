# Documentation Index

## 📚 Getting Started

Start here if you're new to the project:

1. **[README.md](README.md)** - Complete project overview
   - Features and capabilities
   - Installation instructions
   - Architecture overview
   - Basic usage examples

2. **[QUICKREF.md](QUICKREF.md)** - Quick reference guide
   - Command cheat sheet
   - File structure
   - Input/output formats
   - Debugging tips

## 🎓 Learning Resources

Learn how to use the simulator:

1. **[TUTORIAL.md](TUTORIAL.md)** - Step-by-step tutorial
   - Quick start guide
   - Configuration explanation
   - Multiple scenarios
   - Performance tuning
   - Advanced usage

2. **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Implementation summary
   - What was built
   - Requirements verification
   - Features list
   - Code statistics

## 📖 Reference Documentation

Detailed information for specific topics:

- **[MANIFEST.md](MANIFEST.md)** - Complete file listing
  - What files were created
  - Code statistics
  - Feature checklist
  - Dependencies

## 💻 Code Documentation

### Core Modules

```
Core Simulation Engine:
├─ simulator.py          Event-driven simulation engine
├─ scheduler.py          Round-Robin scheduling algorithm
├─ processor.py          CPU representation
├─ process.py           Process management
├─ memory_manager.py     Virtual memory with LRU
├─ system_call_manager.py System process handling
└─ logger.py             Output generation

Application Layer:
├─ main.py              Entry point and orchestration
├─ config_manager.py    Configuration management
└─ result_analyzer.py   Result analysis tools

Testing:
└─ test_simulator.py    Unit tests (17 tests)
```

### Module Functions

Quick lookup of key components in each module:

**process.py**

- `Process` class - Process representation
- `ProcessState` enum - Process states

**processor.py**

- `Processor` class - CPU representation

**scheduler.py**

- `Scheduler` class - Round-Robin scheduling

**memory_manager.py**

- `MemoryManager` class - Memory management with LRU

**system_call_manager.py**

- `SystemCallManager` class - Syscall handling
- `SystemProcess` class - Special system process

**simulator.py**

- `Simulator` class - Main simulation engine
- `Event` class - Event representation
- `EventType` enum - Event types

**logger.py**

- `Logger` class - Output generation

**config_manager.py**

- `ConfigManager` class - Configuration management
- `SimulationProfile` class - Pre-built profiles

**result_analyzer.py**

- `ResultAnalyzer` class - Result analysis

## 🚀 Usage Guide

### Running the Simulator

```bash
# Default: python main.py
# Custom: python main.py input_file.txt
# Tests: python test_simulator.py
# Analysis: python result_analyzer.py
# Profiles: python config_manager.py [light|medium|heavy|io|cpu]
```

### Input File Format

See [README.md - Input File Format](README.md#input-file-format) or [QUICKREF.md](QUICKREF.md) for details.

### Understanding Output

See [TUTORIAL.md - Understanding the Output](TUTORIAL.md#understanding-the-output)

## 📊 Examples

### Quick Examples

1. **Light Load**

   ```bash
   python config_manager.py light
   python main.py profile_light.json
   ```

2. **Medium Load**

   ```bash
   python main.py input.txt
   ```

3. **Heavy Load**
   ```bash
   python config_manager.py heavy
   python main.py profile_heavy.json
   ```

### Learning Scenarios

See [TUTORIAL.md - Common Scenarios](TUTORIAL.md#common-scenarios)

## 🔍 Finding Information

**Looking for...**

- **How to run?** → [QUICKREF.md](QUICKREF.md) - Command Cheat Sheet
- **How it works?** → [README.md](README.md) - Architecture Overview
- **What was built?** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)
- **Configuration help?** → [TUTORIAL.md](TUTORIAL.md) - Understanding Configuration
- **Output explanation?** → [TUTORIAL.md](TUTORIAL.md) - Understanding Output
- **Performance tips?** → [TUTORIAL.md](TUTORIAL.md) - Performance Tuning
- **Debugging?** → [QUICKREF.md](QUICKREF.md) - Debugging Tips
- **Code structure?** → [README.md](README.md) - Project Structure
- **List of files?** → [MANIFEST.md](MANIFEST.md)
- **Examples?** → [input.txt](input.txt), [input_advanced.txt](input_advanced.txt)

## 📋 File Locations

```
ProiectCSS/
├── Documentation/
│   ├── README.md              ← Start here
│   ├── TUTORIAL.md            ← Learn by example
│   ├── QUICKREF.md            ← Quick lookup
│   ├── PROJECT_SUMMARY.md     ← What was built
│   ├── MANIFEST.md            ← File listing
│   └── INDEX.md               ← This file
│
├── Core Code/
│   ├── simulator.py
│   ├── scheduler.py
│   ├── memory_manager.py
│   ├── processor.py
│   ├── process.py
│   └── system_call_manager.py
│
├── Application/
│   ├── main.py
│   ├── logger.py
│   ├── config_manager.py
│   └── result_analyzer.py
│
├── Testing/
│   └── test_simulator.py
│
├── Examples/
│   ├── input.txt
│   └── input_advanced.txt
│
└── Output/
    └── (auto-generated files)
```

## 🎯 Common Tasks

### Task: Run a Basic Simulation

1. Read: [QUICKREF.md - Command Cheat Sheet](QUICKREF.md#command-cheat-sheet)
2. Execute: `python main.py`

### Task: Create Custom Configuration

1. Read: [TUTORIAL.md - Understanding Configuration](TUTORIAL.md#understanding-the-configuration)
2. Edit: Create new `input.txt` file
3. Execute: `python main.py input.txt`

### Task: Analyze Results

1. Read: [TUTORIAL.md - Performance Metrics](TUTORIAL.md#performance-metrics)
2. Execute: `python result_analyzer.py`

### Task: Understand Algorithm

1. Read: [README.md - Architecture](README.md#system-architecture)
2. Read: [QUICKREF.md - Key Algorithms](QUICKREF.md#key-algorithms)
3. Study: Source code in [scheduler.py](scheduler.py) or [memory_manager.py](memory_manager.py)

### Task: Extend Simulator

1. Read: [README.md - Future Extensions](README.md#future-extensions)
2. Read: [README.md - Extending the Project](README.md#extending-the-project)
3. Study: Relevant module source code
4. Implement: Your extension

## 📞 Quick Help

**"How do I...?"**

- Run the simulator? → `python main.py`
- Use custom input? → `python main.py input_file.txt`
- Understand the output? → See [TUTORIAL.md](TUTORIAL.md#understanding-the-output)
- Analyze results? → `python result_analyzer.py`
- Fix a problem? → See [QUICKREF.md - Debugging](QUICKREF.md#debugging-checklist)
- Configure parameters? → See [TUTORIAL.md](TUTORIAL.md#understanding-the-configuration)
- Create a profile? → `python config_manager.py [type]`
- Run tests? → `python test_simulator.py`

## 🔗 Navigation

| Document           | Best For                     | Length    |
| ------------------ | ---------------------------- | --------- |
| README.md          | Complete overview            | 310 lines |
| TUTORIAL.md        | Learning by example          | 440 lines |
| QUICKREF.md        | Quick lookup                 | 280 lines |
| PROJECT_SUMMARY.md | Understanding what was built | 270 lines |
| MANIFEST.md        | File and code statistics     | 280 lines |
| This INDEX.md      | Finding information          | 280 lines |

## 📝 Notes

- All documentation is in Markdown format
- Code examples are included in most documents
- References between documents use [links]()
- Quick reference commands are provided throughout

---

**Last Updated**: April 27, 2026
**Status**: COMPLETE ✅

Start with [README.md](README.md) for an overview, then use [QUICKREF.md](QUICKREF.md) and [TUTORIAL.md](TUTORIAL.md) as needed.
