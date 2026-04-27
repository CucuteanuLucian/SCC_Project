"""
Configuration management for the simulator.
"""
import os
from typing import Dict, Any, Tuple
from json_utils import json_loads, json_dumps
from process import Process


class ConfigManager:
    """Manages simulator configuration from various formats."""
    
    DEFAULT_CONFIG = {
        'processors': 2,
        'ram': 1024,
        'timeslice': 4,
        'system_period': 10,
        'disk_rate': 100
    }
    
    @staticmethod
    def load_from_json(filepath: str) -> Tuple[Dict, list]:
        """
        Load configuration from JSON file.
        
        Args:
            filepath: Path to JSON file
            
        Returns:
            Tuple of (config_dict, processes_list)
        """
        with open(filepath, 'r') as f:
            data = json_loads(f.read())
        
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update(data.get('config', {}))
        
        processes = []
        for p_data in data.get('processes', []):
            process = Process(
                process_id=p_data['id'],
                release_time=p_data['release_time'],
                memory_required=p_data['memory'],
                bursts=p_data['bursts']
            )
            processes.append(process)
        
        return config, processes
    
    @staticmethod
    def save_to_json(config: Dict, processes: list, filepath: str):
        """Save configuration to JSON file."""
        data = {
            'config': config,
            'processes': [
                {
                    'id': p.id,
                    'release_time': p.release_time,
                    'memory': p.memory_required,
                    'bursts': p.bursts
                }
                for p in processes
            ]
        }
        
        with open(filepath, 'w') as f:
            f.write(json_dumps(data, indent=2))
        
        print(f"Configuration saved to: {filepath}")
    
    @staticmethod
    def load_from_text(filepath: str) -> Tuple[Dict, list]:
        """Load configuration from text file (traditional format)."""
        from main import InputParser
        return InputParser.parse_file(filepath)
    
    @staticmethod
    def create_json_template(filepath: str):
        """Create a JSON configuration template."""
        template = {
            "config": {
                "processors": 2,
                "ram": 512,
                "timeslice": 4,
                "system_period": 10,
                "disk_rate": 100
            },
            "processes": [
                {
                    "id": "P1",
                    "release_time": 0,
                    "memory": 256,
                    "bursts": [5, 2, 3, 4, 9, 4, 6]
                },
                {
                    "id": "P2",
                    "release_time": 2,
                    "memory": 128,
                    "bursts": [4, 3, 6, 2, 5]
                }
            ]
        }
        
        with open(filepath, 'w') as f:
            f.write(json_dumps(template, indent=2))
        
        print(f"JSON template created: {filepath}")


class SimulationProfile:
    """Predefined simulation profiles for common scenarios."""
    
    @staticmethod
    def light_workload() -> Tuple[Dict, list]:
        """Light workload: few small processes."""
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update({
            'processors': 1,
            'ram': 256,
            'timeslice': 4
        })
        
        processes = [
            Process("P1", 0, 64, [3, 1, 2, 1, 3]),
            Process("P2", 1, 64, [2, 1, 3, 1, 2]),
            Process("P3", 2, 64, [3, 1, 2, 1, 3])
        ]
        
        return config, processes
    
    @staticmethod
    def medium_workload() -> Tuple[Dict, list]:
        """Medium workload: balanced mix."""
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update({
            'processors': 2,
            'ram': 512,
            'timeslice': 4
        })
        
        processes = [
            Process("P1", 0, 256, [5, 2, 3, 4, 9, 4, 6]),
            Process("P2", 2, 128, [4, 3, 6, 2, 5]),
            Process("P3", 1, 192, [7, 2, 8, 3, 4]),
            Process("P4", 3, 64, [3, 1, 4, 2, 5, 1, 3])
        ]
        
        return config, processes
    
    @staticmethod
    def heavy_workload() -> Tuple[Dict, list]:
        """Heavy workload: many large processes."""
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update({
            'processors': 4,
            'ram': 1024,
            'timeslice': 2,
            'system_period': 5
        })
        
        processes = [
            Process("P1", 0, 128, [10, 2, 10, 2, 8]),
            Process("P2", 0, 128, [12, 3, 11, 2, 9, 1, 5]),
            Process("P3", 1, 256, [15, 2, 14, 1, 10]),
            Process("P4", 2, 64, [6, 4, 5, 3, 4, 2, 6]),
            Process("P5", 3, 96, [8, 5, 7, 4, 6, 3, 5]),
            Process("P6", 1, 32, [3, 1, 2, 1, 3, 1, 2]),
            Process("P7", 4, 48, [4, 2, 3, 2, 4, 1, 3])
        ]
        
        return config, processes
    
    @staticmethod
    def io_heavy() -> Tuple[Dict, list]:
        """I/O heavy: processes with many syscalls."""
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update({
            'processors': 2,
            'ram': 512,
            'timeslice': 2,
            'system_period': 5
        })
        
        processes = [
            Process("P1", 0, 128, [2, 3, 2, 3, 2, 3, 2, 3, 2]),
            Process("P2", 1, 128, [3, 2, 3, 2, 3, 2, 3]),
            Process("P3", 2, 96, [2, 4, 2, 4, 2, 4, 2])
        ]
        
        return config, processes
    
    @staticmethod
    def cpu_intensive() -> Tuple[Dict, list]:
        """CPU intensive: few syscalls per process."""
        config = ConfigManager.DEFAULT_CONFIG.copy()
        config.update({
            'processors': 4,
            'ram': 512,
            'timeslice': 8
        })
        
        processes = [
            Process("P1", 0, 256, [20, 1, 20, 1, 20]),
            Process("P2", 1, 256, [18, 1, 18, 1, 18]),
            Process("P3", 2, 256, [22, 1, 22, 1, 22])
        ]
        
        return config, processes


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        profile = sys.argv[1].lower()
    else:
        profile = "medium"
    
    profiles = {
        'light': SimulationProfile.light_workload,
        'medium': SimulationProfile.medium_workload,
        'heavy': SimulationProfile.heavy_workload,
        'io': SimulationProfile.io_heavy,
        'cpu': SimulationProfile.cpu_intensive
    }
    
    if profile not in profiles:
        print(f"Unknown profile: {profile}")
        print(f"Available: {', '.join(profiles.keys())}")
        sys.exit(1)
    
    config, processes = profiles[profile]()
    
    # Save as JSON
    filename = f"profile_{profile}.json"
    ConfigManager.save_to_json(config, processes, filename)
    
    print(f"\nProfile '{profile}':")
    print(f"  Processors: {config['processors']}")
    print(f"  RAM: {config['ram']}")
    print(f"  Processes: {len(processes)}")
