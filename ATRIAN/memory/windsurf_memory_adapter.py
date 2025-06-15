# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - @references {C:\EGOS\ATRiAN\atrian_ethical_compass.py}
# - @references {C:\EGOS\run_tools.py}
# - @references {C:\EGOS\scripts\system_health\core\validator.py}
# --- 

import os
import sys
import json
import logging
import time
import hashlib
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union, Set
from enum import Enum
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("atrian_memory_adapter")

# Privacy sensitivity levels
class PrivacySensitivity(Enum):
    """Enumeration of privacy sensitivity levels for memory operations."""
    LOW = 1      # General, non-sensitive operations
    MEDIUM = 2   # Operations with some sensitive context
    HIGH = 3     # Operations with highly sensitive data
    CRITICAL = 4 # Operations with critical security implications

# Memory retention policies
class RetentionPolicy(Enum):
    """Enumeration of retention policies for stored memory items."""
    TRANSIENT = 1  # Retain only for current session
    SHORT_TERM = 2 # Retain for a short period (e.g., 24 hours)
    MEDIUM_TERM = 3 # Retain for a medium period (e.g., 30 days)
    LONG_TERM = 4  # Retain for extended period (e.g., 1 year)
    PERMANENT = 5  # Retain indefinitely (requires explicit user consent)

# Memory backend interface
class MemoryBackendInterface(ABC):
    """Abstract base class for memory storage backends."""
    
    @abstractmethod
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store a value with associated metadata."""
        pass
    
    @abstractmethod
    def retrieve(self, key: str) -> Tuple[Any, Dict[str, Any]]:
        """Retrieve a value and its metadata."""
        pass
    
    @abstractmethod
    def list(self, prefix: str = "") -> List[str]:
        """List all keys with the given prefix."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Delete a value by key."""
        pass
    
    @abstractmethod
    def clear(self, prefix: str = "") -> int:
        """Clear all values with the given prefix. Returns count of cleared items."""
        pass


class PrivacyFilter:
    """Privacy filter for detecting and handling sensitive data.
    
    This class implements the Sacred Privacy (SP) principle by detecting,
    anonymizing, and managing sensitive data in memory operations.
    
    Attributes:
        privacy_terms (Set[str]): Set of terms that indicate sensitive data
        anonymization_patterns (Dict[str, str]): Patterns for anonymizing data
        retention_policies (Dict[PrivacySensitivity, timedelta]): Retention periods by sensitivity
    """
    
    def __init__(self):
        """Initialize the privacy filter with default settings."""
        # Terms that indicate sensitive data
        self.privacy_terms = {
            # Personal identifiers
            "password", "secret", "token", "key", "credential", "auth", "authentication",
            "personal", "private", "sensitive", "confidential", "restricted",
            # Financial terms
            "credit", "debit", "card", "cvv", "ccv", "payment", "bank", "account",
            # Identity terms
            "ssn", "social security", "passport", "license", "id number", "identity",
            # Contact information
            "address", "phone", "email", "contact", "location", "gps", "coordinate",
            # Health information
            "health", "medical", "diagnosis", "treatment", "prescription", "patient"
        }
        
        # Patterns for anonymizing different types of data
        self.anonymization_patterns = {
            # Credit card pattern: 16 digits, possibly with spaces or dashes
            r'\b(?:\d[ -]*?){13,16}\b': '[CREDIT_CARD]',
            # Email pattern
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b': '[EMAIL]',
            # Phone number patterns (various formats)
            r'\b\(?\d{3}\)?[-. ]?\d{3}[-. ]?\d{4}\b': '[PHONE]',
            # Social Security Number pattern
            r'\b\d{3}-\d{2}-\d{4}\b': '[SSN]',
            # IP address pattern
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b': '[IP_ADDRESS]',
            # URL pattern
            r'https?://[^\s]+': '[URL]',
            # API key pattern (alphanumeric string of 20+ chars)
            r'\b[A-Za-z0-9_\-]{20,}\b': '[API_KEY]',
            # Password pattern (when explicitly labeled)
            r'(?i)password[\s:=]+[^\s]+': '[PASSWORD]',
            # Token pattern (when explicitly labeled)
            r'(?i)token[\s:=]+[^\s]+': '[TOKEN]'
        }
        
        # Retention policies by sensitivity level
        self.retention_policies = {
            PrivacySensitivity.LOW: timedelta(days=365),       # 1 year
            PrivacySensitivity.MEDIUM: timedelta(days=90),     # 90 days
            PrivacySensitivity.HIGH: timedelta(days=30),       # 30 days
            PrivacySensitivity.CRITICAL: timedelta(days=1)     # 1 day
        }
        
        logger.info("PrivacyFilter initialized with default settings")
    
    def detect_sensitivity(self, data: Any) -> PrivacySensitivity:
        """Detect the privacy sensitivity level of data.
        
        Args:
            data (Any): The data to analyze
            
        Returns:
            PrivacySensitivity: The detected sensitivity level
        """
        # Convert data to string for analysis
        data_str = str(data).lower()
        
        # Check for critical patterns first
        for pattern in [r'\b\d{3}-\d{2}-\d{4}\b', r'(?i)password[\s:=]+[^\s]+']:
            if re.search(pattern, data_str):
                return PrivacySensitivity.CRITICAL
        
        # Count privacy terms
        term_count = sum(1 for term in self.privacy_terms if term in data_str)
        
        # Determine sensitivity based on term count
        if term_count >= 3:
            return PrivacySensitivity.HIGH
        elif term_count >= 1:
            return PrivacySensitivity.MEDIUM
        else:
            return PrivacySensitivity.LOW
    
    def anonymize_data(self, data: Any) -> Any:
        """Anonymize sensitive data.
        
        Args:
            data (Any): The data to anonymize
            
        Returns:
            Any: The anonymized data
        """
        # Handle different data types
        if isinstance(data, str):
            # Apply anonymization patterns to string data
            result = data
            for pattern, replacement in self.anonymization_patterns.items():
                result = re.sub(pattern, replacement, result)
            return result
        elif isinstance(data, dict):
            # Recursively anonymize dictionary values
            return {k: self.anonymize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            # Recursively anonymize list items
            return [self.anonymize_data(item) for item in data]
        else:
            # Return other data types unchanged
            return data
    
    def should_retain(self, sensitivity: PrivacySensitivity, timestamp: datetime) -> bool:
        """Determine if data should be retained based on sensitivity and age.
        
        Args:
            sensitivity (PrivacySensitivity): The sensitivity level of the data
            timestamp (datetime): When the data was created or last modified
            
        Returns:
            bool: True if data should be retained, False if it should be deleted
        """
        # Get retention period for sensitivity level
        retention_period = self.retention_policies.get(sensitivity, timedelta(days=30))
        
        # Calculate expiration date
        expiration_date = timestamp + retention_period
        
        # Compare with current date
        return datetime.now() < expiration_date
    
    def get_retention_date(self, sensitivity: PrivacySensitivity) -> datetime:
        """Get the retention date for a given sensitivity level.
        
        Args:
            sensitivity (PrivacySensitivity): The sensitivity level
            
        Returns:
            datetime: The date until which data should be retained
        """
        retention_period = self.retention_policies.get(sensitivity, timedelta(days=30))
        return datetime.now() + retention_period


class LocalStorageBackend(MemoryBackendInterface):
    """Local storage backend implementation using file system.
    
    This backend stores data in JSON files within a designated directory.
    Each key maps to a separate file to prevent concurrent access issues.
    
    Attributes:
        storage_dir (str): Directory path for storing memory files
        metadata_suffix (str): Suffix for metadata files
    """
    
    def __init__(self, storage_dir: str = None):
        """Initialize the local storage backend.
        
        Args:
            storage_dir (str, optional): Directory path for storing memory files.
                If None, uses a default path in the user's home directory.
        """
        if storage_dir is None:
            home_dir = os.path.expanduser("~")
            storage_dir = os.path.join(home_dir, ".atrian", "memory")
        
        self.storage_dir = storage_dir
        self.metadata_suffix = ".metadata"
        
        # Ensure storage directory exists
        os.makedirs(self.storage_dir, exist_ok=True)
        
        logger.info(f"LocalStorageBackend initialized at {self.storage_dir}")
    
    def _get_file_path(self, key: str, is_metadata: bool = False) -> str:
        """Get the file path for a key.
        
        Args:
            key (str): The key to get the file path for
            is_metadata (bool): Whether to get the metadata file path
            
        Returns:
            str: The file path for the key
        """
        # Sanitize key for file system use
        safe_key = re.sub(r'[^\w\-\.]', '_', key)
        
        # Add metadata suffix if needed
        if is_metadata:
            safe_key += self.metadata_suffix
        
        return os.path.join(self.storage_dir, safe_key)
    
    def store(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Store a value with associated metadata.
        
        Args:
            key (str): The key to store the value under
            value (Any): The value to store
            metadata (Dict[str, Any], optional): Metadata to associate with the value
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Store value
            value_path = self._get_file_path(key)
            with open(value_path, 'w') as f:
                json.dump(value, f, indent=2)
            
            # Store metadata if provided
            if metadata is not None:
                # Add timestamp if not present
                if 'timestamp' not in metadata:
                    metadata['timestamp'] = datetime.now().isoformat()
                
                metadata_path = self._get_file_path(key, is_metadata=True)
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            return True
        except Exception as e:
            logger.error(f"Error storing {key}: {str(e)}")
            return False
    
    def retrieve(self, key: str) -> Tuple[Any, Dict[str, Any]]:
        """Retrieve a value and its metadata.
        
        Args:
            key (str): The key to retrieve
            
        Returns:
            Tuple[Any, Dict[str, Any]]: The value and its metadata
        """
        value = None
        metadata = {}
        
        try:
            # Retrieve value
            value_path = self._get_file_path(key)
            if os.path.exists(value_path):
                with open(value_path, 'r') as f:
                    value = json.load(f)
            
            # Retrieve metadata if exists
            metadata_path = self._get_file_path(key, is_metadata=True)
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
        except Exception as e:
            logger.error(f"Error retrieving {key}: {str(e)}")
        
        return value, metadata
    
    def list(self, prefix: str = "") -> List[str]:
        """List all keys with the given prefix.
        
        Args:
            prefix (str, optional): Prefix to filter keys by
            
        Returns:
            List[str]: List of keys matching the prefix
        """
        try:
            # List all files in storage directory
            all_files = os.listdir(self.storage_dir)
            
            # Filter out metadata files and apply prefix filter
            keys = [
                f for f in all_files 
                if not f.endswith(self.metadata_suffix) and 
                (not prefix or f.startswith(prefix))
            ]
            
            return keys
        except Exception as e:
            logger.error(f"Error listing keys with prefix {prefix}: {str(e)}")
            return []
    
    def delete(self, key: str) -> bool:
        """Delete a value by key.
        
        Args:
            key (str): The key to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Delete value file
            value_path = self._get_file_path(key)
            if os.path.exists(value_path):
                os.remove(value_path)
            
            # Delete metadata file if exists
            metadata_path = self._get_file_path(key, is_metadata=True)
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return True
        except Exception as e:
            logger.error(f"Error deleting {key}: {str(e)}")
            return False
    
    def clear(self, prefix: str = "") -> int:
        """Clear all values with the given prefix.
        
        Args:
            prefix (str, optional): Prefix to filter keys by
            
        Returns:
            int: Number of items cleared
        """
        try:
            # Get keys to clear
            keys = self.list(prefix)
            count = 0
            
            # Delete each key
            for key in keys:
                if self.delete(key):
                    count += 1
            
            return count
        except Exception as e:
            logger.error(f"Error clearing keys with prefix {prefix}: {str(e)}")
            return 0


class WindsurfMemoryAdapter:
    """Memory adapter for integrating ATRiAN components with Windsurf IDE.
    
    This adapter provides a unified interface for storing and retrieving
    trust scores, operation history, and other ATRiAN state information
    in the Windsurf IDE's memory system.
    
    Attributes:
        backend (MemoryBackendInterface): Storage backend implementation
        privacy_filter (PrivacyFilter): Privacy filter for sensitive data
        trust_decay_rate (float): Rate at which trust decays over time
        context_relevance_threshold (float): Threshold for context relevance
    """
    
    def __init__(self, backend: MemoryBackendInterface = None, config_path: str = None):
        """Initialize the Windsurf memory adapter.
        
        Args:
            backend (MemoryBackendInterface, optional): Storage backend implementation.
                If None, uses LocalStorageBackend by default.
            config_path (str, optional): Path to configuration file.
                If provided, loads configuration from file.
        """
        # Initialize backend
        self.backend = backend or LocalStorageBackend()
        
        # Initialize privacy filter
        self.privacy_filter = PrivacyFilter()
        
        # Default configuration
        self.config = {
            "trust_decay_rate": 0.01,  # 1% decay per day
            "context_relevance_threshold": 0.3,  # Minimum relevance score (0-1)
            "max_operation_history": 100,  # Maximum operations to store per user
            "max_context_items": 10,  # Maximum context items to return
            "enable_privacy_filter": True,  # Whether to enable privacy filtering
            "enable_trust_decay": True,  # Whether to enable trust decay
            "enable_context_relevance": True  # Whether to enable context relevance scoring
        }
        
        # Load configuration if provided
        if config_path and os.path.exists(config_path):
            self._load_config(config_path)
        
        logger.info("WindsurfMemoryAdapter initialized")
    
    def _load_config(self, config_path: str) -> None:
        """Load configuration from file.
        
        Args:
            config_path (str): Path to configuration file
        """
        try:
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                self.config.update(loaded_config)
            logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
    
    def _get_key(self, key_type: str, user_id: str, sub_key: str = None) -> str:
        """Generate a storage key.
        
        Args:
            key_type (str): Type of key (e.g., 'trust', 'operation')
            user_id (str): User identifier
            sub_key (str, optional): Sub-key for additional specificity
            
        Returns:
            str: Generated key
        """
        key = f"atrian:{key_type}:{user_id}"
        if sub_key:
            key += f":{sub_key}"
        return key
    
    def _apply_trust_decay(self, trust_score: float, last_updated: datetime) -> float:
        """Apply time-based trust decay to a trust score.
        
        Implements Compassionate Temporality (CT) by gradually
        decaying trust scores over time when not reinforced.
        
        Args:
            trust_score (float): Current trust score (0.0 to 1.0)
            last_updated (datetime): When the trust score was last updated
            
        Returns:
            float: Decayed trust score
        """
        if not self.config["enable_trust_decay"]:
            return trust_score
        
        # Calculate days since last update
        days_elapsed = (datetime.now() - last_updated).total_seconds() / (24 * 3600)
        
        # Apply decay formula: score * (1 - decay_rate)^days
        decay_factor = (1 - self.config["trust_decay_rate"]) ** days_elapsed
        decayed_score = trust_score * decay_factor
        
        # Ensure score doesn't fall below minimum threshold (0.3)
        return max(0.3, decayed_score)
    
    def _calculate_context_relevance(self, context: Dict[str, Any], operation_type: str) -> float:
        """Calculate relevance score for a context item.
        
        Args:
            context (Dict[str, Any]): Context item to score
            operation_type (str): Current operation type
            
        Returns:
            float: Relevance score (0.0 to 1.0)
        """
        if not self.config["enable_context_relevance"]:
            return 1.0
        
        # Base score starts at 0.5
        score = 0.5
        
        # Boost score if operation type matches
        if context.get("operation_type") == operation_type:
            score += 0.3
        
        # Apply recency factor (newer items are more relevant)
        if "timestamp" in context:
            try:
                timestamp = datetime.fromisoformat(context["timestamp"])
                days_old = (datetime.now() - timestamp).total_seconds() / (24 * 3600)
                # Exponential decay based on age
                recency_factor = 0.2 * (0.9 ** min(days_old, 30))
                score += recency_factor
            except (ValueError, TypeError):
                pass
        
        return min(1.0, score)
    
    def store_trust_score(self, user_id: str, score: float) -> bool:
        """Store a trust score for a user.
        
        Args:
            user_id (str): User identifier
            score (float): Trust score (0.0 to 1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Validate score
        score = max(0.0, min(1.0, score))
        
        # Create metadata
        metadata = {
            "timestamp": datetime.now().isoformat(),
            "type": "trust_score"
        }
        
        # Store score
        key = self._get_key("trust", user_id)
        return self.backend.store(key, score, metadata)
    
    def retrieve_trust_score(self, user_id: str) -> Optional[float]:
        """Retrieve a trust score for a user.
        
        Args:
            user_id (str): User identifier
            
        Returns:
            Optional[float]: Trust score if found, None otherwise
        """
        # Get key
        key = self._get_key("trust", user_id)
        
        # Retrieve score and metadata
        score, metadata = self.backend.retrieve(key)
        
        if score is not None:
            # Apply trust decay if enabled
            if self.config["enable_trust_decay"] and "timestamp" in metadata:
                try:
                    last_updated = datetime.fromisoformat(metadata["timestamp"])
                    score = self._apply_trust_decay(score, last_updated)
                    
                    # Update score with decayed value if significantly different
                    if abs(score - float(score)) >= 0.01:
                        self.store_trust_score(user_id, score)
                except (ValueError, TypeError):
                    pass
            
            return score
        
        return None
    
    def store_operation(self, user_id: str, operation_type: str, 
                       context: Dict[str, Any], result: Dict[str, Any]) -> str:
        """Store an operation in memory.
        
        Args:
            user_id (str): User identifier
            operation_type (str): Type of operation
            context (Dict[str, Any]): Operation context
            result (Dict[str, Any]): Operation result
            
        Returns:
            str: Operation ID
        """
        # Generate operation ID
        operation_id = f"{operation_type}_{int(time.time())}_{hashlib.md5(str(context).encode()).hexdigest()[:8]}"
        
        # Prepare operation data
        operation_data = {
            "operation_id": operation_id,
            "operation_type": operation_type,
            "context": context,
            "result": result,
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id
        }
        
        # Apply privacy filter if enabled
        if self.config["enable_privacy_filter"]:
            # Detect sensitivity
            sensitivity = self.privacy_filter.detect_sensitivity(operation_data)
            
            # Anonymize data if sensitive
            if sensitivity in [PrivacySensitivity.HIGH, PrivacySensitivity.CRITICAL]:
                operation_data["context"] = self.privacy_filter.anonymize_data(context)
                operation_data["result"] = self.privacy_filter.anonymize_data(result)
            
            # Add sensitivity to metadata
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "type": "operation",
                "sensitivity": sensitivity.value,
                "retention_date": self.privacy_filter.get_retention_date(sensitivity).isoformat()
            }
        else:
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "type": "operation"
            }
        
        # Store operation
        key = self._get_key("operation", user_id, operation_id)
        self.backend.store(key, operation_data, metadata)
        
        # Update operation history index
        self._update_operation_history(user_id, operation_id, operation_type)
        
        return operation_id
    
    def _update_operation_history(self, user_id: str, operation_id: str, operation_type: str) -> None:
        """Update the operation history index for a user.
        
        Args:
            user_id (str): User identifier
            operation_id (str): Operation identifier
            operation_type (str): Type of operation
        """
        # Get history key
        history_key = self._get_key("history", user_id)
        
        # Retrieve existing history
        history, metadata = self.backend.retrieve(history_key)
        
        if history is None:
            # Initialize history if not exists
            history = {
                "operations": [],
                "by_type": {}
            }
            metadata = {
                "timestamp": datetime.now().isoformat(),
                "type": "history"
            }
        
        # Add operation to history
        operation_entry = {
            "id": operation_id,
            "type": operation_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to main operations list
        history["operations"].insert(0, operation_entry)
        
        # Limit history size
        if len(history["operations"]) > self.config["max_operation_history"]:
            history["operations"] = history["operations"][:self.config["max_operation_history"]]
        
        # Add to type-specific list
        if operation_type not in history["by_type"]:
            history["by_type"][operation_type] = []
        
        history["by_type"][operation_type].insert(0, operation_entry)
        
        # Limit type-specific history size
        if len(history["by_type"][operation_type]) > self.config["max_operation_history"]:
            history["by_type"][operation_type] = history["by_type"][operation_type][:self.config["max_operation_history"]]
        
        # Store updated history
        self.backend.store(history_key, history, metadata)
    
    def retrieve_operation(self, user_id: str, operation_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve an operation from memory.
        
        Args:
            user_id (str): User identifier
            operation_id (str): Operation identifier
            
        Returns:
            Optional[Dict[str, Any]]: Operation data if found, None otherwise
        """
        # Get key
        key = self._get_key("operation", user_id, operation_id)
        
        # Retrieve operation
        operation, metadata = self.backend.retrieve(key)
        
        return operation
    
    def retrieve_context(self, user_id: str, operation_type: str, limit: int = None) -> List[Dict[str, Any]]:
        """Retrieve relevant context for an operation type.
        
        Args:
            user_id (str): User identifier
            operation_type (str): Type of operation
            limit (int, optional): Maximum number of context items to return
            
        Returns:
            List[Dict[str, Any]]: List of relevant context items
        """
        if limit is None:
            limit = self.config["max_context_items"]
        
        # Get history key
        history_key = self._get_key("history", user_id)
        
        # Retrieve history
        history, _ = self.backend.retrieve(history_key)
        
        if history is None or "by_type" not in history or operation_type not in history["by_type"]:
            return []
        
        # Get operations of the specified type
        operations = history["by_type"][operation_type]
        
        # Retrieve and score context items
        context_items = []
        for op in operations[:min(limit * 2, len(operations))]:
            operation = self.retrieve_operation(user_id, op["id"])
            if operation:
                # Calculate relevance score
                relevance = self._calculate_context_relevance(operation, operation_type)
                
                # Add to context items if above threshold
                if relevance >= self.config["context_relevance_threshold"]:
                    context_items.append({
                        "operation": operation,
                        "relevance": relevance
                    })
        
        # Sort by relevance and limit
        context_items.sort(key=lambda x: x["relevance"], reverse=True)
        context_items = context_items[:limit]
        
        # Return just the operations
        return [item["operation"] for item in context_items]
    
    def clear_sensitive_data(self, user_id: str, data_type: str = None) -> int:
        """Clear sensitive data from memory.
        
        Args:
            user_id (str): User identifier
            data_type (str, optional): Type of data to clear (e.g., 'operation_type')
            
        Returns:
            int: Number of items cleared
        """
        cleared_count = 0
        
        # Get history key
        history_key = self._get_key("history", user_id)
        
        # Retrieve history
        history, history_metadata = self.backend.retrieve(history_key)
        
        if history is None:
            return 0
        
        # If data_type is specified, clear only that type
        if data_type:
            if "by_type" in history and data_type in history["by_type"]:
                # Get operations of the specified type
                operations = history["by_type"][data_type]
                
                # Clear each operation
                for op in operations:
                    key = self._get_key("operation", user_id, op["id"])
                    if self.backend.delete(key):
                        cleared_count += 1
                
                # Remove from history
                history["by_type"].pop(data_type)
                
                # Update main operations list
                history["operations"] = [op for op in history["operations"] if op["type"] != data_type]
                
                # Store updated history
                self.backend.store(history_key, history, history_metadata)
        else:
            # Clear all operations
            if "operations" in history:
                for op in history["operations"]:
                    key = self._get_key("operation", user_id, op["id"])
                    if self.backend.delete(key):
                        cleared_count += 1
            
            # Clear history
            self.backend.delete(history_key)
        
        return cleared_count
    
    def prune_expired_data(self) -> int:
        """Prune expired data based on retention policies.
        
        Returns:
            int: Number of items pruned
        """
        pruned_count = 0
        
        # List all operation keys
        operation_keys = self.backend.list("atrian:operation:")
        
        for key in operation_keys:
            # Retrieve operation and metadata
            operation, metadata = self.backend.retrieve(key)
            
            if operation and metadata and "sensitivity" in metadata and "timestamp" in metadata:
                try:
                    # Parse sensitivity and timestamp
                    sensitivity = PrivacySensitivity(int(metadata["sensitivity"]))
                    timestamp = datetime.fromisoformat(metadata["timestamp"])
                    
                    # Check if should be retained
                    if not self.privacy_filter.should_retain(sensitivity, timestamp):
                        # Delete expired data
                        if self.backend.delete(key):
                            pruned_count += 1
                            
                            # Extract user_id and operation_id from key
                            parts = key.split(":")
                            if len(parts) >= 4:
                                user_id = parts[2]
                                operation_id = parts[3]
                                
                                # Update history to remove pruned operation
                                self._remove_from_history(user_id, operation_id)
                except (ValueError, TypeError) as e:
                    logger.error(f"Error processing metadata for {key}: {str(e)}")
        
        return pruned_count
    
    def _remove_from_history(self, user_id: str, operation_id: str) -> None:
        """Remove an operation from the history index.
        
        Args:
            user_id (str): User identifier
            operation_id (str): Operation identifier
        """
        # Get history key
        history_key = self._get_key("history", user_id)
        
        # Retrieve history
        history, metadata = self.backend.retrieve(history_key)
        
        if history is None:
            return
        
        # Remove from main operations list
        if "operations" in history:
            history["operations"] = [op for op in history["operations"] if op["id"] != operation_id]
        
        # Remove from type-specific lists
        if "by_type" in history:
            for op_type in history["by_type"]:
                history["by_type"][op_type] = [op for op in history["by_type"][op_type] if op["id"] != operation_id]
        
        # Store updated history
        self.backend.store(history_key, history, metadata)
    
    def get_stats(self, user_id: str = None) -> Dict[str, Any]:
        """Get memory usage statistics.
        
        Args:
            user_id (str, optional): User identifier to get stats for
            
        Returns:
            Dict[str, Any]: Memory usage statistics
        """
        stats = {
            "total_items": 0,
            "operation_count": 0,
            "trust_score_count": 0,
            "history_count": 0,
            "by_sensitivity": {
                "low": 0,
                "medium": 0,
                "high": 0,
                "critical": 0
            }
        }
        
        # Get prefix for listing
        prefix = "atrian:"
        if user_id:
            prefix += f"*:{user_id}"
        
        # List all keys
        keys = self.backend.list(prefix)
        stats["total_items"] = len(keys)
        
        # Count by type
        for key in keys:
            parts = key.split(":")
            if len(parts) >= 2:
                key_type = parts[1]
                
                if key_type == "operation":
                    stats["operation_count"] += 1
                    
                    # Get sensitivity if available
                    _, metadata = self.backend.retrieve(key)
                    if metadata and "sensitivity" in metadata:
                        try:
                            sensitivity = PrivacySensitivity(int(metadata["sensitivity"]))
                            if sensitivity == PrivacySensitivity.LOW:
                                stats["by_sensitivity"]["low"] += 1
                            elif sensitivity == PrivacySensitivity.MEDIUM:
                                stats["by_sensitivity"]["medium"] += 1
                            elif sensitivity == PrivacySensitivity.HIGH:
                                stats["by_sensitivity"]["high"] += 1
                            elif sensitivity == PrivacySensitivity.CRITICAL:
                                stats["by_sensitivity"]["critical"] += 1
                        except (ValueError, TypeError):
                            pass
                elif key_type == "trust":
                    stats["trust_score_count"] += 1
                elif key_type == "history":
                    stats["history_count"] += 1
        
        return stats