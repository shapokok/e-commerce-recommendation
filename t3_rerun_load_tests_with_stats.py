"""
Re-run load tests to get stats in JSON format
This will generate both HTML reports and JSON stats files
"""

import subprocess
import time
import sys

# Fix encoding for Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

print("=" * 70)
print("  RE-RUNNING LOAD TESTS WITH STATS OUTPUT")
print("=" * 70)

print("\nThis will run 3 load tests:")
print("  - 50 users for 60 seconds")
print("  - 100 users for 60 seconds")
print("  - 500 users for 60 seconds")
print("\nMake sure your FastAPI server is running!")
print()

input("Press Enter to continue...")

test_configs = [
    {
        "users": 50,
        "spawn_rate": 10,
        "report": "report_50_users.html",
        "csv": "stats_50_users",
    },
    {
        "users": 100,
        "spawn_rate": 20,
        "report": "report_100_users.html",
        "csv": "stats_100_users",
    },
    {
        "users": 500,
        "spawn_rate": 50,
        "report": "report_500_users.html",
        "csv": "stats_500_users",
    },
]

for config in test_configs:
    print(f"\n[Test] Running with {config['users']} users...")
    cmd = [
        "locust",
        "-f",
        "t3_locustfile.py",
        "--host=http://127.0.0.1:8000",
        "--users",
        str(config["users"]),
        "--spawn-rate",
        str(config["spawn_rate"]),
        "--run-time",
        "1m",
        "--html",
        config["report"],
        "--csv",
        config["csv"],
        "--headless",
    ]

    try:
        subprocess.run(cmd, timeout=120)
        print(f"  ✓ Test complete!")
        print(f"  ✓ HTML report: {config['report']}")
        print(f"  ✓ CSV stats: {config['csv']}_stats.csv")
    except subprocess.TimeoutExpired:
        print(f"  ✗ Test timed out")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    time.sleep(5)  # Wait between tests

print("\n" + "=" * 70)
print("  ALL TESTS COMPLETE!")
print("=" * 70)
print("\nNow run: python create_clean_reports.py")
print("=" * 70)
