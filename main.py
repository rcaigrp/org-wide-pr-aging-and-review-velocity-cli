import argparse
import os
import sys
from monitor import fetch_org_data
from report import render_report

def main():
    parser = argparse.ArgumentParser(description="Org-Wide PR Aging & Review Velocity CLI")
    parser.add_argument("--org", required=True, help="GitHub organization name")
    parser.add_argument("--min-days-stale", type=int, default=14, help="Minimum days to consider PR stale")
    parser.add_argument("--output-format", choices=["table", "csv"], default="table", help="Output format")
    args = parser.parse_args()

    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print("Error: GITHUB_TOKEN environment variable is not set.")
        sys.exit(1)

    try:
        pr_data = fetch_org_data(args.org, token, args.min_days_stale)
    except Exception as e:
        print(f"Error fetching data: {e}")
        sys.exit(1)

    render_report(pr_data, args.output_format)

if __name__ == "__main__":
    main()
