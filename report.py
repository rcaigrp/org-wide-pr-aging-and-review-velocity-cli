from typing import List, Dict
from rich.table import Table
from rich.console import Console

console = Console()

def get_age_color(days: int) -> str:
    """Return color based on PR age."""
    if days < 7:
        return "green"
    elif days <= 14:
        return "yellow"
    else:
        return "red"

def render_table(pr_data: List[Dict]) -> None:
    """Render PR data as a rich table with color-coded rows."""
    if not pr_data:
        console.print("No stale PRs found.")
        return
    
    table = Table(show_header=True, header_style="bold blue")
    table.add_column("Repo", style="white")
    table.add_column("PR #", style="cyan")
    table.add_column("Author", style="magenta")
    table.add_column("Days Open", style="yellow")
    table.add_column("Review Density", style="green")
    table.add_column("Link", style="blue")
    
    for pr in pr_data:
        color = get_age_color(pr["days_open"])
        table.add_row(
            pr["repo"],
            str(pr["pr_number"]),
            pr["author"],
            str(pr["days_open"]),
            str(pr["review_density"]),
            pr["link"],
            style=color
        )
    
    console.print(table)

def render_report(pr_data: List[Dict], output_format: str = "table") -> None:
    """Render report based on format."""
    if output_format == "table":
        render_table(pr_data)
    else:
        import csv
        import sys
        writer = csv.writer(sys.stdout)
        writer.writerow(["Repo", "PR #", "Author", "Days Open", "Review Density", "Link"])
        for pr in pr_data:
            writer.writerow([pr["repo"], pr["pr_number"], pr["author"], pr["days_open"], pr["review_density"], pr["link"]])
