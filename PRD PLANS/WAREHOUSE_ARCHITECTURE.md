WAREHOUSE_ARCHITECTURE.md

Purpose
Provide a transparent, persistent read-through layer that:
- Reuses previously retrieved market data for requested tickers and trading-day date ranges.
- Calls Yahoo only for trading-day dates that are not yet stored locally.
- Feeds the calculation layer with data in the exact same format it receives today.
- Stores all Warehouse data inside the project repository using an embedded SQLite database.

Storage engine (authoritative)
- Embedded SQLite (light SQL), single-file database stored at: ./warehouse/warehouse.sqlite
- WAL mode enabled; transactional writes for atomic upserts and coverage updates.
- No external database services; the database file lives within the repository directory.
- Backup/restore: copy the single file; optional export/import as needed.
- Repository policy: the location is fixed under ./warehouse/; whether the file is tracked by VCS is a project decision.

Placement (high-level)
[User Task]
  ↓
[Existing Data Access Boundary ← insert Warehouse here]
  ├─ (1) Check Warehouse coverage for requested tickers & trading-day dates
  ├─ (2) For gaps only → Yahoo (existing behavior, unchanged)
  │       └─ Persist new slices locally (./warehouse/warehouse.sqlite) and update coverage
  └─ (3) Read full requested trading-day range from Warehouse → return to Calculations

Responsibilities by layer
- Calculations (unchanged): Consume data exactly as before; unaware of Warehouse.
- Data Access Boundary (existing): Remains the single point that supplies data to calculations.
- Warehouse (new):
  • Understands which trading-day dates are already stored (“coverage”).
  • Detects gaps between requested trading-day dates and stored trading-day dates.
  • Persists newly fetched slices and updates coverage in the embedded SQLite file.
  • Serves the complete requested trading-day range back to the Data Access Boundary.
- Yahoo (existing): Source of truth for any missing slices; invocation parameters remain exactly as they are today.

Trading-day awareness (authoritative rules)
- Coverage is defined only over trading days. Non-trading days (weekends, US market holidays, exchange-wide closures) are not part of coverage and never constitute “missing data.”
- The authoritative notion of “which days are trading days for a given ticker” is the same one implicit in today’s data path (i.e., the daily rows Yahoo actually returns for that ticker). Do not introduce a new or different calendar.
- When a request spans non-trading days, those dates are ignored by gap detection; no Yahoo calls are made for them; no synthetic rows are created.
- For tickers listed on different exchanges (NYSE, NASDAQ, etc.), coverage aligns with how today’s product receives daily data for that specific ticker from Yahoo (per-ticker reality, not a global calendar).
- “Today” handling follows the current product behavior. If today is a non-trading day, there is nothing to fetch. If today is a trading day and currently considered incomplete, only the tail is refreshed according to the existing semantics, without changing interfaces or parameters.

Request lifecycle (authoritative sequence)
1) Receive request for specific tickers and a date range.
2) Map the requested range to the trading-day dates that the current system expects for each ticker (same semantics as today).
3) Inspect Warehouse coverage for those trading-day dates in ./warehouse/warehouse.sqlite.
4) Compute missing trading-day sub-ranges (if any).
5) Fetch only those missing trading-day sub-ranges from Yahoo using the same request pattern the system uses today.
6) Persist newly fetched slices to the embedded SQLite Warehouse and update coverage to include those trading-day dates.
7) Load the entire requested trading-day range from Warehouse.
8) Return data in the current contract (same shape, ordering, and types).
9) Calculations run unmodified and produce outputs as today.

Freshness (policy level, calendar-aware)
- If a request includes very recent dates, apply the same “recent tail” refresh behavior the product uses today, restricted to trading-day dates only.
- Freshness policy must not change interfaces or Yahoo parameters and must not cause calls for non-trading days.

Error handling & fallbacks
- If Warehouse read fails: fall back to Yahoo for the necessary trading-day dates; do not block calculations.
- If Yahoo fetch fails for a missing trading-day slice: return the same error behavior the system has today (no new error shapes).
- Warehouse must not introduce partial or altered outputs; either it supplies the exact contract or defers to the existing path.

Observability (minimal, decision-focused)
- Counters: warehouse_hit, warehouse_miss, yahoo_calls, missing_range_segments, calendar_skipped_days.
- Timings: read from Warehouse, Yahoo fetch, persist, end-to-end.
- Disk: optional metric for database size at ./warehouse/warehouse.sqlite.

Rollout & control
- A single feature flag enables/disables the Warehouse path end-to-end.
- With the flag OFF, the system behaves exactly as it does today.
- Staged enablement is recommended; compare outputs with Warehouse OFF to confirm bit-for-bit identity.

Non-goals
- No changes to calculation logic or its inputs/outputs.
- No changes to Yahoo client semantics or parameters.
- No introduction of synthetic non-trading-day rows.
- No external database servers or services.

Success criteria
- Identical outputs vs. today for the same inputs.
- Reduced Yahoo calls on repeated or overlapping trading-day ranges.
- Faster responses when ranges are fully covered locally.
- The database file is used at ./warehouse/warehouse.sqlite (in-repo, single-file, embedded).
