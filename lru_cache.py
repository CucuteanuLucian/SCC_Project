"""
Custom LRU (Least Recently Used) cache implementation.
"""
from typing import Dict, Any, Optional, Tuple


class Node:
    """Node in doubly-linked list for LRU cache."""
    
    def __init__(self, key: Any, value: Any = None):
        """Initialize node."""
        self.key = key
        self.value = value
        self.prev = None
        self.next = None


class LRUCache:
    """LRU cache implemented from scratch using doubly-linked list."""
    
    def __init__(self, capacity: int = float('inf')):
        """
        Initialize LRU cache.
        
        Args:
            capacity: Maximum number of items (if inf, no limit)
        """
        self.capacity = capacity
        self.cache: Dict[Any, Node] = {}
        
        # Dummy nodes for linked list
        self.head = Node(None)  # Most recent
        self.tail = Node(None)  # Least recent
        self.head.next = self.tail
        self.tail.prev = self.head
    
    def put(self, key: Any, value: Any = True):
        """Add or update item."""
        # Remove if exists
        if key in self.cache:
            self._remove_node(self.cache[key])
        
        # Create new node
        node = Node(key, value)
        self.cache[key] = node
        self._add_to_head(node)
        
        # Remove least recent if over capacity
        if len(self.cache) > self.capacity:
            removed_node = self.tail.prev
            self._remove_node(removed_node)
            del self.cache[removed_node.key]
    
    def get(self, key: Any) -> Optional[Any]:
        """Get item and mark as recently used."""
        if key not in self.cache:
            return None
        
        node = self.cache[key]
        self._remove_node(node)
        self._add_to_head(node)
        return node.value
    
    def move_to_end(self, key: Any):
        """Move item to end (most recent)."""
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            self._add_to_head(node)
    
    def update_access(self, key: Any):
        """Mark item as recently accessed."""
        if key in self.cache:
            node = self.cache[key]
            self._remove_node(node)
            self._add_to_head(node)
    
    def get_least_recent(self) -> Optional[Any]:
        """Get least recently used key."""
        if len(self.cache) == 0:
            return None
        return self.tail.prev.key
    
    def __contains__(self, key: Any) -> bool:
        """Check if key in cache."""
        return key in self.cache
    
    def __len__(self) -> int:
        """Return number of items."""
        return len(self.cache)
    
    def __getitem__(self, key: Any):
        """Get item value."""
        if key not in self.cache:
            raise KeyError(key)
        return self.cache[key].value
    
    def __setitem__(self, key: Any, value: Any):
        """Set item value."""
        self.put(key, value)
    
    def __delitem__(self, key: Any):
        """Delete item from cache."""
        if key not in self.cache:
            raise KeyError(key)
        node = self.cache[key]
        self._remove_node(node)
        del self.cache[key]

    def __iter__(self):
        """Iterate over keys from least to most recent."""
        current = self.tail.prev
        while current != self.head:
            yield current.key
            current = current.prev
    
    def items(self):
        """Iterate over (key, value) pairs."""
        current = self.tail.prev
        while current != self.head:
            yield (current.key, current.value)
            current = current.prev
    
    def keys(self):
        """Get list of keys."""
        return list(self)
    
    def values(self):
        """Get list of values."""
        current = self.tail.prev
        result = []
        while current != self.head:
            result.append(current.value)
            current = current.prev
        return result
    
    def _remove_node(self, node: Node):
        """Remove node from linked list."""
        prev_node = node.prev
        next_node = node.next
        prev_node.next = next_node
        next_node.prev = prev_node
    
    def _add_to_head(self, node: Node):
        """Add node to head (most recent)."""
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node
