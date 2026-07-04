# monitoring-gap-analyzer

![CI](https://github.com/somasundarv/monitoring-gap-analyzer/actions/workflows/ci.yml/badge.svg)

Cross-references your service catalog against Prometheus alert rules and Grafana
dashboards to surface monitoring blind spots — services that are running in
production with no alerting, no dashboard, or both.

Born out of a recurring SRE problem: services get shipped, alerting/dashboards
lag behind (or never land), and the gap is only discovered during an incident.
This tool turns "do we have monitoring coverage?" into a single command instead
of a manual audit.

## How it works

1. **Service catalog** (`services.yaml`) — your list of services, each with a
   criticality tier (`tier1`/`tier2`/`tier3`), an owning team, and optional
   aliases (since alert/dashboard naming is rarely consistent with the catalog
   name).
2. **Alert rules** — a Prometheus-style rules file (`groups: -> rules:`).
3. **Dashboards** — a directory of Grafana dashboard JSON exports.

For each service, the analyzer checks whether any alert rule or dashboard
panel references it (by name or alias) and classifies the result:

| Gap type | Meaning |
|---|---|
| `covered` | has at least one alert and one dashboard |
| `missing alert` | has a dashboard but no alert |
| `missing dashboard` | has an alert but no dashboard |
| `no monitoring` | has neither |

Severity is **criticality-weighted**, not just a flat flag — a `tier1` service
missing a dashboard ranks above a `tier3` service with no monitoring at all,
because partial blindness on a critical service is the more dangerous gap in
practice.

## Usage

```bash
pip install -e .

monitoring-gap-analyzer \
  --catalog examples/service_catalog.yaml \
  --alerts examples/alert_rules.yaml \
  --dashboards examples/dashboards \
  --format table
```

Markdown output (e.g. for pasting into a wiki page or PR description):

```bash
monitoring-gap-analyzer \
  --catalog examples/service_catalog.yaml \
  --alerts examples/alert_rules.yaml \
  --dashboards examples/dashboards \
  --format markdown
```

```
| Service | Criticality | Owner | Alert | Dashboard | Gap | Severity |
|---|---|---|---|---|---|---|
| recommendation-engine | tier2 | ml-platform-team | no | yes | missing alert | 3.0 |
| user-profile-service | tier1 | identity-team | yes | no | missing dashboard | 3.0 |
| legacy-batch-job | tier3 | data-eng-team | no | no | no monitoring | 2.0 |
| checkout-service | tier1 | payments-team | yes | yes | covered | 0.0 |
```

Gate CI on coverage (exit code 1 if any gap exists):

```bash
monitoring-gap-analyzer --catalog ... --alerts ... --dashboards ... --fail-on-gap
```

## Service catalog format

```yaml
services:
  - name: checkout-service
    criticality: tier1
    owner: payments-team
    aliases: ["checkout-api", "checkout"]
```

## Development

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
ruff check .
```

## Roadmap

- Live mode: pull alert rules directly from a running Prometheus instance and
  dashboards from the Grafana HTTP API, instead of static file exports.
- Slack/PagerDuty notification on newly introduced gaps (diff against last run).
- Auto-suggest a starter alert rule / dashboard panel for flagged services.

## License

MIT
