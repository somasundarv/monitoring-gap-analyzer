from __future__ import annotations

from rich.console import Console
from rich.table import Table

from .analyzer import GapResult


def render_table(results: list[GapResult]) -> None:
    table = Table(title="Monitoring Gap Report")
    table.add_column("Service")
    table.add_column("Criticality")
    table.add_column("Owner")
    table.add_column("Alert?")
    table.add_column("Dashboard?")
    table.add_column("Gap")
    table.add_column("Severity", justify="right")

    for r in results:
        style = "green" if r.gap_type == "covered" else "red"
        table.add_row(
            r.service.name,
            r.service.criticality,
            r.service.owner,
            "yes" if r.has_alert else "no",
            "yes" if r.has_dashboard else "no",
            f"[{style}]{r.gap_type}[/{style}]",
            str(r.severity_score),
        )
    Console().print(table)


def render_markdown(results: list[GapResult]) -> str:
    lines = [
        "| Service | Criticality | Owner | Alert | Dashboard | Gap | Severity |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in results:
        lines.append(
            f"| {r.service.name} | {r.service.criticality} | {r.service.owner} "
            f"| {'yes' if r.has_alert else 'no'} | {'yes' if r.has_dashboard else 'no'} "
            f"| {r.gap_type} | {r.severity_score} |"
        )
    return "\n".join(lines)
