"""
Logging and output generation (text log and Gantt chart visualization).
"""
import os
from typing import List, Dict, Optional
from datetime_utils import DateTime, get_current_datetime_str


class Logger:
    """Generates text logs and graphical output."""
    
    def __init__(self, output_dir: str = "output"):
        """
        Initialize logger.
        
        Args:
            output_dir: Directory to save output files
        """
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.timestamp = DateTime.now().strftime("%Y%m%d_%H%M%S")
        self.timeline_data: Dict[int, List[str]] = {}  # {processor_id: [process_ids]}
    
    def save_text_log(self, log_entries: List[str], filename: str = None) -> str:
        """
        Save text log to file.
        
        Args:
            log_entries: List of log messages
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"simulation_log_{self.timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("=== OS Process Scheduling Simulator - Execution Log ===\n")
            f.write(f"Generated: {DateTime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 60 + "\n\n")
            
            for entry in log_entries:
                f.write(entry + "\n")
        
        print(f"\nText log saved to: {filepath}")
        return filepath
    
    def record_timeline_event(self, processor_id: int, process_id: str, 
                              start_time: int, end_time: int):
        """
        Record event for Gantt chart.
        
        Args:
            processor_id: Processor executing process
            process_id: Process ID
            start_time: Start time
            end_time: End time
        """
        if processor_id not in self.timeline_data:
            self.timeline_data[processor_id] = []
        
        self.timeline_data[processor_id].append({
            "process": process_id,
            "start": start_time,
            "end": end_time,
            "duration": end_time - start_time
        })
    
    def generate_gantt_chart_text(self, max_time: int = None) -> str:
        """
        Generate ASCII Gantt chart.
        
        Args:
            max_time: Maximum time to display (optional)
            
        Returns:
            Gantt chart as string
        """
        if not self.timeline_data:
            return "No timeline data available"
        
        if max_time is None:
            max_time = 80
        
        chart_lines = []
        chart_lines.append("=== Gantt Chart (ASCII) ===\n")
        
        # Sort by processor ID
        for processor_id in sorted(self.timeline_data.keys()):
            events = self.timeline_data[processor_id]
            if not events:
                continue
            
            # Create timeline representation
            timeline = ['─' for _ in range(min(max_time, 80))]
            
            for event in events:
                start = min(event['start'], max_time - 1)
                end = min(event['end'], max_time)
                process_id = event['process'][:3]  # Abbreviate
                
                for t in range(start, end):
                    if t < len(timeline):
                        timeline[t] = '█'
            
            # Build line
            line = f"CPU{processor_id} │ "
            for t in range(min(max_time, 80)):
                if t < len(timeline):
                    line += timeline[t]
            
            chart_lines.append(line + " │")
        
        # Add time scale
        time_scale = "Time │ "
        for i in range(0, min(max_time, 80), 10):
            time_scale += f"{i:<9}"
        chart_lines.append(time_scale)
        
        return "\n".join(chart_lines)
    
    def generate_gantt_chart_visual(self, filename: str = None) -> str:
        """
        Generate detailed Gantt chart with matplotlib.
        
        Args:
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            import numpy as np
        except ImportError:
            return self._fallback_gantt(filename)
        
        if filename is None:
            filename = f"gantt_chart_{self.timestamp}.png"
        
        filepath = os.path.join(self.output_dir, filename)
        
        # Prepare data
        processors = sorted(self.timeline_data.keys())
        num_processors = len(processors)
        
        if not processors or not self.timeline_data[processors[0]]:
            return filepath  # Empty data
        
        # Create figure
        fig, ax = plt.subplots(figsize=(14, 4 + num_processors * 0.8))
        
        # Color map for processes
        colors = {}
        color_list = plt.cm.Set3(np.linspace(0, 1, 12))
        color_idx = 0
        
        max_time = 0
        y_offset = 0
        
        # Draw bars
        for processor_id in processors:
            events = self.timeline_data[processor_id]
            
            for event in events:
                process_id = event['process']
                start = event['start']
                duration = event['duration']
                
                # Assign color to process
                if process_id not in colors:
                    colors[process_id] = color_list[color_idx % len(color_list)]
                    color_idx += 1
                
                # Draw rectangle
                rect = patches.Rectangle((start, y_offset), duration, 0.8,
                                        linewidth=1, edgecolor='black',
                                        facecolor=colors[process_id], alpha=0.7)
                ax.add_patch(rect)
                
                # Add text label
                ax.text(start + duration / 2, y_offset + 0.4, process_id,
                       ha='center', va='center', fontsize=9, fontweight='bold')
                
                max_time = max(max_time, event['end'])
            
            # Add processor label
            ax.text(-2, y_offset + 0.4, f"CPU{processor_id}", 
                   ha='right', va='center', fontweight='bold')
            
            y_offset += 1
        
        # Configure axes
        ax.set_xlim(-3, max_time + 2)
        ax.set_ylim(-0.5, y_offset + 0.5)
        ax.set_xlabel("Time (units)", fontsize=11, fontweight='bold')
        ax.set_ylabel("Processor", fontsize=11, fontweight='bold')
        ax.set_title("OS Process Scheduling - Gantt Chart", fontsize=12, fontweight='bold')
        ax.set_yticks([])
        ax.grid(axis='x', alpha=0.3)
        
        # Add legend
        legend_elements = [patches.Patch(facecolor=colors[pid], alpha=0.7, label=pid)
                          for pid in sorted(colors.keys())]
        ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        plt.tight_layout()
        plt.savefig(filepath, dpi=150, bbox_inches='tight')
        plt.close()
        
        print(f"Gantt chart saved to: {filepath}")
        return filepath
    
    def _fallback_gantt(self, filename: str = None) -> str:
        """Fallback ASCII Gantt chart if matplotlib not available."""
        if filename is None:
            filename = f"gantt_chart_{self.timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(self.generate_gantt_chart_text())
        
        print(f"ASCII Gantt chart saved to: {filepath}")
        return filepath
    
    def save_summary(self, stats: Dict, filename: str = None) -> str:
        """
        Save simulation summary.
        
        Args:
            stats: Statistics dictionary
            filename: Output filename (optional)
            
        Returns:
            Path to saved file
        """
        if filename is None:
            filename = f"summary_{self.timestamp}.txt"
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write("=== Simulation Summary ===\n")
            f.write(f"Generated: {DateTime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("-" * 40 + "\n\n")
            
            f.write(f"Final Simulation Time: {stats['current_time']}\n")
            f.write(f"Total Processes: {stats['total_processes']}\n")
            f.write(f"Terminated Processes: {stats['terminated_processes']}\n")
            f.write(f"System Calls Handled: {stats['syscalls_handled']}\n\n")
            
            f.write("Memory Statistics:\n")
            mem = stats['memory']
            f.write(f"  RAM Size: {mem['ram_size']}\n")
            f.write(f"  RAM Used: {mem['ram_used']}\n")
            f.write(f"  RAM Free: {mem['ram_free']}\n")
            f.write(f"  Processes in RAM: {mem['processes_in_ram']}\n")
            f.write(f"  Processes on Disk: {mem['processes_on_disk']}\n")
        
        print(f"Summary saved to: {filepath}")
        return filepath
