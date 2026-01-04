# 004 — Plan

1. Add observability services to `compose.yml`:
   - `prometheus`, `grafana`, `loki`, `tempo`, `otel-collector`
2. Add config files under `infra/observability/`:
   - Prometheus scrape config
   - Grafana provisioning (datasources)
   - Loki + Tempo config
   - OTel Collector pipelines (logs + traces)
3. Instrument API + agent:
   - `prometheus_client` metrics + `/metrics`
   - OpenTelemetry traces + logs exported to collector via OTLP HTTP
4. Verify:
   - Prometheus targets up
   - Grafana datasources working
   - Logs and traces visible for a simple chat flow
