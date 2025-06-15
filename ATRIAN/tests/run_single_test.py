# @references:
#   - .windsurfrules
#   - CODE_OF_CONDUCT.md
#   - MQP.md
#   - README.md
#   - ROADMAP.md
#   - CROSSREF_STANDARD.md

# 
import unittest
import sys
from test_atrian_trust_weaver import TestWeaverOfTrust

def run_single_test(test_name):
    # Create a test suite with just the specified test
    suite = unittest.TestSuite()
    suite.addTest(TestWeaverOfTrust(test_name))
    
    # Run the test and capture results
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python run_single_test.py <test_method_name>")
        sys.exit(1)
    
    test_name = sys.argv[1]
    success = run_single_test(test_name)
    sys.exit(0 if success else 1)