"""
ATRiAN Ethics as a Service (EaaS) - Persistence Layer

This module provides persistence capabilities for the EaaS API, including
frameworks storage, evaluation history, and audit logging.

Version: 0.1.0
Last Modified: 2025-06-01

@references
  - file:///C:/EGOS/ATRiAN/eaas_models.py
  - file:///C:/EGOS/WORK_2025-06-01_ATRiAN_EaaS_Implementation_Progress.md
  - file:///C:/EGOS/ATRiAN/eaas_api.py
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import json
import os
import yaml
import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import shutil

from eaas_models import (
    EthicsFramework, AuditLogEntry, EthicsEvaluationResult, 
    EthicsExplanation, EthicsSuggestionResponse
)

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class EaasPersistenceManager:
    """
    Manages persistence for the Ethics as a Service (EaaS) API.
    
    Provides storage and retrieval functionality for:
    - Ethical frameworks
    - Evaluation results
    - Explanations
    - Suggestions
    - Audit logs
    
    This implementation focuses on file-based storage (JSON/YAML) to maintain
    alignment with other EGOS components while providing reliable persistence.
    Future versions could support database backends.
    """
    
    def __init__(self, data_dir: str = "C:/EGOS/ATRiAN/data"):
        """
        Initialize the persistence manager with the given data directory.
        
        Args:
            data_dir: Directory where data files will be stored
        """
        self.data_dir = Path(data_dir)
        self.frameworks_dir = self.data_dir / "frameworks"
        self.evaluations_dir = self.data_dir / "evaluations"
        self.explanations_dir = self.data_dir / "explanations"
        self.suggestions_dir = self.data_dir / "suggestions"
        self.audit_dir = self.data_dir / "audit"
        
        # Ensure directories exist
        for directory in [self.data_dir, self.frameworks_dir, self.evaluations_dir, 
                         self.explanations_dir, self.suggestions_dir, self.audit_dir]:
            directory.mkdir(parents=True, exist_ok=True)
            
        # Initialize cache
        self._frameworks_cache: Dict[str, EthicsFramework] = {}
        self._load_frameworks_to_cache()
        
        logger.info(f"EaaS Persistence Manager initialized with data directory: {self.data_dir}")
    
    # === Framework Management ===
    
    def _load_frameworks_to_cache(self) -> None:
        """Load all frameworks from disk into the cache."""
        try:
            for file_path in self.frameworks_dir.glob("*.json"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        framework = EthicsFramework(**data)
                        self._frameworks_cache[framework.id] = framework
                        logger.debug(f"Loaded framework {framework.id} from {file_path}")
                except Exception as e:
                    logger.error(f"Error loading framework from {file_path}: {e}")
            
            logger.info(f"Loaded {len(self._frameworks_cache)} frameworks into cache")
        except Exception as e:
            logger.error(f"Error during framework cache initialization: {e}")
    
    def get_frameworks(self) -> List[EthicsFramework]:
        """Get all ethical frameworks."""
        return list(self._frameworks_cache.values())
    
    def get_framework(self, framework_id: str) -> Optional[EthicsFramework]:
        """Get a specific ethical framework by ID."""
        return self._frameworks_cache.get(framework_id)
    
    def save_framework(self, framework: EthicsFramework) -> bool:
        """Save or update an ethical framework."""
        try:
            # First, validate that it's a proper EthicsFramework object
            if not isinstance(framework, EthicsFramework):
                framework = EthicsFramework(**framework.dict() if hasattr(framework, 'dict') else framework)
            
            # Update the last_updated timestamp
            framework.last_updated = datetime.utcnow()
            
            # Save to disk
            file_path = self.frameworks_dir / f"{framework.id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json.dumps instead of model.json() to avoid Pydantic compatibility issues
                json_data = json.dumps(framework.dict(), indent=2, default=str)
                f.write(json_data)
            
            # Update the cache
            self._frameworks_cache[framework.id] = framework
            logger.info(f"Framework {framework.id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving framework {framework.id if hasattr(framework, 'id') else 'unknown'}: {e}")
            return False
    
    def delete_framework(self, framework_id: str) -> bool:
        """Delete an ethical framework by ID."""
        try:
            # Check if exists
            if framework_id not in self._frameworks_cache:
                logger.warning(f"Framework {framework_id} not found for deletion")
                return False
            
            # Remove from disk
            file_path = self.frameworks_dir / f"{framework_id}.json"
            if file_path.exists():
                file_path.unlink()
            
            # Remove from cache
            del self._frameworks_cache[framework_id]
            logger.info(f"Framework {framework_id} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Error deleting framework {framework_id}: {e}")
            return False
    
    def import_frameworks_from_initial_data(self, source_file: str = "C:/EGOS/ATRiAN/eaas_api.py") -> int:
        """
        Import ethical frameworks from the initial data in eaas_api.py.
        Used for bootstrapping the persistence layer.
        
        Returns:
            int: Number of frameworks imported
        """
        try:
            import re
            count = 0
            
            # Read the source file 
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Look for the ethical_frameworks_db dictionary definition
            match = re.search(r'ethical_frameworks_db: Dict\[str, EthicsFramework\] = \{(.*?)\}', 
                              content, re.DOTALL)
            
            if not match:
                logger.warning(f"Could not find ethical_frameworks_db in {source_file}")
                return 0
            
            # Extract each framework definition and convert to proper objects
            # This is a simplified approach - we're assuming the format is consistent
            frameworks_text = match.group(1)
            framework_blocks = re.findall(r'"([^"]+)":\s+EthicsFramework\((.*?)\)', frameworks_text, re.DOTALL)
            
            for framework_id, framework_args in framework_blocks:
                # Convert the text to a dictionary
                # This is a simplistic approach using eval, which normally should be avoided
                # but we're assuming the source is trusted
                try:
                    framework_dict_text = "{" + framework_args + "}"
                    # Replace datetime.utcnow() with an ISO string for json serialization
                    framework_dict_text = re.sub(r'datetime\.utcnow\(\)', 
                                               f'"{datetime.utcnow().isoformat()}"', 
                                               framework_dict_text)
                    
                    # Safe evaluation using literal_eval
                    import ast
                    framework_dict = ast.literal_eval(framework_dict_text)
                    
                    # Convert datetime strings back to datetime objects
                    if isinstance(framework_dict.get("last_updated"), str):
                        framework_dict["last_updated"] = datetime.fromisoformat(framework_dict["last_updated"])
                    
                    # Create and save the framework
                    framework = EthicsFramework(**framework_dict)
                    if self.save_framework(framework):
                        count += 1
                except Exception as e:
                    logger.error(f"Error importing framework {framework_id}: {e}")
            
            logger.info(f"Imported {count} frameworks from {source_file}")
            return count
        except Exception as e:
            logger.error(f"Error during framework import: {e}")
            return 0
    
    # === Evaluation Results Management ===
    
    def save_evaluation(self, evaluation: EthicsEvaluationResult) -> bool:
        """Save an evaluation result."""
        try:
            # Ensure the evaluation has an ID
            if not evaluation.evaluation_id:
                evaluation.evaluation_id = f"eval_{uuid.uuid4()}"
            
            # Ensure the evaluation has a timestamp
            if not evaluation.timestamp:
                evaluation.timestamp = datetime.utcnow()
            
            # Save to disk
            file_path = self.evaluations_dir / f"{evaluation.evaluation_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json.dumps instead of model.json() to avoid Pydantic compatibility issues
                json_data = json.dumps(evaluation.dict(), indent=2, default=str)
                f.write(json_data)
            
            logger.info(f"Evaluation {evaluation.evaluation_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving evaluation: {e}")
            return False
    
    def get_evaluation(self, evaluation_id: str) -> Optional[EthicsEvaluationResult]:
        """Get an evaluation result by ID."""
        try:
            file_path = self.evaluations_dir / f"{evaluation_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return EthicsEvaluationResult(**data)
        except Exception as e:
            logger.error(f"Error retrieving evaluation {evaluation_id}: {e}")
            return None
    
    def get_evaluations(self, limit: int = 100, offset: int = 0) -> List[EthicsEvaluationResult]:
        """Get multiple evaluation results with pagination."""
        results = []
        try:
            # List files sorted by modification time (newest first)
            files = sorted(self.evaluations_dir.glob("*.json"), 
                          key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Apply pagination
            paginated_files = files[offset:offset + limit]
            
            # Load each file
            for file_path in paginated_files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        results.append(EthicsEvaluationResult(**data))
                except Exception as e:
                    logger.error(f"Error loading evaluation from {file_path}: {e}")
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving evaluations: {e}")
            return []
    
    # === Explanation Management ===
    
    def save_explanation(self, explanation: EthicsExplanation) -> bool:
        """Save an explanation."""
        try:
            # Ensure the explanation has a timestamp
            if not explanation.timestamp:
                explanation.timestamp = datetime.utcnow()
            
            # Save to disk
            file_path = self.explanations_dir / f"{explanation.evaluation_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json.dumps instead of model.json() to avoid Pydantic compatibility issues
                json_data = json.dumps(explanation.dict(), indent=2, default=str)
                f.write(json_data)
            
            logger.info(f"Explanation for evaluation {explanation.evaluation_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving explanation: {e}")
            return False
    
    def get_explanation(self, evaluation_id: str) -> Optional[EthicsExplanation]:
        """Get an explanation by evaluation ID."""
        try:
            file_path = self.explanations_dir / f"{evaluation_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return EthicsExplanation(**data)
        except Exception as e:
            logger.error(f"Error retrieving explanation for evaluation {evaluation_id}: {e}")
            return None
    
    # === Suggestion Management ===
    
    def save_suggestion(self, suggestion: EthicsSuggestionResponse) -> bool:
        """Save a suggestion response."""
        try:
            # Ensure the suggestion has an ID
            if not suggestion.request_id:
                suggestion.request_id = f"req_{uuid.uuid4()}"
            
            # Ensure the suggestion has a timestamp
            if not suggestion.timestamp:
                suggestion.timestamp = datetime.utcnow()
            
            # Save to disk
            file_path = self.suggestions_dir / f"{suggestion.request_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json.dumps instead of model.json() to avoid Pydantic compatibility issues
                json_data = json.dumps(suggestion.dict(), indent=2, default=str)
                f.write(json_data)
            
            logger.info(f"Suggestion {suggestion.request_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving suggestion: {e}")
            return False
    
    def get_suggestion(self, request_id: str) -> Optional[EthicsSuggestionResponse]:
        """Get a suggestion by request ID."""
        try:
            file_path = self.suggestions_dir / f"{request_id}.json"
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return EthicsSuggestionResponse(**data)
        except Exception as e:
            logger.error(f"Error retrieving suggestion {request_id}: {e}")
            return None
    
    # === Audit Log Management ===
    
    def log_audit_entry(self, entry: AuditLogEntry) -> bool:
        """Add an audit log entry."""
        try:
            # Ensure the entry has an ID
            if not entry.log_id:
                entry.log_id = f"log_{uuid.uuid4()}"
            
            # Ensure the entry has a timestamp
            if not entry.timestamp:
                entry.timestamp = datetime.utcnow()
            
            # Save to disk
            # Use a structure like YYYY-MM/DD/log_id.json for better organization
            date_dir = self.audit_dir / entry.timestamp.strftime("%Y-%m") / entry.timestamp.strftime("%d")
            date_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = date_dir / f"{entry.log_id}.json"
            with open(file_path, 'w', encoding='utf-8') as f:
                # Use json.dumps instead of model.json() to avoid Pydantic compatibility issues
                json_data = json.dumps(entry.dict(), indent=2, default=str)
                f.write(json_data)
            
            logger.debug(f"Audit log entry {entry.log_id} saved successfully")
            return True
        except Exception as e:
            logger.error(f"Error saving audit log entry: {e}")
            return False
    
    def get_audit_logs(self, 
                     start_date: Optional[datetime] = None, 
                     end_date: Optional[datetime] = None,
                     user_id: Optional[str] = None,
                     action_type: Optional[str] = None,
                     limit: int = 100, 
                     offset: int = 0) -> List[AuditLogEntry]:
        """
        Get audit logs with filtering and pagination.
        
        Args:
            start_date: Only include logs after this date
            end_date: Only include logs before this date
            user_id: Filter by user ID
            action_type: Filter by action type
            limit: Maximum number of logs to return
            offset: Number of logs to skip
            
        Returns:
            List of audit log entries matching the filters
        """
        results = []
        try:
            # Set default date range if not provided
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)  # Default to last 30 days
            
            # Collect all log files within the date range
            log_files = []
            current_date = start_date
            while current_date <= end_date:
                date_dir = self.audit_dir / current_date.strftime("%Y-%m") / current_date.strftime("%d")
                if date_dir.exists():
                    log_files.extend(date_dir.glob("*.json"))
                current_date += timedelta(days=1)
            
            # Sort by modification time (newest first)
            log_files = sorted(log_files, key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Load and filter logs
            count = 0
            for file_path in log_files:
                if count >= offset + limit:
                    break
                    
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        entry = AuditLogEntry(**data)
                        
                        # Apply filters
                        if user_id and entry.user_id != user_id:
                            continue
                        if action_type and entry.action_type != action_type:
                            continue
                        
                        # Apply pagination
                        if count >= offset:
                            results.append(entry)
                        
                        count += 1
                except Exception as e:
                    logger.error(f"Error loading audit log from {file_path}: {e}")
            
            return results
        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}")
            return []
    
    # === Utility Methods ===
    
    def backup_data(self, backup_dir: str = "C:/EGOS/ATRiAN/backups") -> bool:
        """
        Create a backup of all EaaS data.
        
        Args:
            backup_dir: Directory where the backup will be stored
            
        Returns:
            True if backup was successful, False otherwise
        """
        try:
            backup_path = Path(backup_dir)
            backup_path.mkdir(parents=True, exist_ok=True)
            
            # Create timestamped backup directory
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_subdir = backup_path / f"eaas_backup_{timestamp}"
            backup_subdir.mkdir()
            
            # Copy all data files
            shutil.copytree(self.data_dir, backup_subdir / "data")
            
            logger.info(f"Created backup at {backup_subdir}")
            return True
        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            return False


# Example usage
if __name__ == "__main__":
    # Configure logging for the example
    logging.basicConfig(level=logging.INFO)
    
    # Create the persistence manager
    persistence = EaasPersistenceManager()
    
    # Import frameworks from initial data
    print(f"Imported {persistence.import_frameworks_from_initial_data()} frameworks from initial data")
    
    # Check the imported frameworks
    frameworks = persistence.get_frameworks()
    print(f"Available frameworks: {len(frameworks)}")
    for framework in frameworks:
        print(f"  - {framework.id}: {framework.name} (v{framework.version})")
        
    print("\nPersistence layer ready for use by EaaS API!")