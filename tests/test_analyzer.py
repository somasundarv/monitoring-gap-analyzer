from pathlib import Path

from monitoring_gap_analyzer.analyzer import analyze
from monitoring_gap_analyzer.catalog import Service, load_catalog
from monitoring_gap_analyzer.sources import load_alert_rule_texts, load_dashboard_texts

EXAMPLES = Path(__file__).resolve().parent.parent / "examples"


def test_service_matches_by_alias():
    svc = Service(name="checkout-service", criticality="tier1", owner="payments-team", aliases=["checkout-api"])
    assert svc.matches('job="checkout-api" error rate')
    assert not svc.matches("unrelated text")


def test_analyze_classifies_all_gap_types():
    covered = Service(name="svc-a", criticality="tier1", owner="team-a")
    missing_alert = Service(name="svc-b", criticality="tier2", owner="team-b")
    missing_dashboard = Service(name="svc-c", criticality="tier1", owner="team-c")
    no_monitoring = Service(name="svc-d", criticality="tier3", owner="team-d")

    alert_texts = ["alert for svc-a", "alert for svc-c"]
    dashboard_texts = ["dashboard for svc-a", "dashboard for svc-b"]

    results = analyze([covered, missing_alert, missing_dashboard, no_monitoring], alert_texts, dashboard_texts)
    by_name = {r.service.name: r for r in results}

    assert by_name["svc-a"].gap_type == "covered"
    assert by_name["svc-b"].gap_type == "missing alert"
    assert by_name["svc-c"].gap_type == "missing dashboard"
    assert by_name["svc-d"].gap_type == "no monitoring"


def test_severity_weights_criticality_over_partial_gap():
    tier1_missing_dashboard = Service(name="svc-x", criticality="tier1", owner="t")
    tier3_no_monitoring = Service(name="svc-y", criticality="tier3", owner="t")

    results = analyze(
        [tier1_missing_dashboard, tier3_no_monitoring],
        alert_texts=["alert for svc-x"],
        dashboard_texts=[],
    )
    by_name = {r.service.name: r for r in results}
    assert by_name["svc-x"].severity_score > by_name["svc-y"].severity_score


def test_end_to_end_with_example_fixtures():
    services = load_catalog(EXAMPLES / "service_catalog.yaml")
    alert_texts = load_alert_rule_texts(EXAMPLES / "alert_rules.yaml")
    dashboard_texts = load_dashboard_texts(EXAMPLES / "dashboards")

    results = analyze(services, alert_texts, dashboard_texts)
    by_name = {r.service.name: r for r in results}

    assert by_name["checkout-service"].gap_type == "covered"
    assert by_name["recommendation-engine"].gap_type == "missing alert"
    assert by_name["user-profile-service"].gap_type == "missing dashboard"
    assert by_name["legacy-batch-job"].gap_type == "no monitoring"
