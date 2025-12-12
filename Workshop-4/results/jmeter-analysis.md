# JMeter Stress Test Analysis

**Test plan:** Workshop-4/jmeter/parking-api-stress.jmx  
**Target:** core-service (Docker)  
**Base path:** /api/core  
**Report:** Workshop-4/jmeter/results/report/index.html  

## Summary (Total)
- Samples: 300
- Failures: 0
- Error %: 0.00%
- Average response time: 42.66 ms
- Median: 22.00 ms
- p90: 71.90 ms
- p95: 89.00 ms
- p99: 538.00 ms
- Min/Max: 11 ms / 738 ms
- Throughput: 69.67 transactions/s

## APDEX
- Total APDEX: 0.993 (T=500 ms, F=1500 ms)
- GET overview: 0.980
- GET slots: 1.000
- GET sessions: 1.000

## Per-endpoint highlights
- GET overview: avg 59.50 ms, p95 174 ms, max 738 ms, throughput 23.41/s
- GET sessions: avg 41.06 ms, p95 104 ms, max 114 ms, throughput 28.60/s
- GET slots: avg 27.42 ms, p95 64 ms, max 73 ms, throughput 28.26/s

## Observations
- No errors were observed (PASS 100%).
- A single outlier increased the p99 (max 738 ms), likely due to warm-up/cold-start effects.
- Overall performance is stable with low average latency and high throughput for the tested endpoints.
