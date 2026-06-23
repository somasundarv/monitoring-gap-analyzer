from __future__ import annotations

import json
from pathlib import Path

import yaml


def load_alert_rule_texts(path: str | Path) -> list[str]:
    """Flatten a Prometheus-style alert rules file into one searchable text blob per rule."""
    data = yaml.safe_load(Path(path).read_text())
    texts = []
    for group in data.get("groups", []):
        for rule in group.get("rules", []):
            if "alert" not in rule:
                continue
            blob = " ".join(
                [
                    rule.get("alert", ""),
                    rule.get("expr", ""),
                    " ".join(str(v) for v in rule.get("labels", {}).values()),
                ]
            )
            texts.append(blob)
    return texts


def load_dashboard_texts(dir_path: str | Path) -> list[str]:
    """Flatten Grafana dashboard JSON exports into one searchable text blob per dashboard."""
    texts = []
    for file in sorted(Path(dir_path).glob("*.json")):
        data = json.loads(file.read_text())
        parts = [data.get("title", ""), " ".join(data.get("tags", []))]
        for panel in data.get("panels", []):
            parts.append(panel.get("title", ""))
            for target in panel.get("targets", []):
                parts.append(target.get("expr", "") or target.get("query", ""))
        texts.append(" ".join(parts))
    return texts
