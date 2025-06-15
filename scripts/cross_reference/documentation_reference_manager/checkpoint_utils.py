"""Checkpoint Utilities

Functions for saving, loading, and managing checkpoints during long-running
documentation processing tasks. Supports the Evolutionary Preservation principle
by ensuring work is not lost during interruptions.

This module provides:
- Serialization of complex data structures to JSON
- Checkpoint saving with timestamps
- Checkpoint loading with validation
- Cleanup of old checkpoint files

@references: 
- C:\EGOS\docs_egos\03_processes\script_management\script_management_best_practices.md"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

import json
import logging
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

# Configure module logger
logger = logging.getLogger(__name__)


def _convert_to_serializable(obj: Any) -> Any:
    """Convert an object to a JSON-serializable format.
    
    Handles sets, dictionaries, lists, Path objects, and custom objects
    by recursively converting them to serializable types.
    
    Args:
        obj: The object to convert.
        
    Returns:
        A JSON-serializable representation of the object.
    """
    try:
        if isinstance(obj, set):
            return list(obj)
        elif isinstance(obj, dict):
            return {k: _convert_to_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [_convert_to_serializable(item) for item in obj]
        elif isinstance(obj, Path):
            return str(obj)  # Convert Path objects to strings
        elif hasattr(obj, '__dict__'):  # Handle custom objects by their __dict__
            return _convert_to_serializable(obj.__dict__)
        else:
            # Attempt to serialize directly to catch non-serializable types early
            json.dumps(obj)
            return obj
    except TypeError as e:
        logger.warning(f"Type conversion error for {type(obj)}: {str(e)}. Using str() representation.")
        return str(obj)
    except Exception as e:
        logger.warning(f"Unexpected serialization error for {type(obj)}: {str(e)}. Using str() representation.")
        return str(obj)


def save_checkpoint(stage: str, data: Any, base_path: str) -> Optional[str]:
    """Save a checkpoint to disk.
    
    Creates a timestamped JSON checkpoint file for the given processing stage.
    
    Args:
        stage: Current processing stage (e.g., 'scan', 'extract').
        data: Data to save.
        base_path: Base path of the project.
        
    Returns:
        Path to the saved checkpoint file, or None if saving failed.
    """
    checkpoint_dir = Path(base_path) / "reports" / "documentation" / "checkpoints"
    try:
        checkpoint_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        logger.error(f"Error creating checkpoint directory {checkpoint_dir}: {e}")
        return None

    # Create timestamped checkpoint file
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    checkpoint_file = checkpoint_dir / f"{stage}_checkpoint_{timestamp}.json"
    
    # Also maintain a "latest" checkpoint file
    latest_checkpoint_file = checkpoint_dir / f"{stage}_checkpoint_latest.json"
    
    serializable_data = {
        "timestamp": timestamp,
        "stage": stage,
        "data": _convert_to_serializable(data)
    }

    try:
        # Write the timestamped checkpoint
        with open(checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2)
            
        # Also write to the "latest" checkpoint file
        with open(latest_checkpoint_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_data, f, indent=2)
            
        logger.info(f"Checkpoint saved for stage '{stage}' at {checkpoint_file}")
        
        # Clean up old checkpoints
        clean_old_checkpoints(stage, str(checkpoint_dir))
        
        return str(checkpoint_file)
    except Exception as e:
        logger.error(f"Error saving checkpoint for stage '{stage}': {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def clean_old_checkpoints(stage: str, checkpoint_dir_path: str, keep: int = 5) -> None:
    """Clean up old checkpoint files for a specific stage.
    
    Keeps the most recent checkpoints and removes older ones to prevent
    excessive disk usage.
    
    Args:
        stage: The stage to clean checkpoints for (e.g., 'scan').
        checkpoint_dir_path: Directory containing checkpoints.
        keep: Number of recent checkpoints to keep.
    """
    try:
        checkpoint_dir = Path(checkpoint_dir_path)
        if not checkpoint_dir.exists():
            return
            
        # Find all timestamped checkpoints for this stage
        checkpoints = list(checkpoint_dir.glob(f"{stage}_checkpoint_*.json"))
        
        # Filter out the "latest" checkpoint file
        checkpoints = [cp for cp in checkpoints if not cp.name.endswith("_latest.json")]
        
        # Sort by modification time (newest first)
        checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        
        # Remove old checkpoints beyond the keep limit
        if len(checkpoints) > keep:
            for old_checkpoint in checkpoints[keep:]:
                try:
                    old_checkpoint.unlink()
                    logger.debug(f"Deleted old checkpoint: {old_checkpoint}")
                except Exception as e:
                    logger.warning(f"Failed to delete old checkpoint {old_checkpoint}: {e}")
    except Exception as e:
        logger.warning(f"Error cleaning old checkpoints for stage '{stage}': {e}")


def load_checkpoint(stage: str, base_path: str) -> Optional[Any]:
    """Load the most recent checkpoint for a given stage.
    
    Args:
        stage: Processing stage to load (e.g., 'scan', 'extract').
        base_path: Base path of the project.
        
    Returns:
        Loaded data or None if checkpoint doesn't exist or is invalid.
    """
    checkpoint_dir = Path(base_path) / "reports" / "documentation" / "checkpoints"
    
    # First try to load the "latest" checkpoint
    latest_checkpoint_file = checkpoint_dir / f"{stage}_checkpoint_latest.json"
    
    if not latest_checkpoint_file.exists():
        logger.info(f"No checkpoint found for stage '{stage}' at {latest_checkpoint_file}")
        
        # As a fallback, try to find the most recent timestamped checkpoint
        try:
            checkpoints = list(checkpoint_dir.glob(f"{stage}_checkpoint_*.json"))
            checkpoints = [cp for cp in checkpoints if not cp.name.endswith("_latest.json")]
            
            if not checkpoints:
                logger.info(f"No timestamped checkpoints found for stage '{stage}'")
                return None
                
            # Sort by modification time (newest first)
            checkpoints.sort(key=lambda p: p.stat().st_mtime, reverse=True)
            latest_checkpoint_file = checkpoints[0]
        except Exception as e:
            logger.error(f"Error finding timestamped checkpoints: {e}")
            return None

    try:
        with open(latest_checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        # Validate the checkpoint data
        if not isinstance(checkpoint_data, dict) or "stage" not in checkpoint_data or "data" not in checkpoint_data:
            logger.error(f"Invalid checkpoint format in {latest_checkpoint_file}")
            return None
            
        if checkpoint_data["stage"] != stage:
            logger.warning(
                f"Stage mismatch in checkpoint file {latest_checkpoint_file}. "
                f"Expected '{stage}', found '{checkpoint_data.get('stage')}'."
            )
            return None
            
        logger.info(f"Successfully loaded checkpoint for stage '{stage}' from {latest_checkpoint_file}")
        return checkpoint_data["data"]
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON from checkpoint file {latest_checkpoint_file}: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading checkpoint for stage '{stage}': {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None