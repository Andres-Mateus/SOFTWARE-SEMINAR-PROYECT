# JMeter Stress Test Analysis

The JMeter plan (`Workshop-4/jmeter/parking-api-stress.jmx`) drives concurrent requests against the core-service read endpoints.

- **Load model:** 10 virtual users, 5 loops (50 total iterations per sampler) hitting `/api/core/stats/overview`, `/api/core/slots`, and `/api/core/sessions?limit=10`.
- **Throughput expectation:** Under normal conditions the read-only endpoints respond in milliseconds because they only query cached slot/session data. Latency should remain well below 500ms with zero errors.
- **What to watch:**
  - Rising error rate indicates missing database connectivity or the core container not being ready.
  - Spikes in latency for `/api/core/sessions` usually mean the database lacks indexes or the dataset grew unexpectedly.
  - If CPU becomes a bottleneck, consider scaling the core-service container replicas or tuning PostgreSQL shared buffers.
- **Results location:** when executed via the CLI command in the README, a JTL file is stored at `Workshop-4/jmeter/results/results.jtl`. Use JMeter GUI or `JMeterPluginsCMD` to render HTML summaries.
