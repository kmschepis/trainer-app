# 004 — Execution Log

## 2026-01-03

### Changes

- Added observability infra configs under `infra/observability/`:
	- Prometheus scrape config
	- Grafana datasource provisioning
	- Loki + Tempo config
	- OTel Collector pipelines for traces+logs
- Updated `compose.yml` to run:
	- `prometheus` (9090)
	- `grafana` (3001)
	- `loki` (3100)
	- `tempo` (3200)
	- `otel-collector` (host 4319 → container 4318)
- Instrumented services:
	- API and agent export traces+logs via OTLP HTTP to the collector
	- API and agent expose Prometheus `/metrics`

### Fixes

- Tempo needed write permission to its local storage volume; ran Tempo as root in Compose (`user: "0"`) for local-dev stability.
- Fixed OTLP exporter configuration in services to rely on `OTEL_EXPORTER_OTLP_ENDPOINT` (base URL) so traces/logs hit `/v1/traces` and `/v1/logs` correctly.

### Verification

- `docker compose up --build -d`
- Check `http://localhost:3001` (Grafana)
- Check `http://localhost:9090/targets` (Prometheus targets)
- Check `http://localhost:8000/metrics` and `http://localhost:9000/metrics`

Observed:

- Loki labels include `service_name` and logs are queryable via `query_range`.
- Tempo returns `200` for `GET /api/traces/{traceId}` for traces emitted by the agent.
