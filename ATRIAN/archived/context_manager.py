# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md) (Sections 3.2.1, 4.2)
# - [ATRiAN README](./README.md)
# - [EGOS Global Rules](../.windsurfrules) (Section 3.6 - ATRiAN)
# - [Master Quantum Prompt (MQP.md)](../MQP.md)
# --- 

import logging
from typing import Any, Dict, Optional, Tuple

# Configure basic logging for the module
# In a full EGOS setup, this would integrate with a centralized logging system (CRONOS).
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO) # Default to INFO, can be configured

class ContextManager:
    """
    Manages active and passive contexts within the ATRiAN system.

    The ContextManager is responsible for storing, retrieving, and managing
    various pieces of contextual information that ATRiAN and other EGOS
    components might need. It distinguishes between a single 'active' context
    (e.g., the current primary focus of an operation) and multiple 'passive'
    contexts (e.g., background information, user preferences, system state).

    Attributes:
        active_context (Optional[Tuple[str, Dict[str, Any]]]): 
            The current active context, stored as a tuple of (name, context_data).
            Context_data includes the actual context information and metadata like 'sensitivity'.
        passive_contexts (Dict[str, Dict[str, Any]]):
            A dictionary of passive contexts, where keys are context names and values
            are context_data dictionaries (including metadata).
    """

    def __init__(self):
        """Initializes the ContextManager with no active or passive contexts."""
        self.active_context: Optional[Tuple[str, Dict[str, Any]]] = None
        self.passive_contexts: Dict[str, Dict[str, Any]] = {}
        logger.info("ContextManager initialized.")

    def set_active_context(self, name: str, data: Any, sensitivity: str = 'low', **kwargs) -> None:
        """
        Sets or updates the active context.

        Args:
            name (str): The name of the active context.
            data (Any): The actual data of the context.
            sensitivity (str): The sensitivity level (e.g., 'low', 'medium', 'high_privacy_SP').
                               Defaults to 'low'. This aligns with Sacred Privacy (SP).
            **kwargs: Additional metadata to store with the context.

        Raises:
            TypeError: If 'name' is not a string or 'sensitivity' is not a string.
            ValueError: If 'name' or 'sensitivity' is empty.
        """
        if not isinstance(name, str):
            logger.error("Failed to set active context: name must be a string.")
            raise TypeError("Context name must be a string.")
        if not name.strip():
            logger.error("Failed to set active context: name cannot be empty.")
            raise ValueError("Context name cannot be empty.")
        if not isinstance(sensitivity, str):
            logger.error(f"Failed to set active context '{name}': sensitivity must be a string.")
            raise TypeError("Context sensitivity must be a string.")
        if not sensitivity.strip():
            logger.error(f"Failed to set active context '{name}': sensitivity cannot be empty.")
            raise ValueError("Context sensitivity cannot be empty.")

        context_data = {
            "data": data,
            "sensitivity": sensitivity,
            **kwargs
        }
        # Future: CM-07 Validate context_data against a schema if defined.
        # self.validate_context_schema(context_data)
        
        self.active_context = (name, context_data)
        logger.info(f"Active context '{name}' set with sensitivity '{sensitivity}'.")
        # Future: CM-06 Log this interaction.
        # self.log_interaction('set_active_context', name=name, sensitivity=sensitivity)

    def add_passive_context(self, name: str, data: Any, sensitivity: str = 'low', **kwargs) -> None:
        """
        Adds or updates a passive context.

        Args:
            name (str): The name of the passive context.
            data (Any): The actual data of the context.
            sensitivity (str): The sensitivity level (e.g., 'low', 'medium', 'high_privacy_SP').
                               Defaults to 'low'. This aligns with Sacred Privacy (SP).
            **kwargs: Additional metadata to store with the context.

        Raises:
            TypeError: If 'name' is not a string or 'sensitivity' is not a string.
            ValueError: If 'name' or 'sensitivity' is empty.
        """
        if not isinstance(name, str):
            logger.error("Failed to add passive context: name must be a string.")
            raise TypeError("Context name must be a string.")
        if not name.strip():
            logger.error("Failed to add passive context: name cannot be empty.")
            raise ValueError("Context name cannot be empty.")
        if not isinstance(sensitivity, str):
            logger.error(f"Failed to add passive context '{name}': sensitivity must be a string.")
            raise TypeError("Context sensitivity must be a string.")
        if not sensitivity.strip():
            logger.error(f"Failed to add passive context '{name}': sensitivity cannot be empty.")
            raise ValueError("Context sensitivity cannot be empty.")

        context_data = {
            "data": data,
            "sensitivity": sensitivity,
            **kwargs
        }
        # Future: CM-07 Validate context_data against a schema if defined.
        # self.validate_context_schema(context_data)

        self.passive_contexts[name] = context_data
        logger.info(f"Passive context '{name}' added/updated with sensitivity '{sensitivity}'.")
        # Future: CM-06 Log this interaction.
        # self.log_interaction('add_passive_context', name=name, sensitivity=sensitivity)

    def get_active_context(self) -> Optional[Tuple[str, Dict[str, Any]]]:
        """
        Retrieves the active context.

        Returns:
            Optional[Tuple[str, Dict[str, Any]]]: A tuple (name, context_data) if active context is set,
                                                  otherwise None.
        """
        # Access control checks could be implemented here based on trust layer in a real scenario.
        if self.active_context:
            logger.debug(f"Retrieved active context: {self.active_context[0]}.")
        else:
            logger.debug("No active context set.")
        return self.active_context

    def get_passive_context(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves a specific passive context by name.

        Args:
            name (str): The name of the passive context to retrieve.

        Returns:
            Optional[Dict[str, Any]]: The context_data if found, otherwise None.
        
        Raises:
            TypeError: If 'name' is not a string.
            ValueError: If 'name' is empty.
        """
        if not isinstance(name, str):
            logger.error("Failed to get passive context: name must be a string.")
            raise TypeError("Context name must be a string.")
        if not name.strip():
            logger.error("Failed to get passive context: name cannot be empty.")
            raise ValueError("Context name cannot be empty.")

        context = self.passive_contexts.get(name)
        if context:
            logger.debug(f"Retrieved passive context: {name}.")
        else:
            logger.warning(f"Passive context '{name}' not found.")
        return context

    def get_all_passive_contexts(self) -> Dict[str, Dict[str, Any]]:
        """
        Retrieves all passive contexts.

        Returns:
            Dict[str, Dict[str, Any]]: A dictionary of all passive contexts.
        """
        logger.debug("Retrieved all passive contexts.")
        return self.passive_contexts.copy() # Return a copy to prevent direct modification

    def remove_passive_context(self, name: str) -> bool:
        """
        Removes a specific passive context by name.

        Args:
            name (str): The name of the passive context to remove.

        Returns:
            bool: True if the context was found and removed, False otherwise.
        
        Raises:
            TypeError: If 'name' is not a string.
            ValueError: If 'name' is empty.
        """
        if not isinstance(name, str):
            logger.error("Failed to remove passive context: name must be a string.")
            raise TypeError("Context name must be a string.")
        if not name.strip():
            logger.error("Failed to remove passive context: name cannot be empty.")
            raise ValueError("Context name cannot be empty.")

        if name in self.passive_contexts:
            del self.passive_contexts[name]
            logger.info(f"Passive context '{name}' removed.")
            # Future: CM-06 Log this interaction.
            # self.log_interaction('remove_passive_context', name=name)
            return True
        logger.warning(f"Attempted to remove non-existent passive context '{name}'.")
        return False

    def clear_active_context(self) -> None:
        """
        Clears the active context.
        """
        if self.active_context:
            logger.info(f"Active context '{self.active_context[0]}' cleared.")
            # Future: CM-06 Log this interaction.
            # self.log_interaction('clear_active_context', name=self.active_context[0])
            self.active_context = None
        else:
            logger.info("No active context to clear.")

    def clear_all_passive_contexts(self) -> None:
        """
        Clears all passive contexts.
        """
        count = len(self.passive_contexts)
        self.passive_contexts.clear()
        logger.info(f"All {count} passive contexts cleared.")
        # Future: CM-06 Log this interaction.
        # self.log_interaction('clear_all_passive_contexts', count=count)

    def clear_all_contexts(self) -> None:
        """
        Clears both the active context and all passive contexts.
        """
        self.clear_active_context()
        self.clear_all_passive_contexts()
        logger.info("All active and passive contexts cleared.")

    # --- Placeholder methods for future implementation (CM-06, CM-07) ---
    def log_interaction(self, method_name: str, **kwargs) -> None:
        """
        (Placeholder) Logs significant interactions with the ContextManager.
        This method is intended to integrate with a centralized EGOS logging system (CRONOS).

        Args:
            method_name (str): The name of the method that was called.
            **kwargs: Additional details about the interaction.
        """
        # In a real implementation, this would format and send log data
        # to the EGOS CRONOS logging service.
        log_details = {**{"interaction_method": method_name}, **kwargs}
        logger.debug(f"[Future Log - CRONOS] ContextManager interaction: {log_details}")
        # EGOS_PRINCIPLE:Systemic_Cartography - Logging interactions aids in understanding system flow.
        # EGOS_PRINCIPLE:Evolutionary_Preservation - Logs serve as records for future analysis.

    def validate_context_schema(self, context_data: Dict[str, Any]) -> bool:
        """
        (Placeholder) Validates the structure of context_data against a predefined schema.
        This ensures consistency and integrity of contextual information.

        Args:
            context_data (Dict[str, Any]): The context data dictionary to validate.

        Returns:
            bool: True if the data conforms to the schema, False otherwise.
                  (Currently always returns True as it's a placeholder).
        
        Raises:
            NotImplementedError: If called directly before full implementation.
        """
        # In a real implementation, this would use a schema validation library (e.g., JSONSchema)
        # to check context_data against a defined structure for different context types.
        # EGOS_PRINCIPLE:Systemic_Organization - Ensuring data conforms to schemas.
        logger.debug(f"[Future Validation] Schema validation for context: {context_data.get('name', 'Unnamed')}. Currently a NOP.")
        # raise NotImplementedError("validate_context_schema is not yet fully implemented.")
        return True # Placeholder behavior

if __name__ == '__main__':
    # Example Usage & Basic Test
    # This section demonstrates how to use the ContextManager and can serve as a basic sanity check.
    # For comprehensive testing, refer to test_context_manager.py
    
    print("--- ContextManager Example Usage ---")
    manager = ContextManager()

    # Set active context
    try:
        manager.set_active_context("user_session_001", {"user_id": "Alice", "session_start": "2024-05-27T10:00:00Z"}, sensitivity="medium_privacy_SP", source="user_login")
        active_ctx = manager.get_active_context()
        if active_ctx:
            print(f"Active Context: {active_ctx[0]} - Data: {active_ctx[1]['data']}, Sensitivity: {active_ctx[1]['sensitivity']}")
    except (TypeError, ValueError) as e:
        print(f"Error setting active context: {e}")

    # Add passive contexts
    try:
        manager.add_passive_context("system_config", {"version": "1.2.3", "feature_flags": ["A", "B"]}, sensitivity="low", component="core_system")
        manager.add_passive_context("user_preferences_Alice", {"theme": "dark", "notifications": "enabled"}, sensitivity="high_privacy_SP", user_id="Alice")
    except (TypeError, ValueError) as e:
        print(f"Error adding passive context: {e}")

    # Get a passive context
    sys_config = manager.get_passive_context("system_config")
    if sys_config:
        print(f"System Config (Passive): Data: {sys_config['data']}, Sensitivity: {sys_config['sensitivity']}")

    # Get all passive contexts
    all_passive = manager.get_all_passive_contexts()
    print(f"All Passive Contexts ({len(all_passive)}):")
    for name, ctx in all_passive.items():
        print(f"  - {name}: Sensitivity: {ctx['sensitivity']}, Data: {ctx['data']}")

    # Example of error handling
    print("\n--- Testing Error Handling ---")
    try:
        manager.set_active_context("", {"data": "empty name test"}) # Empty name
    except ValueError as e:
        print(f"Caught expected error: {e}")
    try:
        manager.add_passive_context("test_type_error", {}, sensitivity=123) # Wrong type for sensitivity
    except TypeError as e:
        print(f"Caught expected error: {e}")

    # Clear contexts
    manager.clear_all_contexts()
    print(f"\nActive context after clearing: {manager.get_active_context()}")
    print(f"Passive contexts after clearing: {manager.get_all_passive_contexts()}")

    print("--- ContextManager Example Usage Complete ---")