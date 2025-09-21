Objective (unchanged contracts)

Introduce a local persistent Warehouse layer that transparently reuses previously retrieved market data and fetches only missing ranges from Yahoo. The computational outputs, request interfaces, and data formats must remain exactly as they are today.

New end-to-end flow (authoritative)

Task request (portfolio/ticker analysis) → Check Warehouse → Fetch only missing from Yahoo → Persist to Warehouse → Read full range from Warehouse → Calculations → Output

This replaces the “always Yahoo first” behavior without changing computation modules.

Guardrails (non-negotiable)

No public contract changes. Whatever the calculation layer expects today (shape, columns, index semantics, ordering) is returned identically.

Single data entry point. The Warehouse logic is inserted only in the existing data access boundary; calculation code never talks to Warehouse directly.

Yahoo behavior stays the same when Warehouse is off or empty.

Idempotent persistence. Repeated storage of the same records does not duplicate data.

Deterministic merging. When a request spans known and unknown dates, only the unknown dates are fetched from Yahoo.

Rollout switch

A single on/off flag (e.g., WAREHOUSE_ENABLED) gates the entire Warehouse path. When off, behavior equals today’s production behavior.

Execution plan (phases = outcomes; track with checkboxes)

Phase 0 — Architecture alignment (no code changes)

 Confirm the one boundary where market data is retrieved for calculations.

 Confirm exact data contract currently returned to calculations (columns, index, ordering, types).

 Document current request→fetch→calculate→output path to ensure drop-in placement for Warehouse.

Phase 1 — Read-through path (no Yahoo changes)

 Insert Warehouse read just before the current Yahoo call.

 For a given request range: determine which dates are already present locally and which are missing (gap detection).

 If Warehouse is disabled or empty: proceed as today.

Phase 2 — Fill-gaps path (Yahoo only for missing dates)

 For the missing sub-ranges only, call Yahoo exactly as today (same parameters, same semantics).

 Persist the newly retrieved data locally.

 Update local coverage so future requests recognize these dates as present.

Phase 3 — Authoritative source for calculations

 After gap filling, re-read the entire requested range from Warehouse.

 Return data to the calculation layer in the exact current format.

Phase 4 — Observability & rollout

 Add counters: warehouse_hits, warehouse_misses, yahoo_calls, filled_ranges.

 Add lightweight timing around (read, fill, persist) to quantify speed-up.

 Enable Warehouse in staging; compare outputs run-for-run with Warehouse off (bit-for-bit equality).

 Gradually enable in production with the flag, monitor metrics, and be ready to toggle off.

Acceptance scenarios (must pass)

Cold start: First request for a range results in Yahoo calls; subsequent identical request uses Warehouse only; outputs identical.

Range expansion: Request [Y1..Y2] after [Y2..Y3] is already stored triggers Yahoo only for [Y1..Y2), not for [Y2..Y3]; outputs identical to legacy path.

No regression: With Warehouse disabled, behavior (including API parameters and results) is unchanged from today.

Idempotency: Re-requesting the same dates does not multiply stored rows; outputs identical.

Performance: Repeat requests of fully covered ranges involve zero Yahoo calls and are measurably faster.