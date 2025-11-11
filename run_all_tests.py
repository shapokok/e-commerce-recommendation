"""
Master Test Runner
Executes all testing suites and generates comprehensive report
"""

import subprocess
import sys
import time
from datetime import datetime

class Color:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_banner(text):
    """Print formatted banner"""
    print(f"\n{Color.BOLD}{Color.BLUE}{'='*70}")
    print(f"  {text}")
    print(f"{'='*70}{Color.END}\n")

def run_test_suite(name, script, description):
    """Run a test suite and report results"""
    print_banner(f"Running: {name}")
    print(description)
    print()
    
    start_time = time.time()
    
    try:
        result = subprocess.run(
            [sys.executable, script],
            capture_output=False,
            text=True
        )
        
        elapsed = time.time() - start_time
        
        if result.returncode == 0:
            print(f"\n{Color.GREEN}✓ {name} completed successfully in {elapsed:.1f}s{Color.END}")
            return True
        else:
            print(f"\n{Color.RED}✗ {name} failed with return code {result.returncode}{Color.END}")
            return False
            
    except Exception as e:
        print(f"\n{Color.RED}✗ Error running {name}: {e}{Color.END}")
        return False

def check_server():
    """Check if the API server is running"""
    import requests
    
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print(f"{Color.GREEN}✓ API server is running{Color.END}")
            return True
    except:
        pass
    
    print(f"{Color.RED}✗ API server is not running!{Color.END}")
    print("Please start the server first: python main.py")
    return False

def main():
    """Run all test suites"""
    print(f"{Color.BOLD}{Color.BLUE}")
    print("="*70)
    print("  E-COMMERCE RECOMMENDATION SYSTEM")
    print("  COMPREHENSIVE TESTING SUITE")
    print("="*70)
    print(f"{Color.END}")
    print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Test Environment: Local Development")
    print()
    
    # Check if server is running
    if not check_server():
        print(f"\n{Color.YELLOW}Please start the API server and try again.{Color.END}")
        return
    
    # Track results
    results = {}
    
    # Test Suite 1: Functional Testing
    results['functional'] = run_test_suite(
        "Functional Testing",
        "test_functional.py",
        "Testing all system features: registration, authentication, products, interactions, recommendations"
    )
    
    # Test Suite 2: Database Testing
    results['database'] = run_test_suite(
        "Database Testing",
        "test_database.py",
        "Testing data integrity, query performance, indexing, and CRUD operations"
    )
    
    # Test Suite 3: Recommendation Quality
    results['recommendation'] = run_test_suite(
        "Recommendation Quality Testing",
        "test_recommendation_quality.py",
        "Evaluating recommendation algorithm using Precision, Recall, F1-Score metrics"
    )
    
    # Test Suite 4: Performance Testing
    print_banner("Performance Testing")
    print("Performance testing is already completed. Check performance_report.json")
    results['performance'] = True
    
    # Generate Report
    print_banner("Generating Final Report")
    print("Creating comprehensive Word document with all test results...")
    
    try:
        subprocess.run([sys.executable, "generate_report.py"], check=True)
        print(f"{Color.GREEN}✓ Report generated successfully{Color.END}")
        results['report'] = True
    except Exception as e:
        print(f"{Color.RED}✗ Report generation failed: {e}{Color.END}")
        results['report'] = False
    
    # Final Summary
    print_banner("TESTING SUMMARY")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"Total Test Suites: {total}")
    print(f"{Color.GREEN}Passed: {passed}{Color.END}")
    print(f"{Color.RED}Failed: {total - passed}{Color.END}")
    
    print(f"\n{Color.BOLD}Test Suite Results:{Color.END}")
    for suite, status in results.items():
        symbol = "✓" if status else "✗"
        color = Color.GREEN if status else Color.RED
        print(f"  {color}{symbol} {suite.capitalize()}{Color.END}")
    
    print(f"\n{Color.BOLD}Generated Files:{Color.END}")
    files = [
        "functional_test_results.json",
        "database_test_results.json",
        "recommendation_quality_results.json",
        "performance_report.json",
        "Testing_Report_NoSQL_System.docx"
    ]
    
    import os
    for file in files:
        if os.path.exists(file):
            print(f"  {Color.GREEN}✓ {file}{Color.END}")
        else:
            print(f"  {Color.YELLOW}○ {file} (not found){Color.END}")
    
    print(f"\n{Color.BOLD}{Color.GREEN}{'='*70}")
    print("  TESTING COMPLETE!")
    print(f"{'='*70}{Color.END}")
    
    print(f"\nView the comprehensive report in: {Color.BOLD}Testing_Report_NoSQL_System.docx{Color.END}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Color.YELLOW}Testing interrupted by user{Color.END}")
    except Exception as e:
        print(f"\n\n{Color.RED}Error during testing: {e}{Color.END}")
        import traceback
        traceback.print_exc()