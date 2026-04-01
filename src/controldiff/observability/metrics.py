from __future__ import annotations

from prometheus_client import Counter, Histogram

RUN_COUNTER = Counter(
    "controldiff_runs_total",
    "Total number of workflow runs processed.",
    labelnames=("status",),
)

RUN_DURATION = Histogram(
    "controldiff_run_duration_seconds",
    "Duration of ControlDiff workflow runs.",
)
