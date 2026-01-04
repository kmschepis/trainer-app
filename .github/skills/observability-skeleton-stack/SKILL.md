---
name: observability-skeleton-stack
description: Stand up and verify the “real skeleton” observability stack (Prometheus, Grafana, Loki, Tempo, OTel Collector) plus Python service instrumentation. Use when wiring or debugging metrics/logs/traces in the Compose environment.
---

## Mission

Provide production-shaped observability early, even while product features are minimal.

## When to use (triggers)

- Grafana has no data sources, or dashboards show no data.
- Logs aren’t queryable in Loki.
- Traces aren’t visible in Tempo.
- OTLP export errors appear in service logs.

## Inputs

- `compose.yml`
- `infra/observability/**` config files
- Python service OTel initialization modules:
  - `services/api/app/observability.py`
  - `services/agent/app/observability.py`

## Outputs

- Running services:
  - Prometheus (9090)
  - Grafana (3001)
  - Loki (3100)
  - Tempo (3200)
  - OTel Collector (receives OTLP)
- Python services export traces/logs via OTLP.
- API/Agent expose Prometheus metrics at `GET /metrics`.

## Workflow

1. Confirm Compose includes obs services and mounts:
   - Prometheus config: `infra/observability/prometheus/prometheus.yml`
   - Grafana provisioning: `infra/observability/grafana/provisioning/datasources/datasources.yml`
   - Loki config: `infra/observability/loki/loki.yml`
   - Tempo config: `infra/observability/tempo/tempo.yml`
   - OTel Collector config: `infra/observability/otel-collector/config.yml`
2. Confirm app services have env vars set for OTLP export.
3. Boot:
   - `docker compose up --build -d`
4. Verify endpoints:
   - Grafana: `http://localhost:3001`
   - Prometheus: `http://localhost:9090`
5. Verify metrics:
   - Prometheus target scrape shows `api` and `agent` up.
6. Verify logs:
   - In Grafana Explore, select Loki data source and query recent logs.
7. Verify traces:
   - In Grafana Explore, select Tempo data source and search recent traces.

## Troubleshooting heuristics

- Tempo permission errors: ensure local volume permissions are compatible (for this repo, the workaround was running Tempo as root in Compose).
- OTLP endpoint issues: prefer standard env semantics and avoid double-specifying `/v1/*` paths incorrectly.

## Example (from this repo)

- Compose wiring: `compose.yml`
- Collector pipeline: `infra/observability/otel-collector/config.yml`
- Python instrumentation: `services/api/app/observability.py`
