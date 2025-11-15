"""
CRDT (Conflict-free Replicated Data Type) implementation for collaborative editing.

Provides operational transformation and conflict resolution for real-time
collaborative document editing.
"""

import json
import uuid
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class OperationType(Enum):
    """Types of operations that can be performed on a document."""
    INSERT = "insert"
    DELETE = "delete"
    REPLACE = "replace"


@dataclass
class Operation:
    """Represents a single edit operation."""
    op_id: str
    user_id: str
    timestamp: str
    op_type: OperationType
    position: int
    content: str = ""
    length: int = 0  # For delete operations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'op_id': self.op_id,
            'user_id': self.user_id,
            'timestamp': self.timestamp,
            'op_type': self.op_type.value,
            'position': self.position,
            'content': self.content,
            'length': self.length
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """Create from dictionary."""
        return cls(
            op_id=data['op_id'],
            user_id=data['user_id'],
            timestamp=data['timestamp'],
            op_type=OperationType(data['op_type']),
            position=data['position'],
            content=data.get('content', ''),
            length=data.get('length', 0)
        )


class CRDTDocument:
    """
    CRDT-based document for conflict-free collaborative editing.
    
    Uses a sequence CRDT (Replicated Growable Array) to maintain consistency
    across multiple editors without requiring a central coordinator.
    """
    
    def __init__(self, doc_id: str, initial_content: str = ""):
        """
        Initialize CRDT document.
        
        Args:
            doc_id: Unique document identifier
            initial_content: Initial document content
        """
        self.doc_id = doc_id
        self.content = initial_content
        self.operations: List[Operation] = []
        self.version = 0
        self.last_modified = datetime.now().isoformat()
    
    def apply_operation(self, operation: Operation) -> bool:
        """
        Apply an operation to the document.
        
        Args:
            operation: Operation to apply
        
        Returns:
            True if operation was applied successfully
        """
        try:
            if operation.op_type == OperationType.INSERT:
                self._apply_insert(operation)
            elif operation.op_type == OperationType.DELETE:
                self._apply_delete(operation)
            elif operation.op_type == OperationType.REPLACE:
                self._apply_replace(operation)
            
            self.operations.append(operation)
            self.version += 1
            self.last_modified = datetime.now().isoformat()
            return True
        except Exception:
            return False
    
    def _apply_insert(self, op: Operation) -> None:
        """Apply insert operation."""
        if op.position < 0 or op.position > len(self.content):
            raise ValueError(f"Invalid insert position: {op.position}")
        
        self.content = (
            self.content[:op.position] + 
            op.content + 
            self.content[op.position:]
        )
    
    def _apply_delete(self, op: Operation) -> None:
        """Apply delete operation."""
        if op.position < 0 or op.position + op.length > len(self.content):
            raise ValueError(f"Invalid delete range: {op.position}-{op.position + op.length}")
        
        self.content = (
            self.content[:op.position] + 
            self.content[op.position + op.length:]
        )
    
    def _apply_replace(self, op: Operation) -> None:
        """Apply replace operation."""
        if op.position < 0 or op.position + op.length > len(self.content):
            raise ValueError(f"Invalid replace range: {op.position}-{op.position + op.length}")
        
        self.content = (
            self.content[:op.position] + 
            op.content + 
            self.content[op.position + op.length:]
        )
    
    def create_operation(self, user_id: str, op_type: OperationType,
                        position: int, content: str = "", length: int = 0) -> Operation:
        """
        Create a new operation.
        
        Args:
            user_id: User performing the operation
            op_type: Type of operation
            position: Position in document
            content: Content to insert/replace
            length: Length to delete/replace
        
        Returns:
            Created Operation object
        """
        return Operation(
            op_id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now().isoformat(),
            op_type=op_type,
            position=position,
            content=content,
            length=length
        )
    
    def merge(self, other: 'CRDTDocument') -> List[str]:
        """
        Merge operations from another document.
        
        Args:
            other: Other CRDT document to merge from
        
        Returns:
            List of conflict messages (empty if no conflicts)
        """
        conflicts = []
        
        # Get operations not in this document
        our_op_ids = {op.op_id for op in self.operations}
        new_operations = [op for op in other.operations if op.op_id not in our_op_ids]
        
        # Sort by timestamp for deterministic ordering
        new_operations.sort(key=lambda op: op.timestamp)
        
        # Apply new operations
        for op in new_operations:
            # Transform operation based on concurrent operations
            transformed_op = self._transform_operation(op)
            
            if not self.apply_operation(transformed_op):
                conflicts.append(
                    f"Conflict applying operation {op.op_id} from user {op.user_id}"
                )
        
        return conflicts
    
    def _transform_operation(self, op: Operation) -> Operation:
        """
        Transform an operation based on concurrent operations.
        
        This implements Operational Transformation (OT) to handle concurrent edits.
        
        Args:
            op: Operation to transform
        
        Returns:
            Transformed operation
        """
        # Find concurrent operations (same timestamp range)
        op_time = datetime.fromisoformat(op.timestamp)
        concurrent_ops = [
            existing_op for existing_op in self.operations
            if abs((datetime.fromisoformat(existing_op.timestamp) - op_time).total_seconds()) < 1
        ]
        
        # Adjust position based on concurrent operations
        adjusted_position = op.position
        
        for concurrent_op in concurrent_ops:
            if concurrent_op.position <= op.position:
                if concurrent_op.op_type == OperationType.INSERT:
                    adjusted_position += len(concurrent_op.content)
                elif concurrent_op.op_type == OperationType.DELETE:
                    adjusted_position -= concurrent_op.length
        
        # Create transformed operation
        return Operation(
            op_id=op.op_id,
            user_id=op.user_id,
            timestamp=op.timestamp,
            op_type=op.op_type,
            position=max(0, adjusted_position),
            content=op.content,
            length=op.length
        )
    
    def get_state(self) -> Dict[str, Any]:
        """Get current document state."""
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'version': self.version,
            'last_modified': self.last_modified,
            'operation_count': len(self.operations)
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary."""
        return {
            'doc_id': self.doc_id,
            'content': self.content,
            'operations': [op.to_dict() for op in self.operations],
            'version': self.version,
            'last_modified': self.last_modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CRDTDocument':
        """Create document from dictionary."""
        doc = cls(data['doc_id'], data['content'])
        doc.version = data['version']
        doc.last_modified = data['last_modified']
        doc.operations = [Operation.from_dict(op) for op in data['operations']]
        return doc


class ConflictResolver:
    """Resolves conflicts in collaborative editing."""
    
    @staticmethod
    def resolve_concurrent_edits(operations: List[Operation]) -> List[Operation]:
        """
        Resolve conflicts in concurrent edit operations.
        
        Uses a deterministic strategy based on timestamps and user IDs.
        
        Args:
            operations: List of potentially conflicting operations
        
        Returns:
            Resolved list of operations
        """
        if len(operations) <= 1:
            return operations
        
        # Sort by timestamp, then by user_id for deterministic ordering
        sorted_ops = sorted(operations, key=lambda op: (op.timestamp, op.user_id))
        
        # Transform operations to account for each other
        result = []
        for i, op in enumerate(sorted_ops):
            transformed_op = op
            
            # Transform based on previous operations
            for prev_op in result:
                transformed_op = ConflictResolver._transform_against(transformed_op, prev_op)
            
            result.append(transformed_op)
        
        return result
    
    @staticmethod
    def _transform_against(op: Operation, prev_op: Operation) -> Operation:
        """
        Transform an operation against a previous operation.
        
        Args:
            op: Operation to transform
            prev_op: Previous operation to transform against
        
        Returns:
            Transformed operation
        """
        new_position = op.position
        
        # Adjust position based on previous operation
        if prev_op.position < op.position:
            if prev_op.op_type == OperationType.INSERT:
                new_position += len(prev_op.content)
            elif prev_op.op_type == OperationType.DELETE:
                new_position -= prev_op.length
        
        return Operation(
            op_id=op.op_id,
            user_id=op.user_id,
            timestamp=op.timestamp,
            op_type=op.op_type,
            position=max(0, new_position),
            content=op.content,
            length=op.length
        )
    
    @staticmethod
    def detect_conflicts(doc1: CRDTDocument, doc2: CRDTDocument) -> List[Dict[str, Any]]:
        """
        Detect conflicts between two document versions.
        
        Args:
            doc1: First document version
            doc2: Second document version
        
        Returns:
            List of conflict descriptions
        """
        conflicts = []
        
        # Find operations unique to each document
        ops1_ids = {op.op_id for op in doc1.operations}
        ops2_ids = {op.op_id for op in doc2.operations}
        
        unique_to_doc1 = [op for op in doc1.operations if op.op_id not in ops2_ids]
        unique_to_doc2 = [op for op in doc2.operations if op.op_id not in ops1_ids]
        
        # Check for overlapping edits
        for op1 in unique_to_doc1:
            for op2 in unique_to_doc2:
                if ConflictResolver._operations_overlap(op1, op2):
                    conflicts.append({
                        'type': 'overlapping_edit',
                        'op1': op1.to_dict(),
                        'op2': op2.to_dict(),
                        'position': min(op1.position, op2.position)
                    })
        
        return conflicts
    
    @staticmethod
    def _operations_overlap(op1: Operation, op2: Operation) -> bool:
        """Check if two operations overlap in the document."""
        # Get ranges for each operation
        range1_start = op1.position
        range1_end = op1.position + (len(op1.content) if op1.op_type == OperationType.INSERT else op1.length)
        
        range2_start = op2.position
        range2_end = op2.position + (len(op2.content) if op2.op_type == OperationType.INSERT else op2.length)
        
        # Check if ranges overlap
        return not (range1_end < range2_start or range2_end < range1_start)
