# 004 — Observability Stack (scalable skeleton)

## Goal

Bring up a real, scalable observability baseline **while the app is still minimal**:

- **Metrics**: Prometheus scrapes API + agent
- **Logs**: services export logs via OpenTelemetry → Collector → Loki
- **Traces**: services export traces via OpenTelemetry → Collector → Tempo
- **Unified UI**: Grafana with datasources pre-provisioned

This reduces debugging overhead and makes responsiveness/latency visible early.

## Acceptance criteria

- `docker compose up --build -d` starts:
  - Prometheus (`:9090`)
  - Grafana (`:3001`)
  - Loki (`:3100`)
  - Tempo (`:3200`)
  - OpenTelemetry Collector (internal)
- API exposes `GET /metrics` with Prometheus format.
- Agent exposes `GET /metrics` with Prometheus format.
- API and agent export traces to Tempo (visible in Grafana Explore → Traces).
- API and agent export logs to Loki (visible in Grafana Explore → Logs).
- Dashboards are not required yet; just working data sources and data.

## Notes

- This is a local-dev skeleton mirroring production primitives.
- We keep configs in `infra/observability/`.
