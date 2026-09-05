"""
GraphTriage — Synthetic Dataset Definitions (Day 2, Step 1)

This file defines everything the generator (Day 2, Step 2 - generate.py) needs
to produce realistic-looking, labeled tickets:

- SERVICES: the 5 fake microservice names used purely as a metadata label on
  each ticket (we are NOT building 5 real services — see chat explanation).
- PRIORITIES: the possible ticket priority values.
- ROOT_CAUSES: 13 root-cause categories. Each has:
    - resolution_time_hours: (min, max) range used to generate a realistic
      resolution time for tickets of this category.
    - priority_weights: probability of LOW/MEDIUM/HIGH priority for this
      category (e.g. memory-leak skews HIGH, config-error skews LOW).
    - detail_range / detail_unit: used to fill a realistic-looking number
      into the ticket text (e.g. "response time exceeding 4200ms").
    - title_templates / description_templates: multiple phrasings per
      category so generated tickets aren't all identical.

Nothing in this file is executed directly — generate.py (Step 2) imports
these definitions and does the actual random ticket generation.
"""

SERVICES = [
    "payment-service",
    "auth-service",
    "search-service",
    "order-service",
    "notification-service",
]

PRIORITIES = ["LOW", "MEDIUM", "HIGH"]

ROOT_CAUSES = {

    "timeout": {
        "resolution_time_hours": (2, 6),
        "priority_weights": {"LOW": 0.2, "MEDIUM": 0.5, "HIGH": 0.3},
        "detail_range": (500, 8000),
        "detail_unit": "ms",
        "title_templates": [
            "{service} requests timing out under load",
            "Intermittent timeout errors on {service}",
            "{service} API response time exceeding {n}{unit}",
        ],
        "description_templates": [
            "Users are reporting that {service} times out intermittently during peak hours. Average response latency has spiked to {n}{unit}, well above the expected threshold.",
            "Monitoring shows {service} response latency crossing {n}{unit} for a subset of requests, causing downstream failures in dependent services.",
            "Multiple retries observed for {service} calls; timeout threshold of {n}{unit} is being breached repeatedly since this morning.",
        ],
    },

    "null-pointer-exception": {
        "resolution_time_hours": (2, 6),
        "priority_weights": {"LOW": 0.3, "MEDIUM": 0.5, "HIGH": 0.2},
        "detail_range": (2, 40),
        "detail_unit": " occurrences/hour",
        "title_templates": [
            "NullPointerException crashing {service}",
            "{service} throwing NPE on certain requests",
            "Unhandled null reference causing {service} failures",
        ],
        "description_templates": [
            "{service} logs show a NullPointerException occurring roughly {n}{unit}, causing 500 errors for affected requests.",
            "A null reference in the request-handling path of {service} is causing intermittent crashes, observed {n} times in the last hour.",
            "Stack traces indicate an unhandled NPE in {service}, triggered by malformed input on certain endpoints.",
        ],
    },

    "connection-pool-exhaustion": {
        "resolution_time_hours": (3, 8),
        "priority_weights": {"LOW": 0.1, "MEDIUM": 0.4, "HIGH": 0.5},
        "detail_range": (50, 200),
        "detail_unit": " active connections",
        "title_templates": [
            "{service} database connection pool exhausted",
            "Connection pool timeout errors on {service}",
            "{service} unable to acquire DB connections under load",
        ],
        "description_templates": [
            "{service} is failing to acquire new database connections; pool usage has reached {n}{unit}, at capacity.",
            "Under peak load, {service}'s connection pool is being exhausted, with {n}{unit} held open longer than expected.",
            "Database connection pool for {service} is maxed out at {n}{unit}, causing request queuing and failures.",
        ],
    },

    "memory-leak": {
        "resolution_time_hours": (8, 24),
        "priority_weights": {"LOW": 0.05, "MEDIUM": 0.25, "HIGH": 0.7},
        "detail_range": (20, 500),
        "detail_unit": " MB/hour",
        "title_templates": [
            "Memory usage steadily increasing on {service}",
            "{service} restarting due to OutOfMemoryError",
            "Suspected memory leak in {service}",
        ],
        "description_templates": [
            "{service} memory consumption is growing at approximately {n}{unit}, eventually triggering OOM restarts.",
            "Heap dumps from {service} show retained objects growing over time, consistent with a memory leak at roughly {n}{unit}.",
            "{service} instances are being restarted by the orchestrator due to memory pressure, growing at {n}{unit} since deployment.",
        ],
    },

    "config-error": {
        "resolution_time_hours": (1, 3),
        "priority_weights": {"LOW": 0.5, "MEDIUM": 0.4, "HIGH": 0.1},
        "detail_range": (5, 95),
        "detail_unit": "% of requests misrouted",
        "title_templates": [
            "Misconfigured environment variable breaking {service}",
            "{service} pointing to wrong downstream endpoint",
            "Configuration drift causing {service} failures",
        ],
        "description_templates": [
            "A misconfigured property in {service} is causing {n}{unit}, following the last deployment.",
            "{service} is using an outdated configuration value, resulting in {n}{unit} to an incorrect endpoint.",
            "Environment-specific configuration was not updated for {service}, leading to {n}{unit} in the current environment.",
        ],
    },

    "rate-limit-exceeded": {
        "resolution_time_hours": (1, 2),
        "priority_weights": {"LOW": 0.4, "MEDIUM": 0.5, "HIGH": 0.1},
        "detail_range": (100, 5000),
        "detail_unit": " requests/sec",
        "title_templates": [
            "{service} rejecting requests due to rate limiting",
            "Rate limit threshold breached on {service}",
            "{service} clients receiving 429 errors",
        ],
        "description_templates": [
            "{service} is rejecting a portion of traffic after exceeding {n}{unit}, the configured rate limit.",
            "Client integrations are hitting {service}'s rate limiter, sustained load of {n}{unit} exceeding the threshold.",
            "A traffic spike pushed {service} to {n}{unit}, triggering rate-limit rejections for legitimate users.",
        ],
    },

    "cache-invalidation-bug": {
        "resolution_time_hours": (2, 5),
        "priority_weights": {"LOW": 0.3, "MEDIUM": 0.5, "HIGH": 0.2},
        "detail_range": (5, 80),
        "detail_unit": "% stale reads",
        "title_templates": [
            "Stale data being served by {service}",
            "Cache invalidation bug in {service}",
            "{service} returning outdated results after updates",
        ],
        "description_templates": [
            "{service} is serving stale cached data for approximately {n}{unit} after an update, due to a cache invalidation bug.",
            "Users report seeing outdated information from {service}; investigation points to {n}{unit} caused by improper cache invalidation.",
            "A recent change to {service} did not properly invalidate the cache, resulting in {n}{unit} of requests receiving old data.",
        ],
    },

    "deadlock": {
        "resolution_time_hours": (4, 10),
        "priority_weights": {"LOW": 0.05, "MEDIUM": 0.35, "HIGH": 0.6},
        "detail_range": (2, 50),
        "detail_unit": " threads blocked",
        "title_templates": [
            "{service} hanging due to suspected deadlock",
            "Thread deadlock detected in {service}",
            "{service} requests stuck indefinitely",
        ],
        "description_templates": [
            "Thread dumps from {service} show {n}{unit} in a circular wait condition, consistent with a deadlock.",
            "{service} has become unresponsive; monitoring shows {n}{unit} for an extended period with no progress.",
            "A deadlock between two resources in {service} is blocking {n}{unit}, requiring a manual restart to recover.",
        ],
    },

    "authentication-failure": {
        "resolution_time_hours": (1, 4),
        "priority_weights": {"LOW": 0.2, "MEDIUM": 0.4, "HIGH": 0.4},
        "detail_range": (10, 500),
        "detail_unit": " failed login attempts",
        "title_templates": [
            "Users unable to authenticate via {service}",
            "{service} rejecting valid JWT tokens",
            "Spike in authentication failures on {service}",
        ],
        "description_templates": [
            "{service} is rejecting valid credentials for a subset of users, with {n}{unit} recorded in the last hour.",
            "A token validation issue in {service} is causing legitimate sessions to be rejected, affecting {n}{unit}.",
            "Following a recent deployment, {service} is failing to validate JWT tokens correctly, resulting in {n}{unit}.",
        ],
    },

    "data-corruption": {
        "resolution_time_hours": (5, 12),
        "priority_weights": {"LOW": 0.05, "MEDIUM": 0.25, "HIGH": 0.7},
        "detail_range": (5, 300),
        "detail_unit": " records affected",
        "title_templates": [
            "Corrupted records detected in {service}",
            "{service} writing malformed data",
            "Data integrity issue found in {service}",
        ],
        "description_templates": [
            "An investigation into {service} found {n}{unit} with corrupted or malformed fields, likely due to a serialization bug.",
            "{service} appears to have written inconsistent data during a recent batch job, affecting {n}{unit}.",
            "Data validation checks flagged {n}{unit} in {service} as corrupted, requiring manual reconciliation.",
        ],
    },

    "third-party-api-failure": {
        "resolution_time_hours": (2, 8),
        "priority_weights": {"LOW": 0.3, "MEDIUM": 0.5, "HIGH": 0.2},
        "detail_range": (5, 90),
        "detail_unit": "% error rate",
        "title_templates": [
            "{service} degraded due to third-party API outage",
            "Upstream provider errors impacting {service}",
            "{service} failing to reach external dependency",
        ],
        "description_templates": [
            "{service} depends on an external API that is currently returning errors at a {n}{unit}, causing downstream failures.",
            "An outage at a third-party provider used by {service} is resulting in {n}{unit} for dependent operations.",
            "{service} does not have a fallback for the current third-party API degradation, seeing {n}{unit} on affected calls.",
        ],
    },

    "disk-space-exhaustion": {
        "resolution_time_hours": (1, 3),
        "priority_weights": {"LOW": 0.1, "MEDIUM": 0.4, "HIGH": 0.5},
        "detail_range": (85, 99),
        "detail_unit": "% disk used",
        "title_templates": [
            "{service} host running low on disk space",
            "Disk space alert triggered for {service}",
            "{service} write failures due to full disk",
        ],
        "description_templates": [
            "The host running {service} has reached {n}{unit}, causing write failures for logs and temporary files.",
            "{service} is unable to write new data as disk utilization has hit {n}{unit} on the underlying volume.",
            "Log rotation failed on {service}'s host, allowing disk usage to climb to {n}{unit} before the alert fired.",
        ],
    },

    "race-condition": {
        "resolution_time_hours": (4, 10),
        "priority_weights": {"LOW": 0.1, "MEDIUM": 0.4, "HIGH": 0.5},
        "detail_range": (10, 200),
        "detail_unit": " concurrent requests",
        "title_templates": [
            "Inconsistent state observed in {service} under concurrency",
            "Race condition suspected in {service}",
            "{service} producing inconsistent results under parallel load",
        ],
        "description_templates": [
            "Under approximately {n}{unit}, {service} is producing inconsistent results, suggesting a race condition in shared state handling.",
            "{service} occasionally processes the same request twice when {n}{unit} arrive in a short window, indicating a concurrency bug.",
            "Load testing with {n}{unit} revealed a race condition in {service}'s update logic, leading to data inconsistency.",
        ],
    },

}


def _validate_definitions():
    """Sanity-check the definitions above at import time (fails loudly if a
    category is misconfigured, rather than silently producing bad data)."""
    for name, cfg in ROOT_CAUSES.items():
        weights = cfg["priority_weights"]
        total = round(sum(weights.values()), 5)
        assert total == 1.0, f"{name}: priority_weights must sum to 1.0, got {total}"
        assert set(weights.keys()) == set(PRIORITIES), f"{name}: priority_weights keys must match PRIORITIES"
        lo, hi = cfg["resolution_time_hours"]
        assert 0 < lo < hi, f"{name}: invalid resolution_time_hours range {cfg['resolution_time_hours']}"
        dlo, dhi = cfg["detail_range"]
        assert 0 <= dlo < dhi, f"{name}: invalid detail_range {cfg['detail_range']}"
        assert len(cfg["title_templates"]) >= 3, f"{name}: needs at least 3 title templates"
        assert len(cfg["description_templates"]) >= 3, f"{name}: needs at least 3 description templates"


_validate_definitions()


if __name__ == "__main__":
    # Quick manual check: python3 config.py
    print(f"{len(SERVICES)} services, {len(ROOT_CAUSES)} root-cause categories defined.")
    print("All definitions validated successfully.")
