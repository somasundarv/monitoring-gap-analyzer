from __future__ import annotations

from pathlib import Path

import click

from .analyzer import analyze
from .catalog import load_catalog
from .report import render_markdown, render_table
from .sources import load_alert_rule_texts, load_dashboard_texts


@click.command()
@click.option(
    "--catalog",
    "catalog_path",
    required=True,
    type=click.Path(exists=True),
    help="Service catalog YAML file.",
)
@click.option(
    "--alerts",
    "alerts_path",
    required=True,
    type=click.Path(exists=True),
    help="Prometheus alert rules YAML file.",
)
@click.option(
    "--dashboards",
    "dashboards_path",
    required=True,
    type=click.Path(exists=True, file_okay=False),
    help="Directory of Grafana dashboard JSON exports.",
)
@click.option(
    "--format",
    "fmt",
    type=click.Choice(["table", "markdown"]),
    default="table",
    help="Output format.",
)
@click.option(
    "--output",
    "output_path",
    type=click.Path(),
    default=None,
    help="Write markdown report to this file instead of stdout.",
)
@click.option(
    "--fail-on-gap",
    is_flag=True,
    help="Exit with status 1 if any service has a monitoring gap (useful for CI gating).",
)
def main(
    catalog_path: str,
    alerts_path: str,
    dashboards_path: str,
    fmt: str,
    output_path: str | None,
    fail_on_gap: bool,
) -> None:
    """Cross-reference a service catalog against alert rules and dashboards to find monitoring gaps."""
    services = load_catalog(catalog_path)
    alert_texts = load_alert_rule_texts(alerts_path)
    dashboard_texts = load_dashboard_texts(dashboards_path)
    results = analyze(services, alert_texts, dashboard_texts)

    if fmt == "table":
        render_table(results)
    else:
        markdown = render_markdown(results)
        if output_path:
            Path(output_path).write_text(markdown + "\n")
        else:
            click.echo(markdown)

    if fail_on_gap and any(r.gap_type != "covered" for r in results):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
