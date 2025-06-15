# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# - [ATRiAN Context Manager](./context_manager.py)
# - [ATRiAN Implementation Plan](./ATRiAN_Implementation_Plan.md) (Sections 3.2.6, 6.1.1)
# - [ATRiAN README](./README.md)
# - [EGOS Global Rules](../.windsurfrules)
# --- 

import unittest
from context_manager import ContextManager # Assuming context_manager.py is in the same directory or PYTHONPATH

class TestContextManager(unittest.TestCase):
    """Test suite for the ContextManager class."""

    def setUp(self):
        """Set up a new ContextManager instance before each test."""
        self.manager = ContextManager()

    def test_initialization(self):
        """Test that the ContextManager initializes with empty contexts."""
        self.assertIsNone(self.manager.get_active_context(), "Active context should be None initially.")
        self.assertEqual(self.manager.get_all_passive_contexts(), {}, "Passive contexts should be empty initially.")

    def test_set_and_get_active_context(self):
        """Test setting and retrieving the active context with metadata."""
        test_data = {"id": 1, "value": "test_active"}
        self.manager.set_active_context("active_test", test_data, sensitivity="high_privacy_SP", source="test_case")
        active_ctx_tuple = self.manager.get_active_context()
        self.assertIsNotNone(active_ctx_tuple, "Active context should be set.")
        name, context_data = active_ctx_tuple
        self.assertEqual(name, "active_test")
        self.assertEqual(context_data["data"], test_data)
        self.assertEqual(context_data["sensitivity"], "high_privacy_SP")
        self.assertEqual(context_data["source"], "test_case")

    def test_add_and_get_passive_context(self):
        """Test adding and retrieving a passive context with metadata."""
        test_data = {"id": 2, "value": "test_passive"}
        self.manager.add_passive_context("passive_test_1", test_data, sensitivity="medium", component="module_X")
        passive_ctx = self.manager.get_passive_context("passive_test_1")
        self.assertIsNotNone(passive_ctx, "Passive context should be retrievable.")
        self.assertEqual(passive_ctx["data"], test_data)
        self.assertEqual(passive_ctx["sensitivity"], "medium")
        self.assertEqual(passive_ctx["component"], "module_X")

    def test_get_non_existent_passive_context(self):
        """Test retrieving a non-existent passive context returns None."""
        self.assertIsNone(self.manager.get_passive_context("non_existent_ctx"))

    def test_get_all_passive_contexts(self):
        """Test retrieving all passive contexts."""
        self.manager.add_passive_context("p1", {"data": "d1"}, sensitivity="low")
        self.manager.add_passive_context("p2", {"data": "d2"}, sensitivity="high")
        all_passive = self.manager.get_all_passive_contexts()
        self.assertEqual(len(all_passive), 2)
        self.assertIn("p1", all_passive)
        self.assertIn("p2", all_passive)

    def test_remove_passive_context(self):
        """Test removing a passive context."""
        self.manager.add_passive_context("to_remove", {"data": "removable"})
        self.assertTrue(self.manager.remove_passive_context("to_remove"), "Should return True on successful removal.")
        self.assertIsNone(self.manager.get_passive_context("to_remove"), "Context should be gone after removal.")
        self.assertFalse(self.manager.remove_passive_context("not_there"), "Should return False for non-existent context.")

    def test_clear_active_context(self):
        """Test clearing the active context."""
        self.manager.set_active_context("temp_active", {"data": "temp"})
        self.manager.clear_active_context()
        self.assertIsNone(self.manager.get_active_context(), "Active context should be None after clearing.")

    def test_clear_all_passive_contexts(self):
        """Test clearing all passive contexts."""
        self.manager.add_passive_context("p1", {"data": "d1"})
        self.manager.add_passive_context("p2", {"data": "d2"})
        self.manager.clear_all_passive_contexts()
        self.assertEqual(self.manager.get_all_passive_contexts(), {}, "Passive contexts should be empty after clearing.")

    def test_clear_all_contexts(self):
        """Test clearing all (active and passive) contexts."""
        self.manager.set_active_context("active_temp", {"data": "active_data"})
        self.manager.add_passive_context("passive_temp", {"data": "passive_data"})
        self.manager.clear_all_contexts()
        self.assertIsNone(self.manager.get_active_context())
        self.assertEqual(self.manager.get_all_passive_contexts(), {})

    def test_set_active_context_input_validation(self):
        """Test input validation for set_active_context."""
        with self.assertRaisesRegex(TypeError, "Context name must be a string"): 
            self.manager.set_active_context(123, {"data": "d"})
        with self.assertRaisesRegex(ValueError, "Context name cannot be empty"): 
            self.manager.set_active_context("", {"data": "d"})
        with self.assertRaisesRegex(ValueError, "Context name cannot be empty"): 
            self.manager.set_active_context("   ", {"data": "d"})
        with self.assertRaisesRegex(TypeError, "Context sensitivity must be a string"): 
            self.manager.set_active_context("name", {"data": "d"}, sensitivity=123)
        with self.assertRaisesRegex(ValueError, "Context sensitivity cannot be empty"): 
            self.manager.set_active_context("name", {"data": "d"}, sensitivity="")
        with self.assertRaisesRegex(ValueError, "Context sensitivity cannot be empty"): 
            self.manager.set_active_context("name", {"data": "d"}, sensitivity="  ")

    def test_add_passive_context_input_validation(self):
        """Test input validation for add_passive_context."""
        with self.assertRaisesRegex(TypeError, "Context name must be a string"): 
            self.manager.add_passive_context(123, {"data": "d"})
        with self.assertRaisesRegex(ValueError, "Context name cannot be empty"): 
            self.manager.add_passive_context("", {"data": "d"})
        with self.assertRaisesRegex(TypeError, "Context sensitivity must be a string"): 
            self.manager.add_passive_context("name", {"data": "d"}, sensitivity=123)
        with self.assertRaisesRegex(ValueError, "Context sensitivity cannot be empty"): 
            self.manager.add_passive_context("name", {"data": "d"}, sensitivity="")

    def test_get_passive_context_input_validation(self):
        """Test input validation for get_passive_context."""
        with self.assertRaisesRegex(TypeError, "Context name must be a string"): 
            self.manager.get_passive_context(123)
        with self.assertRaisesRegex(ValueError, "Context name cannot be empty"): 
            self.manager.get_passive_context("")

    def test_remove_passive_context_input_validation(self):
        """Test input validation for remove_passive_context."""
        with self.assertRaisesRegex(TypeError, "Context name must be a string"): 
            self.manager.remove_passive_context(123)
        with self.assertRaisesRegex(ValueError, "Context name cannot be empty"): 
            self.manager.remove_passive_context("")

if __name__ == '__main__':
    unittest.main()