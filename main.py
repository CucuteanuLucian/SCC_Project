"""
Main entry point: input parser and simulation orchestrator.
"""
import sys
import os
from typing import List, Tuple
from process import Process
from simulator import Simulator
from logger import Logger


class InputParser:
    """Parses simulation input files."""
    
    @staticmethod
    def parse_file(filepath: str) -> Tuple[dict, List[Process]]:
        """
        Parse input file.
        
        Format:
            processors=2
            ram=1024
            timeslice=4
            system_period=10
            disk_rate=100
            
            P1 0 256 (5 2 3 4 9)
            P2 2 128 (4 3 6)
        
        Args:
            filepath: Path to input file
            
        Returns:
            Tuple of (config_dict, processes_list)
        """
        config = {
            'processors': 2,
            'ram': 1024,
            'timeslice': 4,
            'system_period': 10,
            'disk_rate': 100
        }
        processes = []
        
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        # Parse configuration
        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key in config:
                    try:
                        config[key] = int(value)
                    except ValueError:
                        config[key] = value
            else:
                # Process definition
                process = InputParser._parse_process_line(line)
                if process:
                    processes.append(process)
        
        return config, processes
    
    @staticmethod
    def _parse_process_line(line: str) -> Process:
        """
        Parse a process definition line.
        
        Format: P1 0 256 (5 2 3 4 9)
            - P1: process ID
            - 0: release time
            - 256: memory requirement
            - (5 2 3 4 9): burst sequence
        
        Args:
            line: Process definition line
            
        Returns:
            Process object or None
        """
        parts = line.split()
        if len(parts) < 4:
            return None
        
        try:
            process_id = parts[0]
            release_time = int(parts[1])
            memory_required = int(parts[2])
            
            # Parse burst sequence from (...)
            burst_str = ' '.join(parts[3:])
            burst_str = burst_str.strip()
            
            if burst_str.startswith('(') and burst_str.endswith(')'):
                burst_str = burst_str[1:-1]
            
            bursts = [int(x) for x in burst_str.split()]
            
            return Process(process_id, release_time, memory_required, bursts)
        except ValueError:
            return None
    
    @staticmethod
    def create_sample_input(filepath: str):
        """Create sample input file for testing."""
        sample = """# OS Process Scheduling Simulator - Input File

# System Configuration
processors=2
ram=512
timeslice=4
system_period=10
disk_rate=100

# Process Definitions
# Format: ProcessID ReleaseTime MemoryRequired (Burst1 Burst2 ...)
# Even indices are CPU bursts, odd indices are System call bursts

P1 0 256 (5 2 3 4 9 4 6)
P2 2 128 (4 3 6 2 5)
P3 1 192 (7 2 8 3 4)
P4 3 64 (3 1 4 2 5 1 3)
"""
        with open(filepath, 'w') as f:
            f.write(sample)
        print(f"Sample input file created: {filepath}")


def main():
    """Main entry point."""
    # Handle command line arguments
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
    else:
        input_file = "input.txt"
        # Create sample if doesn't exist
        if not os.path.exists(input_file):
            InputParser.create_sample_input(input_file)
            print("No input file provided. Created sample: input.txt")
    
    print(f"Loading input from: {input_file}")
    
    # Parse input
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        return
    
    config, processes = InputParser.parse_file(input_file)
    
    print(f"\n=== Configuration ===")
    print(f"Processors: {config['processors']}")
    print(f"RAM: {config['ram']} units")
    print(f"Time Slice: {config['timeslice']} units")
    print(f"System Period: {config['system_period']} units")
    print(f"Disk Transfer Rate: {config['disk_rate']} units/time\n")
    
    print(f"=== Processes ({len(processes)}) ===")
    for p in processes:
        print(f"  {p.id}: release={p.release_time}, memory={p.memory_required}, "
              f"bursts={p.bursts}")
    print()
    
    # Create simulator
    simulator = Simulator(
        num_processors=config['processors'],
        ram_size=config['ram'],
        time_slice=config['timeslice'],
        system_period=config['system_period'],
        disk_transfer_rate=config['disk_rate']
    )
    
    # Add processes
    for process in processes:
        simulator.add_process(process)
    
    # Run simulation
    print("=== Starting Simulation ===\n")
    
    max_time = max(p.release_time + sum(p.bursts) + 100 
                   for p in processes) if processes else 1000
    simulator.run(end_time=int(max_time))
    
    # Get statistics
    stats = simulator.get_statistics()
    
    print("\n=== Simulation Statistics ===")
    print(f"Final Time: {stats['current_time']}")
    print(f"Completed Processes: {stats['terminated_processes']}/{stats['total_processes']}")
    print(f"System Calls Handled: {stats['syscalls_handled']}")
    
    # Save outputs
    print("\n=== Generating Outputs ===")
    logger = Logger("output")
    
    logger.save_text_log(simulator.log_entries)
    logger.save_summary(stats)
    
    # Generate Gantt chart (ASCII)
    gantt_ascii = logger.generate_gantt_chart_text()
    print("\n" + gantt_ascii)
    
    # Try to generate graphical Gantt chart
    try:
        logger.generate_gantt_chart_visual()
    except Exception as e:
        print(f"Note: Could not generate graphical Gantt chart: {e}")
        print("Install matplotlib for graphical output: pip install matplotlib")
    
    print("\n=== Simulation Complete ===")


if __name__ == "__main__":
    main()
