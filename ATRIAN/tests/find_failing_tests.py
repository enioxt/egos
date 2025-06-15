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

def run_tests():
    # Create test suite with all tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestWeaverOfTrust)
    
    # Run tests and capture results
    runner = unittest.TextTestRunner(verbosity=0)
    result = runner.run(suite)
    
    # Print information about failures
    print(f"\n===== DETAILED TEST FAILURE INFORMATION =====")
    print(f"Total tests: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\n----- FAILURES -----")
        for i, (test, traceback) in enumerate(result.failures, 1):
            print(f"\n{i}. FAILED TEST: {test.id()}")
            print(f"ERROR: {traceback.split('AssertionError: ')[1] if 'AssertionError: ' in traceback else traceback}")
    
    if result.errors:
        print("\n----- ERRORS -----")
        for i, (test, traceback) in enumerate(result.errors, 1):
            print(f"\n{i}. ERROR TEST: {test.id()}")
            print(f"ERROR: {traceback}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)