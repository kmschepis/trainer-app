from prometheus_client import Counter, Histogram

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    labelnames=["method", "path", "status"],
)
http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration (seconds)",
    labelnames=["method", "path"],
)

ws_messages_total = Counter(
    "ws_messages_total",
    "Total websocket messages received",
    labelnames=["type"],
)
agent_calls_total = Counter(
    "agent_calls_total",
    "Total agent calls",
    labelnames=["status"],
)
agent_call_duration_seconds = Histogram(
    "agent_call_duration_seconds",
    "Agent call duration (seconds)",
)
