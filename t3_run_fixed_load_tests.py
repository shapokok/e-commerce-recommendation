"""
Automated Re-testing Script
Runs all fixed load tests and generates clean reports
"""

import subprocess
import time
import sys
import os

# Fix encoding for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

print("=" * 70)
print("  AUTOMATED RE-TESTING SCRIPT")
print("  Running fixed load tests...")
print("=" * 70)

# Check if server is running
print("\n[CHECK] Verifying server is running...")
import requests

try:
    response = requests.get("http://127.0.0.1:8000", timeout=5)
    print("✓ Server is running!")
except:
    print("❌ ERROR: Server is not running!")
    print("\nPlease start the server first:")
    print("  python main.py")
    sys.exit(1)

# Test configurations
test_configs = [
    {
        "users": 50,
        "spawn_rate": 10,
        "duration": "60s",
        "report": "Load_Test_Report_50_users_FIXED.html",
        "csv": "stats_50_users_fixed",
    },
    {
        "users": 100,
        "spawn_rate": 20,
        "duration": "60s",
        "report": "Load_Test_Report_100_users_FIXED.html",
        "csv": "stats_100_users_fixed",
    },
    {
        "users": 500,
        "spawn_rate": 50,
        "duration": "60s",
        "report": "Load_Test_Report_500_users_FIXED.html",
        "csv": "stats_500_users_fixed",
    },
]

results_summary = []

for i, config in enumerate(test_configs, 1):
    print(f"\n{'='*70}")
    print(f"  TEST {i}/3: {config['users']} CONCURRENT USERS")
    print(f"{'='*70}")

    cmd = [
        "locust",
        "-f",
        "locustfile_fixed.py",
        "--host",
        "http://127.0.0.1:8000",
        "--users",
        str(config["users"]),
        "--spawn-rate",
        str(config["spawn_rate"]),
        "--run-time",
        config["duration"],
        "--html",
        config["report"],
        "--csv",
        config["csv"],
        "--headless",
    ]

    print(f"\n[RUNNING] locust with {config['users']} users...")
    print(f"  Spawn rate: {config['spawn_rate']} users/sec")
    print(f"  Duration: {config['duration']}")

    try:
        start_time = time.time()
        result = subprocess.run(cmd, timeout=120, capture_output=True, text=True)
        elapsed = time.time() - start_time

        print(f"\n✓ Test completed in {elapsed:.1f} seconds")
        print(f"✓ Report saved: {config['report']}")
        print(f"✓ Stats saved: {config['csv']}_stats.csv")

        # Parse CSV to get failure rate
        try:
            import csv

            csv_file = f"{config['csv']}_stats.csv"
            with open(csv_file, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                if rows:
                    last_row = rows[-1]
                    total_requests = int(
                        last_row.get(
                            "Request Count", last_row.get("# Requests", "0")
                        ).replace('"', "")
                    )
                    failures = int(
                        last_row.get(
                            "Failure Count", last_row.get("# Failures", "0")
                        ).replace('"', "")
                    )

                    if total_requests > 0:
                        failure_rate = (failures / total_requests) * 100
                        print(f"\n📊 Results:")
                        print(f"   Total Requests: {total_requests}")
                        print(f"   Failures: {failures}")
                        print(f"   Failure Rate: {failure_rate:.2f}%")

                        if failure_rate < 5:
                            print(f"   ✅ EXCELLENT: Failure rate under 5%")
                        elif failure_rate < 10:
                            print(f"   ✓ GOOD: Failure rate under 10%")
                        else:
                            print(f"   ⚠ WARNING: Failure rate above 10%")

                        results_summary.append(
                            {
                                "users": config["users"],
                                "total": total_requests,
                                "failures": failures,
                                "rate": failure_rate,
                            }
                        )
        except Exception as e:
            print(f"   ⚠ Could not parse CSV: {e}")

    except subprocess.TimeoutExpired:
        print(f"  ⚠ Test timed out (120s limit)")
    except Exception as e:
        print(f"  ❌ Error: {e}")

    # Wait between tests
    if i < len(test_configs):
        print(f"\n⏳ Waiting 5 seconds before next test...")
        time.sleep(5)

# Final summary
print(f"\n{'='*70}")
print(f"  ALL TESTS COMPLETED!")
print(f"{'='*70}")

if results_summary:
    print(f"\n📊 SUMMARY OF RESULTS:\n")
    print(
        f"{'Users':<10} {'Requests':<12} {'Failures':<12} {'Failure Rate':<15} {'Status':<10}"
    )
    print("-" * 70)

    for result in results_summary:
        status = (
            "✅ EXCELLENT"
            if result["rate"] < 5
            else "✓ GOOD" if result["rate"] < 10 else "⚠ CHECK"
        )
        print(
            f"{result['users']:<10} {result['total']:<12} {result['failures']:<12} {result['rate']:>6.2f}%{'':<8} {status:<10}"
        )

print(f"\n{'='*70}")
print(f"  NEXT STEPS:")
print(f"{'='*70}")
print(f"\n1. Generate final HTML report:")
print(f"   python generate_final_load_report.py")
print(f"\n2. Review individual reports:")
for config in test_configs:
    print(f"   - {config['report']}")
print(f"\n{'='*70}")
