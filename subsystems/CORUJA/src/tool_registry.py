# c:\EGOS\subsystems\CORUJA\src\tool_registry.py
import logging
from typing import Any, Callable, Dict, List, Optional

# Attempt to import KoiosLogger, fallback to standard logging
try:
    # Assuming KoiosLogger is available in this structure
    from koios_utils.log import KoiosLogger
    logger = KoiosLogger(__name__)
except ImportError:
    logger = logging.getLogger(__name__)
    if not logger.hasHandlers():
        logging.basicConfig(level=logging.INFO)
    logger.warning("KoiosLogger not found, falling back to standard logging.")


class ToolRegistryError(Exception):
    """Custom exception for ToolRegistry errors."""
    pass

class ToolRegistry:
    """
    Manages tool definitions, registration, and invocation.

    - Stores tool definitions (e.g., name, description, callable function).
    - Allows registration of new tools.
    - Provides methods to list and retrieve tool details.
    - Handles tool invocation and error handling.
    - Logs actions and errors.
    """

    def __init__(self):
        """Initializes the ToolRegistry with an empty tool store."""
        self._tools: Dict[str, Dict[str, Any]] = {}
        logger.info("ToolRegistry initialized.")

    def register_tool(
        self,
        name: str,
        callable_func: Callable[..., Any],
        description: str,
        parameters: Optional[Dict[str, Any]] = None,
        overwrite: bool = False, # Added option to overwrite
    ) -> None:
        """
        Registers a new tool.

        Args:
            name: The unique name of the tool.
            callable_func: The Python function to execute for this tool.
            description: A description of what the tool does.
            parameters: Optional dictionary describing the tool's parameters
                        (e.g., JSON schema for validation).
            overwrite: If True, allows overwriting an existing tool registration.

        Raises:
            ToolRegistryError: If a tool with the same name already exists and
                               overwrite is False, or if callable_func is invalid.
        """
        if name in self._tools and not overwrite:
            msg = f"Tool '{name}' already registered. Set overwrite=True to replace."
            logger.error(msg)
            raise ToolRegistryError(msg)

        if not callable(callable_func):
             msg = f"Provided 'callable_func' for tool '{name}' is not callable."
             logger.error(msg)
             raise ToolRegistryError(msg)

        self._tools[name] = {
            "callable": callable_func,
            "description": description,
            "parameters": parameters or {}, # Store schema for potential future validation
        }
        log_action = "Overwrote" if name in self._tools and overwrite else "Registered"
        logger.info(f"{log_action} tool: {name}")

    def get_tool_definition(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieves the full definition (including callable) of a tool."""
        tool_details = self._tools.get(name)
        # Avoid logging the callable directly
        if tool_details:
             logger.debug(f"Retrieved tool definition for: {name}")
        else:
             logger.warning(f"Attempted to retrieve definition for non-existent tool: {name}")
        return tool_details

    def get_tool_schema(self, name: str) -> Optional[Dict[str, Any]]:
         """Retrieves the schema (name, description, parameters) of a tool."""
         tool_details = self._tools.get(name)
         if not tool_details:
              logger.warning(f"Attempted to retrieve schema for non-existent tool: {name}")
              return None
         return {
              "name": name,
              "description": tool_details["description"],
              "parameters": tool_details["parameters"],
         }


    def list_tools(self) -> List[Dict[str, Any]]:
        """Returns a list of tool schemas (name, description, parameters)."""
        tool_list = [
            self.get_tool_schema(name)
            for name in self._tools
        ]
        # Filter out None in case of internal inconsistency, though unlikely
        tool_list = [t for t in tool_list if t is not None]
        logger.debug(f"Listed {len(tool_list)} registered tool schemas.")
        return tool_list

    def invoke_tool(self, name: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Invokes a registered tool by name with the given arguments.

        Args:
            name: The name of the tool to invoke.
            **kwargs: Keyword arguments to pass to the tool's callable function.

        Returns:
            A dictionary containing the tool's output or an error.
            Example success: {'status': 'success', 'result': tool_output}
            Example error: {'status': 'error', 'message': 'error details'}
        """
        tool_details = self.get_tool_definition(name)
        if not tool_details:
            msg = f"Tool '{name}' not found for invocation."
            logger.error(msg)
            return {"status": "error", "message": msg}

        callable_func = tool_details["callable"]
        logger.info(f"Invoking tool: {name}")
        # TODO: Add parameter validation against tool_details["parameters"] schema here
        # For now, just log the keys passed
        logger.debug(f"Tool '{name}' called with argument keys: {list(kwargs.keys())}")

        try:
            result = callable_func(**kwargs)
            logger.info(f"Tool '{name}' executed successfully.")
            # Consider limiting result logging based on size/sensitivity
            # logger.debug(f"Tool '{name}' raw result type: {type(result)}")
            return {"status": "success", "result": result}
        except Exception as e:
            # Catching broad Exception, specific tools might raise custom errors
            msg = f"Error during invocation of tool '{name}': {e.__class__.__name__}: {e}"
            logger.exception(f"Exception invoking tool '{name}':") # Log full traceback
            return {"status": "error", "message": msg}

    def unregister_tool(self, name: str) -> bool:
         """Removes a tool registration. Returns True if successful, False otherwise."""
         if name in self._tools:
              del self._tools[name]
              logger.info(f"Unregistered tool: {name}")
              return True
         else:
              logger.warning(f"Attempted to unregister non-existent tool: {name}")
              return False