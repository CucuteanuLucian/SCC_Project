"""
Custom priority queue implementation (min-heap).
"""
from typing import List, Any, Callable


class PriorityQueue:
    """A min-heap based priority queue implemented from scratch."""
    
    def __init__(self, compare: Callable = None):
        """
        Initialize priority queue.
        
        Args:
            compare: Optional custom comparison function. 
                    If None, uses < operator (min-heap)
        """
        self.heap: List[Any] = []
        self.compare = compare or (lambda a, b: a < b)
    
    def push(self, item: Any):
        """Add item to queue."""
        self.heap.append(item)
        self._sift_up(len(self.heap) - 1)
    
    def pop(self) -> Any:
        """Remove and return minimum item."""
        if not self.heap:
            raise IndexError("pop from empty priority queue")
        
        # Swap root with last item
        self.heap[0], self.heap[-1] = self.heap[-1], self.heap[0]
        item = self.heap.pop()
        
        # Restore heap property
        if self.heap:
            self._sift_down(0)
        
        return item
    
    def peek(self) -> Any:
        """Return minimum item without removing."""
        if not self.heap:
            raise IndexError("peek from empty priority queue")
        return self.heap[0]
    
    def _sift_up(self, idx: int):
        """Move item up to restore heap property."""
        while idx > 0:
            parent_idx = (idx - 1) // 2
            if self.compare(self.heap[idx], self.heap[parent_idx]):
                # Swap
                self.heap[idx], self.heap[parent_idx] = self.heap[parent_idx], self.heap[idx]
                idx = parent_idx
            else:
                break
    
    def _sift_down(self, idx: int):
        """Move item down to restore heap property."""
        while True:
            smallest = idx
            left_idx = 2 * idx + 1
            right_idx = 2 * idx + 2
            
            # Check left child
            if left_idx < len(self.heap) and self.compare(self.heap[left_idx], self.heap[smallest]):
                smallest = left_idx
            
            # Check right child
            if right_idx < len(self.heap) and self.compare(self.heap[right_idx], self.heap[smallest]):
                smallest = right_idx
            
            # If smallest is not current, swap and continue
            if smallest != idx:
                self.heap[idx], self.heap[smallest] = self.heap[smallest], self.heap[idx]
                idx = smallest
            else:
                break
    
    def __len__(self) -> int:
        """Return number of items in queue."""
        return len(self.heap)
    
    def __bool__(self) -> bool:
        """Return True if queue is not empty."""
        return len(self.heap) > 0
    
    def is_empty(self) -> bool:
        """Check if queue is empty."""
        return len(self.heap) == 0
