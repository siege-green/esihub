import time
from contextlib import contextmanager
from prometheus_client import CollectorRegistry, Counter, Histogram, Gauge


class ESIHubMetrics:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.request_counter = self._get_or_create_counter(
            "esihub_requests_total", "Total requests made", ["method", "path"]
        )
        self.request_duration = self._get_or_create_histogram(
            "esihub_request_duration_seconds",
            "Request duration in seconds",
            ["method", "path"],
        )
        self.error_counter = self._get_or_create_counter(
            "esihub_errors_total", "Total errors encountered", ["error_type"]
        )
        self.active_requests = self._get_or_create_gauge(
            "esihub_active_requests", "Number of active requests"
        )

    def _get_or_create_counter(self, name, documentation, labelnames):
        try:
            return Counter(name, documentation, labelnames, registry=self.registry)
        except ValueError:
            return self.registry._names_to_collectors[name]

    def _get_or_create_histogram(self, name, documentation, labelnames):
        try:
            return Histogram(name, documentation, labelnames, registry=self.registry)
        except ValueError:
            return self.registry._names_to_collectors[name]

    def _get_or_create_gauge(self, name, documentation):
        try:
            return Gauge(name, documentation, registry=self.registry)
        except ValueError:
            return self.registry._names_to_collectors[name]

    def increment_request(self, method: str, path: str):
        self.request_counter.labels(method=method, path=path).inc()

    @contextmanager
    def measure_request_duration(self, method: str, path: str):
        start_time = time.time()
        self.active_requests.inc()
        try:
            yield
        finally:
            duration = time.time() - start_time
            self.request_duration.labels(method=method, path=path).observe(duration)
            self.active_requests.dec()

    def increment_error(self, error_type: str):
        self.error_counter.labels(error_type=error_type).inc()
