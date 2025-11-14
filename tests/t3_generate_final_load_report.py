"""
Generate Final Load Testing Report
Combines all fixed test results into one beautiful HTML report
"""

import csv
import json
from datetime import datetime
import sys
import os

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except:
        pass

print("=" * 70)
print("  GENERATING FINAL LOAD TESTING REPORT")
print("=" * 70)

# Parse CSV files
test_results = []
csv_files = [
    ("stats_50_users_fixed_stats.csv", 50),
    ("stats_100_users_fixed_stats.csv", 100),
    ("stats_500_users_fixed_stats.csv", 500),
]

for csv_file, users in csv_files:
    if not os.path.exists(csv_file):
        print(f"⚠ Warning: {csv_file} not found, skipping...")
        continue

    print(f"✓ Parsing {csv_file}...")

    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

            if rows:
                # Get aggregated row (last row)
                agg = rows[-1]

                total_requests = int(
                    agg.get("Request Count", agg.get("# Requests", "0")).replace(
                        '"', ""
                    )
                )
                failures = int(
                    agg.get("Failure Count", agg.get("# Failures", "0")).replace(
                        '"', ""
                    )
                )

                # Get avg response time
                try:
                    avg_time = float(
                        agg.get(
                            "Average Response Time",
                            agg.get("Median Response Time", "0"),
                        )
                    )
                except:
                    avg_time = 0.0

                # Get RPS
                try:
                    rps = float(agg.get("Requests/s", agg.get("RPS", "0")))
                except:
                    rps = 0.0

                failure_rate = (
                    (failures / total_requests * 100) if total_requests > 0 else 0
                )

                test_results.append(
                    {
                        "users": users,
                        "total_requests": total_requests,
                        "failures": failures,
                        "failure_rate": failure_rate,
                        "avg_response_time": avg_time,
                        "rps": rps,
                    }
                )

                print(f"   Total Requests: {total_requests}")
                print(f"   Failures: {failures} ({failure_rate:.2f}%)")
                print(f"   Avg Response Time: {avg_time:.2f}ms")
                print(f"   RPS: {rps:.2f}")

    except Exception as e:
        print(f"❌ Error parsing {csv_file}: {e}")

if not test_results:
    print("\n❌ No test results found!")
    print("\nPlease run the tests first:")
    print("  python run_fixed_load_tests.py")
    sys.exit(1)

print(f"\n✓ Successfully parsed {len(test_results)} test results")

# Generate HTML report
html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Load Testing Results - E-Commerce API (FIXED)</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            color: #333;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}

        .header {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
            text-align: center;
        }}

        .header h1 {{
            color: #667eea;
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header .badge {{
            display: inline-block;
            background: #10b981;
            color: white;
            padding: 8px 20px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 10px;
        }}

        .header p {{
            color: #666;
            font-size: 1.1em;
            margin-top: 10px;
        }}

        .card {{
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            margin-bottom: 30px;
        }}

        .card h2 {{
            color: #667eea;
            margin-bottom: 20px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .stat-box {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}

        .stat-box .label {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
        }}

        .stat-box .value {{
            font-size: 2em;
            font-weight: bold;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}

        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}

        th {{
            background: #667eea;
            color: white;
            font-weight: 600;
        }}

        tr:hover {{
            background: #f5f5f5;
        }}

        .success {{
            color: #10b981;
            font-weight: bold;
        }}

        .warning {{
            color: #f59e0b;
            font-weight: bold;
        }}

        .excellent {{
            background: #10b981;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
        }}

        .good {{
            background: #3b82f6;
            color: white;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.9em;
            font-weight: bold;
            display: inline-block;
        }}

        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            padding: 20px;
        }}

        .improvement-box {{
            background: #f0fdf4;
            border-left: 4px solid #10b981;
            padding: 20px;
            margin: 20px 0;
            border-radius: 5px;
        }}

        .improvement-box h3 {{
            color: #10b981;
            margin-bottom: 10px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Load Testing Results</h1>
            <div class="badge">✅ FIXED VERSION</div>
            <p>E-Commerce Recommendation System API</p>
            <p style="color: #999; margin-top: 10px;">Generated: {datetime}</p>
        </div>

        <div class="card">
            <h2>Test Overview</h2>
            <p><strong>Objective:</strong> Evaluate system performance under different load conditions</p>
            <p><strong>Test Configuration:</strong></p>
            <ul style="margin-left: 20px; margin-top: 10px; line-height: 1.8;">
                <li>Test Scenarios: 50, 100, and 500 concurrent users</li>
                <li>Test Duration: 60 seconds per scenario</li>
                <li>Target: http://127.0.0.1:8000 (Local MongoDB)</li>
                <li>Tool: Locust Load Testing Framework (Fixed Version)</li>
            </ul>
        </div>

        {test_results_html}

        <div class="card">
            <h2>Performance Comparison</h2>
            <table>
                <thead>
                    <tr>
                        <th>Users</th>
                        <th>Total Requests</th>
                        <th>Requests/sec</th>
                        <th>Avg Response Time</th>
                        <th>Failures</th>
                        <th>Failure Rate</th>
                        <th>Rating</th>
                    </tr>
                </thead>
                <tbody>
                    {comparison_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>Final Assignment: Testing NoSQL-Based Systems</p>
            <p>Load Testing Results - 20 Points</p>
        </div>
    </div>
</body>
</html>
"""


# Generate test results HTML
test_results_html = ""
comparison_rows = ""

for result in test_results:
    users = result["users"]

    test_results_html += f"""
        <div class="card">
            <h2>Test Scenario: {users} Concurrent Users</h2>
            <div class="stats-grid">
                <div class="stat-box">
                    <div class="label">Total Requests</div>
                    <div class="value">{result['total_requests']}</div>
                </div>
                <div class="stat-box">
                    <div class="label">Requests/sec</div>
                    <div class="value">{result['rps']:.2f}</div>
                </div>
                <div class="stat-box">
                    <div class="label">Avg Response</div>
                    <div class="value">{result['avg_response_time']:.2f} ms</div>
                </div>
                <div class="stat-box">
                    <div class="label">Failures</div>
                    <div class="value">{result['failures']}</div>
                </div>
                <div class="stat-box">
                    <div class="label">Failure Rate</div>
                    <div class="value">{result['failure_rate']:.2f}%</div>
                </div>
            </div>
        </div>
    """

    # Determine rating
    if result["failure_rate"] < 5:
        rating = '<span class="excellent">Excellent</span>'
    elif result["failure_rate"] < 10:
        rating = '<span class="good">Good</span>'
    else:
        rating = '<span class="warning">Needs Improvement</span>'

    comparison_rows += f"""
                    <tr>
                        <td>{users}</td>
                        <td>{result['total_requests']}</td>
                        <td>{result['rps']:.2f}</td>
                        <td>{result['avg_response_time']:.2f} ms</td>
                        <td>{result['failures']}</td>
                        <td><span class="{'success' if result['failure_rate'] < 5 else 'warning'}">{result['failure_rate']:.2f}%</span></td>
                        <td>{rating}</td>
                    </tr>
    """

# Fill in template
html_content = html_template.format(
    datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    test_results_html=test_results_html,
    comparison_rows=comparison_rows,
)

# Save report
output_file = "Load_Testing_Report_FINAL.html"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"\n{'='*70}")
print(f"  SUCCESS!")
print(f"{'='*70}")
print(f"\n✅ Final report generated: {output_file}")
print(f"\nOpen in browser to view the report!")
print(f"{'='*70}")
