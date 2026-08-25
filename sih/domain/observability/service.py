from datetime import datetime, timezone
import time
from typing import Any
from pydantic import BaseModel, Field

class SystemHealth(BaseModel):
    status: str = "HEALTHY"
    version: str = "1.0.0"
    uptime_seconds: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    components: dict[str, str] = Field(default_factory=lambda: {
        "identity": "UP",
        "intelligence": "UP",
        "context": "UP",
        "memory": "UP",
        "policy": "UP",
        "action": "UP",
        "workflow": "UP",
        "database": "UP"
    })

class ObservabilityPlatform:
    def __init__(self):
        self._start_time = time.time()
        self._metrics: dict[str, list[float]] = {
            "intent_latency_ms": [],
            "planning_latency_ms": [],
            "action_latency_ms": [],
            "action_success_count": [0],
            "action_failure_count": [0]
        }

    def record_latency(self, metric_name: str, duration_ms: float) -> None:
        if metric_name not in self._metrics:
            self._metrics[metric_name] = []
        self._metrics[metric_name].append(duration_ms)

    def record_action_result(self, success: bool) -> None:
        if success:
            self._metrics["action_success_count"][0] += 1
        else:
            self._metrics["action_failure_count"][0] += 1

    def get_health(self) -> SystemHealth:
        return SystemHealth(uptime_seconds=time.time() - self._start_time)

    def get_metrics_summary(self) -> dict[str, Any]:
        summary = {}
        for k, v in self._metrics.items():
            if isinstance(v, list) and v and isinstance(v[0], (int, float)):
                if k.endswith("_count"):
                    summary[k] = v[0]
                else:
                    summary[f"avg_{k}"] = sum(v) / len(v) if v else 0.0
                    summary[f"count_{k}"] = len(v)
        return summary

observability_platform = ObservabilityPlatform()
