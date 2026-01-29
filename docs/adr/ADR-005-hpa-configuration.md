# ADR-005: HPA Configuration Values

## Status

Accepted

## Context

The Horizontal Pod Autoscaler (HPA) for the API gateway requires three key parameters: minimum replicas, maximum replicas, and the CPU utilization target. These numbers directly affect availability, cost, and response latency. This ADR documents why specific values were chosen.

## Decision

### Replicas: min 2, max 5

**Minimum 2:**
- Guarantees availability during single-pod failures (node drain, OOM kill, rolling update).
- With only 1 replica, any failure causes downtime.
- 2 is the minimum for zero-downtime rolling updates (one pod serves traffic while the other restarts).

**Maximum 5:**
- This is a cost ceiling for a demonstration/reference project.
- Each replica requests 100m CPU and 128Mi memory; 5 replicas = 500m CPU and 640Mi total.
- For a stateless proxy to GitHub's API, 5 replicas handle significant throughput before GitHub's own rate limits become the bottleneck.

### CPU target: 70%

- Leaves a 30% buffer for absorbing traffic spikes before new pods are scheduled.
- Pod scheduling + startup takes 10-30 seconds; during this window, existing pods must absorb the extra load.
- 70% is a common production target — low enough to avoid saturation, high enough to avoid over-provisioning.

### Resource requests and limits

| Resource | Request | Limit | Rationale |
|----------|---------|-------|-----------|
| CPU | 100m | 500m | FastAPI + uvicorn idles at ~30m CPU. 100m request ensures fair scheduling. 500m limit prevents a runaway request loop from starving other pods. |
| Memory | 128Mi | 256Mi | Idle footprint is ~50MB. 128Mi request accommodates normal operation with headroom. 256Mi limit catches memory leaks before they affect the node. |

### Probe intervals

| Probe | Initial Delay | Period | Why |
|-------|--------------|--------|-----|
| Liveness | 10s | 30s | Longer initial delay lets the app fully start. 30s period avoids unnecessary restarts from transient slowness. |
| Readiness | 5s | 10s | Shorter initial delay gets the pod into service faster. 10s period enables quick removal from the load balancer on failure. |

## Consequences

### Positive

- The system self-heals and scales without manual intervention.
- Resource limits prevent noisy-neighbor problems on shared clusters.
- The values are conservative enough for a reference project while still demonstrating real autoscaling behavior.

### Negative

- Minimum 2 replicas means the project always uses at least 200m CPU and 256Mi memory, even at zero traffic.
- Max 5 may be too low for genuine high-traffic production use — but this is a reference project, not a production service.

### Neutral

- These values should be tuned per environment. The Terraform variables (`min_replicas`, `max_replicas`, `cpu_target`) allow overriding them without changing the manifests.
