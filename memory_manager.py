"""
Memory management: RAM and disk simulation with LRU replacement.
"""
from typing import List, Dict, Optional
from lru_cache import LRUCache


class MemoryManager:
    """Manages RAM and disk storage with LRU replacement policy."""
    
    def __init__(self, ram_size: int, disk_transfer_rate: int):
        """
        Initialize memory manager.
        
        Args:
            ram_size: Total RAM available in units
            disk_transfer_rate: Units of memory per time unit transferred
        """
        self.ram_size = ram_size
        self.disk_transfer_rate = disk_transfer_rate
        self.ram_free = ram_size
        self.processes_in_ram: Dict[str, int] = {}  # {process_id: memory_location}
        self.access_order = LRUCache()  # LRU tracking
        self.processes_on_disk: List[str] = []  # Process IDs on disk
    
    def load_process(self, process) -> int:
        """
        Load a process into RAM.
        
        Args:
            process: Process object to load
            
        Returns:
            Transfer time required
        """
        if process.id in self.processes_in_ram:
            # Already in RAM, update access time
            self.access_order.move_to_end(process.id)
            return 0
        
        # Calculate transfer time
        transfer_time = self.calculate_transfer_time(process.memory_required)
        
        # Make room if necessary
        while self.ram_free < process.memory_required and self.processes_in_ram:
            self._evict_lru_process()
        
        if self.ram_free >= process.memory_required:
            # Load into RAM
            location = self.ram_size - self.ram_free
            self.processes_in_ram[process.id] = location
            self.ram_free -= process.memory_required
            self.access_order[process.id] = True
            self.access_order.move_to_end(process.id)
            process.memory_location = location
            
            if process.id in self.processes_on_disk:
                self.processes_on_disk.remove(process.id)
            
            return transfer_time
        else:
            # Not enough memory, put on disk
            self.processes_on_disk.append(process.id)
            return transfer_time
    
    def update_access(self, process_id: str):
        """Mark a process as recently used (for LRU)."""
        if process_id in self.access_order:
            self.access_order.move_to_end(process_id)
    
    def _evict_lru_process(self):
        """Evict least recently used process to disk."""
        if not self.processes_in_ram:
            return
        
        # Get LRU process (first in order from our custom LRUCache)
        lru_process_id = self.access_order.get_least_recent()
        
        if lru_process_id and lru_process_id in self.processes_in_ram:
            # Find process object to get memory requirement
            memory_used = 0
            # We'll estimate: just remove from RAM
            del self.processes_in_ram[lru_process_id]
            # Remove from access order cache using public API
            if lru_process_id in self.access_order:
                del self.access_order[lru_process_id]
            
            # Note: In a complete implementation, we'd track memory per process
            # For now, we'll use a simple approach
            if lru_process_id not in self.processes_on_disk:
                self.processes_on_disk.append(lru_process_id)
    
    def is_in_ram(self, process_id: str) -> bool:
        """Check if process is in RAM."""
        return process_id in self.processes_in_ram
    
    def is_on_disk(self, process_id: str) -> bool:
        """Check if process is on disk."""
        return process_id in self.processes_on_disk
    
    
    
    def calculate_transfer_time(self, memory_size: int) -> int:
        """
        Calculate transfer time for loading/storing memory.
        
        Args:
            memory_size: Amount of memory to transfer
            
        Returns:
            Time units required
        """
        return (memory_size + self.disk_transfer_rate - 1) // self.disk_transfer_rate
    
    def get_statistics(self) -> Dict:
        """Get current memory statistics."""
        return {
            "ram_size": self.ram_size,
            "ram_free": self.ram_free,
            "ram_used": self.ram_size - self.ram_free,
            "processes_in_ram": len(self.processes_in_ram),
            "processes_on_disk": len(self.processes_on_disk)
        }
    
    def __repr__(self) -> str:
        return f"MemoryManager(RAM: {self.ram_size - self.ram_free}/{self.ram_size}, " \
               f"Disk: {len(self.processes_on_disk)} processes)"
