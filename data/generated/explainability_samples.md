# Explainability Samples — GraphTriage

_Generated: 2026-09-06T12:55:00.154162+00:00_

Each example below shows the two explanation mechanisms working together: SHAP-based keyword contributions (which words drove the prediction) and graph-based similar-ticket retrieval (which past tickets support it). See `docs/design.md` Section 11 and `docs/memory.md` Sprint Day 6 for the design rationale.

## Ticket #1180
**Text:** search-service producing inconsistent results under parallel load. search-service occasionally processes the same request twice when 112 concurrent requests arrive in a short window, indicating a concurrency bug.

**True category:** `race-condition` | **Predicted:** `race-condition` | ✅ Match
**Confidence:** 0.8441

**Top contributing keywords:**
- concurrent (+0.172)
- concurrent requests (+0.172)
- concurrency (+0.165)
- producing inconsistent (+0.142)
- producing (+0.142)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #573 | race-condition | 4.56 | 0.9979 |
| #1089 | race-condition | 9.38 | 0.9866 |
| #584 | race-condition | 8.72 | 0.938 |
| #1157 | race-condition | 9.81 | 0.9374 |
| #146 | race-condition | 4.51 | 0.9271 |

---

## Ticket #1045
**Text:** payment-service write failures due to full disk. Log rotation failed on payment-service's host, allowing disk usage to climb to 92% disk used before the alert fired.

**True category:** `disk-space-exhaustion` | **Predicted:** `disk-space-exhaustion` | ✅ Match
**Confidence:** 0.874

**Top contributing keywords:**
- disk (+1.241)
- write (+0.176)
- host (+0.168)
- disk used (+0.153)
- write failures (+0.152)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #671 | disk-space-exhaustion | 2.39 | 1.0 |
| #162 | disk-space-exhaustion | 2.16 | 0.9993 |
| #583 | disk-space-exhaustion | 2.05 | 0.9987 |
| #661 | disk-space-exhaustion | 2.13 | 0.9987 |
| #701 | disk-space-exhaustion | 1.09 | 0.9969 |

---

## Ticket #1023
**Text:** payment-service database connection pool exhausted. Under peak load, payment-service's connection pool is being exhausted, with 106 active connections held open longer than expected.

**True category:** `connection-pool-exhaustion` | **Predicted:** `connection-pool-exhaustion` | ✅ Match
**Confidence:** 0.8447

**Top contributing keywords:**
- pool (+0.487)
- connection (+0.423)
- connection pool (+0.423)
- exhausted (+0.247)
- pool exhausted (+0.247)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #862 | connection-pool-exhaustion | 4.01 | 0.9895 |
| #960 | connection-pool-exhaustion | 5.49 | 0.9516 |
| #759 | connection-pool-exhaustion | 5.13 | 0.9509 |
| #888 | connection-pool-exhaustion | 6.0 | 0.9493 |
| #337 | connection-pool-exhaustion | 5.18 | 0.9471 |

---

## Ticket #1087
**Text:** Intermittent timeout errors on search-service. Users are reporting that search-service times out intermittently during peak hours. Average response latency has spiked to 5819ms, well above the expected threshold.

**True category:** `timeout` | **Predicted:** `timeout` | ✅ Match
**Confidence:** 0.8456

**Top contributing keywords:**
- response (+0.274)
- response latency (+0.195)
- latency (+0.195)
- timeout (+0.190)
- intermittent timeout (+0.161)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #1062 | timeout | 2.17 | 0.9974 |
| #740 | timeout | 4.67 | 0.9208 |
| #753 | timeout | 3.37 | 0.9177 |
| #301 | timeout | 5.56 | 0.8858 |
| #906 | timeout | 4.02 | 0.8834 |

---

## Ticket #1079
**Text:** auth-service clients receiving 429 errors. A traffic spike pushed auth-service to 2589 requests/sec, triggering rate-limit rejections for legitimate users.

**True category:** `rate-limit-exceeded` | **Predicted:** `rate-limit-exceeded` | ✅ Match
**Confidence:** 0.8952

**Top contributing keywords:**
- rate limit (+0.245)
- limit (+0.245)
- sec (+0.223)
- requests sec (+0.223)
- traffic (+0.184)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #19 | rate-limit-exceeded | 1.33 | 0.9943 |
| #227 | rate-limit-exceeded | 1.76 | 0.9942 |
| #332 | rate-limit-exceeded | 1.07 | 0.9927 |
| #487 | rate-limit-exceeded | 1.48 | 0.9899 |
| #391 | rate-limit-exceeded | 1.91 | 0.9879 |

---

## Ticket #1074
**Text:** Connection pool timeout errors on payment-service. payment-service is failing to acquire new database connections; pool usage has reached 170 active connections, at capacity.

**True category:** `connection-pool-exhaustion` | **Predicted:** `connection-pool-exhaustion` | ✅ Match
**Confidence:** 0.8413

**Top contributing keywords:**
- connections (+0.592)
- pool (+0.560)
- connection (+0.227)
- connection pool (+0.227)
- database (+0.192)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #1108 | connection-pool-exhaustion | 5.96 | 0.9933 |
| #476 | connection-pool-exhaustion | 3.16 | 0.9493 |
| #135 | connection-pool-exhaustion | 6.98 | 0.9192 |
| #886 | connection-pool-exhaustion | 7.86 | 0.9175 |
| #10 | connection-pool-exhaustion | 7.12 | 0.9151 |

---

## Ticket #1052
**Text:** Cache invalidation bug in search-service. search-service is serving stale cached data for approximately 22% stale reads after an update, due to a cache invalidation bug.

**True category:** `cache-invalidation-bug` | **Predicted:** `cache-invalidation-bug` | ✅ Match
**Confidence:** 0.8487

**Top contributing keywords:**
- stale (+0.548)
- cache (+0.459)
- cache invalidation (+0.395)
- invalidation (+0.395)
- invalidation bug (+0.310)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #459 | cache-invalidation-bug | 3.75 | 0.9979 |
| #815 | cache-invalidation-bug | 3.98 | 0.9971 |
| #1166 | cache-invalidation-bug | 3.92 | 0.9535 |
| #318 | cache-invalidation-bug | 2.34 | 0.9534 |
| #551 | cache-invalidation-bug | 4.03 | 0.9529 |

---

## Ticket #1043
**Text:** Spike in authentication failures on search-service. A token validation issue in search-service is causing legitimate sessions to be rejected, affecting 70 failed login attempts.

**True category:** `authentication-failure` | **Predicted:** `authentication-failure` | ✅ Match
**Confidence:** 0.7503

**Top contributing keywords:**
- failed login (+0.198)
- login attempts (+0.198)
- attempts (+0.198)
- login (+0.198)
- failed (+0.155)

**Similar past tickets:**
| Ticket ID | Category | Resolution Time (h) | Similarity |
|---|---|---|---|
| #725 | authentication-failure | 2.56 | 0.9888 |
| #707 | authentication-failure | 2.3 | 0.9324 |
| #951 | authentication-failure | 1.35 | 0.9256 |
| #406 | authentication-failure | 3.43 | 0.8838 |
| #36 | authentication-failure | 2.19 | 0.8806 |

---

## Summary

- Sample size: 8
- Prediction accuracy on this sample: 8/8

These examples can be used directly as figures/tables in the thesis's qualitative evaluation section, and as reference content when building the Day 8 dashboard's explanation panel.
