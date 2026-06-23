from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml

CRITICALITY_WEIGHT = {"tier1": 3, "tier2": 2, "tier3": 1}


@dataclass
class Service:
    name: str
    criticality: str
    owner: str
    aliases: list[str] = field(default_factory=list)

    def matches(self, text: str) -> bool:
        text = text.lower()
        return any(candidate.lower() in text for candidate in [self.name, *self.aliases])


def load_catalog(path: str | Path) -> list[Service]:
    data = yaml.safe_load(Path(path).read_text())
    return [
        Service(
            name=entry["name"],
            criticality=entry.get("criticality", "tier3"),
            owner=entry.get("owner", "unknown"),
            aliases=entry.get("aliases", []),
        )
        for entry in data["services"]
    ]
