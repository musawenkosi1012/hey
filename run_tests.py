#!/usr/bin/env python3
"""
Automated Test Runner for ChroniSense
Runs all 10 test scenarios and generates a comprehensive report
"""
import subprocess
import sys
import json
from datetime import datetime


def run_tests():
    """Run all tests and collect results"""
    print("=" * 70)
    print("ChroniSense Automated Test Suite")
    print("=" * 70)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Run pytest with verbose output
    cmd = [
        sys.executable, '-m', 'pytest',
        'tests/',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        # Parse results
        output = result.stdout
        
        # Extract test counts
        if 'passed' in output:
            print("\n" + "=" * 70)
            print("Test Execution Summary")
            print("=" * 70)
            
            # Find summary line
            for line in output.split('\n'):
                if 'passed' in line or 'failed' in line:
                    if '=' in line:
                        print(line.split('=')[-1].strip())
        
        print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)
        
        return result.returncode
        
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1


def main():
    """Main entry point"""
    print("\n🧪 Starting comprehensive test suite...\n")
    
    # Check if pytest is installed
    try:
        import pytest
    except ImportError:
        print("❌ pytest not installed. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pytest', 'pytest-flask'])
    
    # Run tests
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  Some tests failed. Exit code: {exit_code}")
    
    print("\n📊 For detailed results, see TESTING_REPORT.md\n")
    
    return exit_code


if __name__ == '__main__':
    sys.exit(main())
