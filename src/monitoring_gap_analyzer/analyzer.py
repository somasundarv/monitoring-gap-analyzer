from __future__ import annotations

from dataclasses import dataclass

from .catalog import CRITICALITY_WEIGHT, Service

_GAP_MULTIPLIER = {
    "no monitoring": 2.0,
    "missing alert": 1.5,
    "missing dashboard": 1.0,
    "covered": 0.0,
}


@dataclass
class GapResult:
    service: Service
    has_alert: bool
    has_dashboard: bool

    @property
    def gap_type(self) -> str:
        if not self.has_alert and not self.has_dashboard:
            return "no monitoring"
        if not self.has_alert:
            return "missing alert"
        if not self.has_dashboard:
            return "missing dashboard"
        return "covered"

    @property
    def severity_score(self) -> float:
        weight = CRITICALITY_WEIGHT.get(self.service.criticality, 1)
        return round(weight * _GAP_MULTIPLIER[self.gap_type], 1)


def analyze(
    services: list[Service], alert_texts: list[str], dashboard_texts: list[str]
) -> list[GapResult]:
    results = [
        GapResult(
            service=svc,
            has_alert=any(svc.matches(t) for t in alert_texts),
            has_dashboard=any(svc.matches(t) for t in dashboard_texts),
        )
        for svc in services
    ]
    return sorted(results, key=lambda r: r.severity_score, reverse=True)
