"""
Custom queue implementation (FIFO).
"""
from typing import List, Any


class Queue:
    """A FIFO queue implemented from scratch."""
    
    def __init__(self):
        """Initialize queue."""
        self.items: List[Any] = []
        self._front = 0  # Index of front item
    
    def enqueue(self, item: Any):
        """Add item to end of queue."""
        self.items.append(item)
    
    def dequeue(self) -> Any:
        """Remove and return item from front of queue."""
        if self._front >= len(self.items):
            raise IndexError("dequeue from empty queue")
        
        item = self.items[self._front]
        self._front += 1
        
        # Cleanup: reset if queue is empty or front is too far
        if self._front > len(self.items) // 2 and self._front > 100:
            self.items = self.items[self._front:]
            self._front = 0
        
        return item
    
    def peek(self) -> Any:
        """Return front item without removing."""
        if self._front >= len(self.items):
            raise IndexError("peek from empty queue")
        return self.items[self._front]
    
    def append(self, item: Any):
        """Alias for enqueue."""
        self.enqueue(item)
    
    def popleft(self) -> Any:
        """Alias for dequeue (compatible with collections.deque)."""
        return self.dequeue()
    
    def remove(self, item: Any):
        """Remove first occurrence of item."""
        try:
            idx = self.items.index(item, self._front)
            # Shift items (inefficient but necessary for correctness)
            del self.items[idx]
        except ValueError:
            raise ValueError(f"{item} not in queue")
    
    def __len__(self) -> int:
        """Return number of items in queue."""
        return len(self.items) - self._front
    
    def __bool__(self) -> bool:
        """Return True if queue is not empty."""
        return self._front < len(self.items)
    
    def __iter__(self):
        """Iterate over items in queue."""
        return iter(self.items[self._front:])
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return self._front >= len(self.items)
