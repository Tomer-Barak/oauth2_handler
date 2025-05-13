#!/usr/bin/env python
"""
Run tests for OAuth2 Handler package
"""
import sys
import unittest
import pytest

def run_tests():
    """Run tests using unittest"""
    print("Running basic tests...")
    tests = unittest.defaultTestLoader.discover("tests")
    result = unittest.TextTestRunner().run(tests)
    return result.wasSuccessful()

def run_pytest():
    """Run tests using pytest if available"""
    try:
        import pytest
        print("\nRunning tests with pytest...")
        return pytest.main(["tests", "-v"])
    except ImportError:
        print("Pytest not available, skipping advanced tests")
        return True

if __name__ == "__main__":
    success = run_tests()
    if success:
        success = run_pytest() == 0
    sys.exit(0 if success else 1)
