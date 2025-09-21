Purpose

Provide a transparent, persistent read-through layer that:

Reuses previously retrieved market data for requested tickers and date ranges.

Calls Yahoo only for dates that are not yet stored locally.

Feeds the calculation layer with data in the exact same format it receives today.

Placement (high-level)
[User Task]
    │
    ▼
[Data Access Boundary  ← insert Warehouse here]
    │
    ├─(1) Check Warehouse coverage for requested tickers & dates
    │
    ├─(2) For gaps only → Yahoo (existing behavior, unchanged)
    │            │
    │            └─ Persist new data locally and update coverage
    │
    └─(3) Read full requested range from Warehouse → return to Calculations

Responsibilities (by layer)

Calculations (unchanged): Consume data exactly as before; unaware of Warehouse.

Data Access Boundary (existing): Remains the single point that supplies data to calculations.

Warehouse (new):

Understands which dates are already stored (“coverage”).

Detects gaps between requested dates and stored dates.

Persists newly fetched slices and updates coverage.

Serves the complete requested range back to the Data Access Boundary.

Yahoo (existing): Source of truth for any missing slices; invocation parameters remain exactly as they are today.

Request lifecycle (authoritative sequence)

Receive request for specific tickers and a date range.

Inspect Warehouse coverage for each (ticker, dataset) in that range.

Compute missing sub-ranges (if any).

Fetch only missing sub-ranges from Yahoo using the same request pattern the system uses today.

Persist newly fetched slices and update coverage to reflect the newly available dates.

Load the entire requested range from Warehouse.

Return data in the current contract (same shape, ordering, and types).

Calculations run unmodified and produce outputs as today.

Coverage concept (operational, not technical)

Coverage records which dates are present locally for each (ticker, dataset).

When a request arrives, coverage is used to split the request into:

Covered dates (answer locally),

Missing dates (fetch from Yahoo, then persist).

After persisting, coverage expands so subsequent requests rely more on local data.

Freshness & updates (policy level)

If a request includes very recent dates (e.g., up to “today”), Warehouse may choose to refresh only the recent tail according to a simple freshness policy.

Freshness policy is configurable and must not alter the data contract or Yahoo parameters.

Even when refreshing, the system only fetches the portion considered “stale,” not the entire range.

Error handling & fallbacks

If Warehouse read fails: fall back to Yahoo for the required dates; do not block calculations.

If Yahoo fetch fails for a missing slice: return the same error behavior the system has today (no new error shapes).

Warehouse must not introduce partial or altered outputs; either it supplies the exact contract or defers to the existing path.

Observability (minimal, decision-focused)

Track counts for: warehouse_hit, warehouse_miss, yahoo_calls, missing_range_segments.

Track timing for: read from Warehouse, Yahoo fetch, persist, end-to-end.

These metrics validate that the new flow reduces calls and improves latency without changing results.

Rollout & control

A single feature flag enables/disables the Warehouse path end-to-end.

With the flag off, the system behaves exactly as it does today.

Staged enablement is recommended (e.g., internal, partial traffic, full).

Non-goals

No changes to calculation logic or its inputs/outputs.

No changes to Yahoo client semantics or parameters.

No schema or code guidance in this document; implementation details live elsewhere.

Success criteria (mirrors acceptance)

Identical outputs vs. today for the same requests.

Reduced Yahoo calls on repeated or overlapping ranges.

Faster responses when ranges are fully covered locally.

Ability to disable Warehouse instantly with no behavior change.