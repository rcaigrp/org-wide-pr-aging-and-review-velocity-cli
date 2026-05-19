# Org-Wide PR Aging & Review Velocity CLI

A Python CLI tool that tracks PR age, review activity, and tech debt across a GitHub organization, outputting a formatted terminal report.

## Usage
```bash
python main.py --org your-org --token YOUR_TOKEN
```

## Setup
```bash
pip install requests rich responses
```

## Test
```bash
python -m unittest test_monitor.py
```
