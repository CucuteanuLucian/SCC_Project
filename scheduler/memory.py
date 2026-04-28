"""
Virtual memory manager using LRU replacement policy.

Design:
  - The disk is a serial resource: only one transfer at a time.
  - in_memory is only True once the transfer is fully complete.
  - Eviction only touches processes that are fully in RAM (in_memory=True).
"""


class MemoryManager:
    def __init__(self, total_ram, disk_transfer_rate):
        self.total_ram = total_ram
        self.disk_transfer_rate = disk_transfer_rate
        self.used_ram = 0
        self._in_memory = []   # LRU list; front = oldest (evicted first)

    def touch(self, process):
        """Move process to MRU end."""
        if process in self._in_memory:
            self._in_memory.remove(process)
            self._in_memory.append(process)

    def evict_lru(self):
        """Evict the LRU process from RAM. Returns the evicted process."""
        assert self._in_memory, "Nothing left to evict!"

        # Iterate from oldest (index 0) to newest
        for i, process in enumerate(self._in_memory):
            # Only evict processes that aren't actively doing something critical
            # (Adjust these state strings to match your exact process model)
            if process.state not in ["RUNNING", "SYSCALL", "WAITING_MEM"]:
                victim = self._in_memory.pop(i)
                victim.in_memory = False
                self.used_ram -= victim.memory_required
                return victim

        # If the loop finishes without returning, you have a major problem!
        # E.g., a process requires more RAM than exists, or all RAM is held by running procs.
        raise RuntimeError("Out of Memory: No safe processes available to evict.")

    def complete_load(self, process):
        """Called when disk transfer finishes - marks process as in RAM."""
        self.used_ram += process.memory_required
        process.in_memory = True
        self._in_memory.append(process)
