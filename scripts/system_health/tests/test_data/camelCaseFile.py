#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test file with camelCase naming to test the naming convention validator.
This file intentionally uses non-compliant naming for testing purposes.

@author: EGOS Development Team
@date: 2025-05-26
@version: 1.0.0
@references: EGOS Naming Convention Standards
"""
# 
# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

def testFunction():
    """Test function with camelCase naming."""
    return "This is a test function"

class testClass:
    """Test class with camelCase naming."""
    
    def __init__(self):
        """Initialize the test class."""
        self.value = "Test value"
    
    def getValue(self):
        """Get the value with camelCase method name."""
        return self.value

if __name__ == "__main__":
    print(testFunction())
    test = testClass()
    print(test.getValue())