# Dataset Report — GraphTriage Synthetic Dataset

_Generated: 2026-09-05T07:29:51.978168+00:00_

**Total tickets loaded:** 1200

## Split Distribution

| Split | Count |
|---|---|
| test | 184 |
| train | 837 |
| val | 179 |

## Tickets per Service

| Service | Count |
|---|---|
| search-service | 254 |
| notification-service | 250 |
| payment-service | 236 |
| auth-service | 230 |
| order-service | 230 |

## Tickets per Root-Cause Category

| Category | Count |
|---|---|
| third-party-api-failure | 112 |
| null-pointer-exception | 102 |
| deadlock | 102 |
| authentication-failure | 96 |
| connection-pool-exhaustion | 96 |
| rate-limit-exceeded | 95 |
| cache-invalidation-bug | 92 |
| disk-space-exhaustion | 91 |
| data-corruption | 86 |
| memory-leak | 86 |
| config-error | 85 |
| race-condition | 81 |
| timeout | 76 |

## Priority Distribution

| Priority | Count |
|---|---|
| HIGH | 466 |
| LOW | 247 |
| MEDIUM | 487 |

## Resolution Time — Overall

- Min: 1.00 hours
- Avg: 5.23 hours
- Max: 23.87 hours

## Resolution Time — by Category

| Category | Min (h) | Avg (h) | Max (h) |
|---|---|---|---|
| authentication-failure | 1.02 | 2.52 | 3.98 |
| cache-invalidation-bug | 2.01 | 3.54 | 5.0 |
| config-error | 1.02 | 2.1 | 3.0 |
| connection-pool-exhaustion | 3.11 | 5.37 | 7.93 |
| data-corruption | 5.0 | 8.35 | 11.93 |
| deadlock | 4.01 | 7.16 | 9.87 |
| disk-space-exhaustion | 1.0 | 1.9 | 2.99 |
| memory-leak | 8.17 | 16.69 | 23.87 |
| null-pointer-exception | 2.08 | 3.95 | 5.86 |
| race-condition | 4.05 | 7.04 | 9.99 |
| rate-limit-exceeded | 1.01 | 1.54 | 1.98 |
| third-party-api-failure | 2.02 | 4.78 | 7.98 |
| timeout | 2.06 | 3.99 | 5.99 |

## Notes

This dataset is synthetically generated (see `data/generator/config.py` and `generate.py`) — every label (root cause, service, priority, resolution time) is known by construction, since we generated the ground truth ourselves. This is documented as 'Option B' in `docs/prd.md` Section 9, and should be stated plainly in the thesis/paper as a limitation, not hidden.

Sanity check: no service or category should have a near-zero or overwhelmingly dominant share of tickets. Per the counts above, distribution is reasonably balanced.
