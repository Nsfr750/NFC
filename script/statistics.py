"""
Statistics tracking for NFC operations.

This module provides functionality to track and manage statistics
about read/write operations, tag types, and other metrics.
"""
import time
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

@dataclass
class OperationStats:
    """Statistics for a single operation."""
    operation_type: str  # 'read' or 'write'
    tag_type: str
    success: bool
    timestamp: float = field(default_factory=time.time)
    data_size: int = 0
    duration: float = 0.0
    error: Optional[str] = None

class StatisticsManager:
    """Manages collection and storage of operation statistics."""
    
    def __init__(self, data_dir: str = "data"):
        """Initialize the statistics manager.
        
        Args:
            data_dir: Directory to store statistics data
        """
        self.data_dir = data_dir
        self.stats: List[OperationStats] = []
        self._load_stats()
    
    def _ensure_data_dir(self) -> None:
        """Ensure the data directory exists."""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _get_stats_file(self) -> str:
        """Get the path to the statistics file."""
        return os.path.join(self.data_dir, "statistics.json")
    
    def _load_stats(self) -> None:
        """Load statistics from the data file."""
        stats_file = self._get_stats_file()
        if not os.path.exists(stats_file):
            return
            
        try:
            with open(stats_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.stats = [OperationStats(**item) for item in data]
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error loading statistics: {e}")
    
    def _save_stats(self) -> None:
        """Save statistics to the data file."""
        self._ensure_data_dir()
        stats_file = self._get_stats_file()
        
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump([asdict(stat) for stat in self.stats], f, indent=2)
        except IOError as e:
            print(f"Error saving statistics: {e}")
    
    def add_operation(self, operation_type: str, tag_type: str, success: bool,
                     data_size: int = 0, duration: float = 0.0, 
                     error: Optional[str] = None) -> None:
        """Add a new operation to the statistics.
        
        Args:
            operation_type: Type of operation ('read' or 'write')
            tag_type: Type of NFC tag
            success: Whether the operation was successful
            data_size: Size of the data in bytes
            duration: Duration of the operation in seconds
            error: Error message if the operation failed
        """
        stats = OperationStats(
            operation_type=operation_type,
            tag_type=tag_type,
            success=success,
            data_size=data_size,
            duration=duration,
            error=error
        )
        self.stats.append(stats)
        self._save_stats()
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all statistics."""
        if not self.stats:
            return {}
        
        total_operations = len(self.stats)
        read_ops = [op for op in self.stats if op.operation_type == 'read']
        write_ops = [op for op in self.stats if op.operation_type == 'write']
        
        successful_ops = [op for op in self.stats if op.success]
        failed_ops = [op for op in self.stats if not op.success]
        
        # Calculate tag type distribution
        tag_types = {}
        for op in self.stats:
            tag_types[op.tag_type] = tag_types.get(op.tag_type, 0) + 1
        
        # Calculate average operation duration
        avg_duration = sum(op.duration for op in self.stats) / total_operations if self.stats else 0
        
        return {
            'total_operations': total_operations,
            'read_operations': len(read_ops),
            'write_operations': len(write_ops),
            'success_rate': len(successful_ops) / total_operations * 100 if total_ops else 0,
            'tag_type_distribution': tag_types,
            'average_duration': avg_duration,
            'last_operation': max(self.stats, key=lambda x: x.timestamp).timestamp if self.stats else None,
            'data_processed': sum(op.data_size for op in self.stats if op.data_size)
        }
    
    def get_recent_operations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent operations.
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of recent operations as dictionaries
        """
        sorted_ops = sorted(self.stats, key=lambda x: x.timestamp, reverse=True)
        return [asdict(op) for op in sorted_ops[:limit]]
    
    def clear_statistics(self) -> None:
        """Clear all statistics."""
        self.stats = []
        self._save_stats()

# Global instance for easy access
stats_manager = StatisticsManager()

def record_operation(operation_type: str, tag_type: str, success: bool, 
                   data_size: int = 0, duration: float = 0.0, 
                   error: Optional[str] = None) -> None:
    """Convenience function to record an operation."""
    stats_manager.add_operation(
        operation_type=operation_type,
        tag_type=tag_type,
        success=success,
        data_size=data_size,
        duration=duration,
        error=error
    )
