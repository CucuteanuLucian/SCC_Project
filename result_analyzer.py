"""
Utility functions for analyzing simulation results.
"""
import os
from typing import Dict, List
from datetime_utils import get_current_datetime_iso
from json_utils import json_dumps


class ResultAnalyzer:
    """Analyze simulation results and generate statistics."""
    
    def __init__(self, log_file: str = None):
        """
        Initialize analyzer.
        
        Args:
            log_file: Path to simulation log file
        """
        self.log_file = log_file
        self.log_entries = []
        self.events = []
        
        if log_file and os.path.exists(log_file):
            self._parse_log_file(log_file)
    
    def _parse_log_file(self, filepath: str):
        """Parse simulation log file."""
        with open(filepath, 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line and not line.startswith('='):
                self.log_entries.append(line)
                self._parse_event(line)
    
    def _parse_event(self, log_line: str):
        """Extract event from log line."""
        if not log_line.startswith("Time"):
            return
        
        parts = log_line.split(":")
        if len(parts) < 2:
            return
        
        try:
            time = int(parts[0].replace("Time", "").strip())
            event_desc = ":".join(parts[1:]).strip()
            
            self.events.append({
                'time': time,
                'description': event_desc
            })
        except ValueError:
            pass
    
    def get_event_count_by_type(self) -> Dict[str, int]:
        """Get count of each event type."""
        event_types = {}
        
        for event in self.events:
            desc = event['description']
            
            if "released" in desc:
                event_type = "release"
            elif "assigned" in desc:
                event_type = "assignment"
            elif "Time slice" in desc:
                event_type = "preemption"
            elif "load" in desc:
                event_type = "load"
            elif "terminated" in desc:
                event_type = "termination"
            elif "syscall" in desc:
                event_type = "syscall"
            else:
                event_type = "other"
            
            event_types[event_type] = event_types.get(event_type, 0) + 1
        
        return event_types
    
    def get_process_statistics(self) -> Dict[str, Dict]:
        """Extract per-process statistics from logs."""
        processes = {}
        
        for event in self.events:
            desc = event['description']
            time = event['time']
            
            # Extract process ID
            for word in desc.split():
                if word.startswith("P"):
                    process_id = word
                    
                    if process_id not in processes:
                        processes[process_id] = {
                            'release_time': None,
                            'first_cpu_time': None,
                            'last_event_time': time,
                            'events': []
                        }
                    
                    processes[process_id]['events'].append({
                        'time': time,
                        'description': desc
                    })
                    
                    if "released" in desc:
                        processes[process_id]['release_time'] = time
                    elif "assigned" in desc and processes[process_id]['first_cpu_time'] is None:
                        processes[process_id]['first_cpu_time'] = time
                    
                    processes[process_id]['last_event_time'] = time
                    break
        
        return processes
    
    def calculate_response_times(self) -> Dict[str, int]:
        """Calculate response time (first execution - release) for each process."""
        response_times = {}
        process_stats = self.get_process_statistics()
        
        for process_id, stats in process_stats.items():
            if stats['release_time'] is not None and stats['first_cpu_time'] is not None:
                response_times[process_id] = stats['first_cpu_time'] - stats['release_time']
        
        return response_times
    
    def calculate_turnaround_times(self, end_time: int) -> Dict[str, int]:
        """Calculate turnaround time (end - release) for each process."""
        turnaround_times = {}
        process_stats = self.get_process_statistics()
        
        for process_id, stats in process_stats.items():
            if stats['release_time'] is not None:
                turnaround_times[process_id] = stats['last_event_time'] - stats['release_time']
        
        return turnaround_times
    
    def count_preemptions(self) -> Dict[str, int]:
        """Count preemptions per process."""
        preemptions = {}
        
        for event in self.events:
            if "Time slice" in event['description']:
                desc = event['description']
                
                # Extract process ID
                for word in desc.split():
                    if word.startswith("P"):
                        process_id = word
                        preemptions[process_id] = preemptions.get(process_id, 0) + 1
                        break
        
        return preemptions
    
    def print_summary(self):
        """Print analysis summary."""
        print("\n" + "="*50)
        print("SIMULATION ANALYSIS SUMMARY")
        print("="*50)
        
        # Event types
        print("\nEvent Counts:")
        event_counts = self.get_event_count_by_type()
        for event_type, count in sorted(event_counts.items()):
            print(f"  {event_type:.<30} {count}")
        
        # Response times
        print("\nResponse Times:")
        response_times = self.calculate_response_times()
        if response_times:
            for process_id in sorted(response_times.keys()):
                print(f"  {process_id:.<30} {response_times[process_id]} units")
            avg = sum(response_times.values()) / len(response_times)
            print(f"  Average{'':..<22} {avg:.1f} units")
        
        # Preemptions
        print("\nPreemptions per Process:")
        preemptions = self.count_preemptions()
        if preemptions:
            for process_id in sorted(preemptions.keys()):
                print(f"  {process_id:.<30} {preemptions[process_id]} times")
            total = sum(preemptions.values())
            print(f"  Total{'':..<26} {total} preemptions")
        
        print("\n" + "="*50 + "\n")
    
    def export_json(self, filepath: str):
        """Export analysis to JSON file."""
        data = {
            'timestamp': get_current_datetime_iso(),
            'event_counts': self.get_event_count_by_type(),
            'response_times': self.calculate_response_times(),
            'preemptions': self.count_preemptions(),
            'process_statistics': self.get_process_statistics()
        }
        
        with open(filepath, 'w') as f:
            f.write(json_dumps(data, indent=2))
        
        print(f"Analysis exported to: {filepath}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        log_file = sys.argv[1]
    else:
        # Find latest log file
        output_dir = "output"
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.startswith("simulation_log")]
            if files:
                log_file = os.path.join(output_dir, sorted(files)[-1])
            else:
                print("No log files found in output directory")
                sys.exit(1)
        else:
            print(f"Output directory '{output_dir}' not found")
            sys.exit(1)
    
    print(f"Analyzing: {log_file}")
    analyzer = ResultAnalyzer(log_file)
    analyzer.print_summary()
    
    # Export JSON
    json_file = log_file.replace('.txt', '_analysis.json')
    analyzer.export_json(json_file)
