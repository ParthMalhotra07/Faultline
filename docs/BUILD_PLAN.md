# Build plan and dependency map

All implementation tasks are unfinished at handoff creation. File paths below are proposed outputs, not pre-existing files. Read STATE.json for current statuses, then verify them against disk and recorded checks.

## Scheduling

Work in task-number order among tasks whose dependencies are DONE. If a prerequisite is BLOCKED, continue ready independent tasks; do not simulate completion. Exactly one task may be IN_PROGRESS. Dependencies form a DAG, not a requirement to run parallel agents. No sub-agent delegation is requested by this pack.

### P0 — Feasibility (Hours 0–3)

Gate G0: actual HydraDB multi-hop/update/read evidence, T02. Independent skeleton work can continue if access is blocked.

### P1 — Executable world (Hours 3–8)

Gate G1: real failing checks, private labels isolated, T04.

### P2 — Evidence and graph (Hours 8–12)

Provenance, bounded inspection, ingestion and draft evaluation contracts.

### P3 — Headless transfer (Hours 12–21)

Gate G2: evidence-backed transfer on development pilots, T12. No UI before this gate.

### REST — Rest and contingency (Hours 21–27)

Protect sleep. Use actual remaining time on resumption.

### P4 — Evaluation integrity (Hours 27–34)

Gate G3: frozen protocol and reproducible actual held-out results, T16.

### P5 — Presentation and load (Hours 34–41)

Display measured paths/results; keep optional explanation work small.

### P6 — Rehearsal and package (Hours 41–48)

Gate G4: clean start, recording and real submission-ready artifacts, T23.

## Task dependency summary

- T00 ← start — Environment and project boundary
- T01 ← T00 — Project skeleton and public contracts
- T02 ← T00 — Live HydraDB feasibility proof
- T03 ← T01 — Executable commerce flows
- T04 ← T03 — Private fault controller and public observations
- T05 ← T01, T02 — HydraDB domain schema and seed
- T06 ← T04 — Evaluation harness and split draft
- T07 ← T01, T03, T04 — Budgeted source catalog and inspector
- T08 ← T05, T07 — Verified evidence-to-graph ingestion
- T09 ← T04, T05 — Graph diagnosis and evidence paths
- T10 ← T07, T09 — Gap detector and targeted source selection
- T11 ← T08, T09, T10 — One complete headless learning round
- T12 ← T06, T11 — Development transfer go/no-go gate
- T13 ← T06, T07, T12 — Fair baseline runners
- T14 ← T08, T11, T12 — Failure handling and no-leakage checks
- T15 ← T06, T12, T13, T14 — Freeze final experiment protocol
- T16 ← T15 — Held-out curve and graph ablation
- T17 ← T12, T14 — Public API for demo and investigations
- T18 ← T17 — Minimal live graph investigation UI
- T19 ← T16, T18 — Measured comparison and trace replay
- T20 ← T14 — Bounded retrieval load evidence
- T21 ← T12 — Optional LLM explanation layer
- T22 ← T16, T19, T20 — Clean-start documentation and buyer pitch
- T23 ← T22 — Rehearsal and submission-ready package

## Task cards

### T00 — Environment and project boundary

Phase: P0. Depends on: none. Required.

Expected outputs: artifacts/preflight.md.

Build: Inspect actual OS/Python/Node/WSL or Docker, network and version-control boundary. Detect credential presence without displaying values. Record remaining time and missing organizer details. Do not modify ReliefGrid or assume its dependencies.

Acceptance: Redacted preflight lists available tools with real version output, blockers, chosen workspace, and concrete next commands. No application completion claimed.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T01 — Project skeleton and public contracts

Phase: P0. Depends on: T00. Required.

Expected outputs: pyproject.toml; src/faultline/contracts.py; tests/unit/test_contracts.py.

Build: Create a minimal package and meaningful tests for public records, ID validation, secret redaction and unknown fields. Choose/pin compatible runtime dependencies only as needed.

Acceptance: Package imports; public/private record boundary rejects extra private data; actual test command and output recorded.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T02 — Live HydraDB feasibility proof

Phase: P0. Depends on: T00. Required.

Expected outputs: scripts/graph_smoke.py; src/faultline/graph/adapter.py; artifacts/hydra-smoke/.

Build: Choose and pin one actual HydraDB interface in ADR-002. Build a tiny write/multi-hop/update/read proof with idempotent reseeding, timeouts and explicit error decoding. If blocked, record credentials/runtime missing; work on independent tasks.

Acceptance: A real database round trip succeeds and repeating seed creates no duplicate logical edges. Multi-hop read sees committed updates. Raw redacted responses and tested query forms saved. A mock cannot pass this task.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T03 — Executable commerce flows

Phase: P1. Depends on: T01. Required.

Expected outputs: src/faultline/sandbox/flows.py; src/faultline/sandbox/config.py; tests/integration/test_sandbox.py.

Build: Implement checkout, refunds and renewals with real shared config reads. Emit bounded structured config-access records with source versions and no secret values. Add healthy checks and a sandbox-only reset command.

Acceptance: All healthy checks pass; endpoints/functions depend on actual config values; reset returns the same healthy state. At least two flows share one dependency and one counterexample stays unaffected.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T04 — Private fault controller and public observations

Phase: P1. Depends on: T03. Required.

Expected outputs: src/faultline/evaluation/controller.py; fixtures/private/; fixtures/public/; tests/integration/test_fault_isolation.py.

Build: Implement real local mutations and acceptance checks. Produce public observations/change records including distractor changes. Keep injected labels/controller parameters private. Separate development, learning and held-out manifests.

Acceptance: Each scenario changes actual behavior and restores cleanly. Public DTOs expose no gold labels or fault manifest. Cases are reproducible; multiple-fault cases are excluded from v1 unless explicitly specified.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T05 — HydraDB domain schema and seed

Phase: P2. Depends on: T01, T02. Required.

Expected outputs: src/faultline/graph/store.py; src/faultline/graph/queries/; fixtures/public/topology.json; tests/integration/test_graph_store.py.

Build: Resolve ADR-003. Seed known identities/topology and evidence-backed claims using live tested templates. Implement a content manifest and isolated experiment reset. Do not mark unknown config edges as observed.

Acceptance: Repeated seed is idempotent; provenance is retrievable; initial topology omission policy is explicit; reset targets only the configured FAULTLINE scope; no direct edge bypasses a required verified claim.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T06 — Evaluation harness and split draft

Phase: P2. Depends on: T04. Required.

Expected outputs: src/faultline/evaluation/scoring.py; protocol/draft/; tests/unit/test_scoring.py.

Build: Implement origin scoring, abstention/error counts, private/public views and a draft 6-learning/12-held-out split. Add development-only pilot cases. Final holdout is not run yet.

Acceptance: Known fixtures prove correct denominators and error treatment. Different splits and runtime inputs are distinguishable. Draft IDs and acceptance outcomes recorded without public label exposure.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T07 — Budgeted source catalog and inspector

Phase: P2. Depends on: T01, T03, T04. Required.

Expected outputs: src/faultline/ingestion/catalog.py; src/faultline/ingestion/inspector.py; tests/unit/test_inspector.py.

Build: Serve allowlisted actual telemetry/artifacts. Limit attempts, bytes, records and time. Catalog carries only permissible service ownership/size metadata. Reject arbitrary paths, private files, and unsupported source versions.

Acceptance: Inspections enforce every limit, ledger failures, redact secrets and cannot read private manifests. Catalog metadata does not directly disclose expected diagnosis or pre-parsed hidden relationships.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T08 — Verified evidence-to-graph ingestion

Phase: P2. Depends on: T05, T07. Required.

Expected outputs: src/faultline/ingestion/parser.py; src/faultline/ingestion/commit.py; tests/integration/test_ingestion.py.

Build: Parse structured sources into allowlisted relationships and persist evidence/claims idempotently. Reconcile interrupted writes. Mark claims current only after all required durable pieces exist.

Acceptance: A real observation produces a query-visible justified edge; fabricated/malformed claims are rejected; repeat ingestion is harmless; interruption leaves no verified phantom relationship.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T09 — Graph diagnosis and evidence paths

Phase: P3. Depends on: T04, T05. Required.

Expected outputs: src/faultline/diagnosis/ranker.py; src/faultline/diagnosis/paths.py; tests/integration/test_diagnosis.py.

Build: Implement bounded HydraDB retrieval and architecture ranking v1 with distinct endpoint counts, healthy contradictions and explicit ties. Return supporting claim/evidence IDs.

Acceptance: Hand-checkable pilot graph gives expected ranks; tied evidence returns ambiguous; disconnected graph abstains; timeout/truncation/error never becomes a successful empty result.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T10 — Gap detector and targeted source selection

Phase: P3. Depends on: T07, T09. Required.

Expected outputs: src/faultline/diagnosis/gaps.py; src/faultline/learning/selector.py; tests/unit/test_selector.py.

Build: Implement public-metadata-only gap policy and deterministic source selection. Do not use evaluator labels or a handcoded correct source per case.

Acceptance: Development examples select according to the declared policy; inspected hashes are not recharged/reingested; ties and source exhaustion are explicit. Same inputs yield same selection.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T11 — One complete headless learning round

Phase: P3. Depends on: T08, T09, T10. Required.

Expected outputs: src/faultline/learning/runner.py; src/faultline/cli.py; tests/integration/test_learning_round.py.

Build: Connect diagnose -> gap -> inspect -> validate -> commit -> new snapshot -> revised diagnosis. Add experiment reset separately from sandbox reset. Save round traces and manifests.

Acceptance: From a clean database one actual incident executes the complete loop with recorded budget/evidence/graph update. Restarting the application retains committed learning; reset scopes behave differently and correctly.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T12 — Development transfer go/no-go gate

Phase: P3. Depends on: T06, T11. Required.

Expected outputs: artifacts/pilot-transfer/; docs/DECISIONS.md.

Build: Use only development pilots: learn on incident A, diagnose genuinely different incident B with snapshot 0 and snapshot 1. Explain exactly which new relationship affected B. Investigate honest failures before adding UI.

Acceptance: At least one different pilot benefits for an evidence-backed structural reason, without label leakage, a hardcoded bad first answer or larger diagnosis budget. Record failures too. If not achieved, gate remains open and report a focused design issue.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T13 — Fair baseline runners

Phase: P4. Depends on: T06, T07, T12. Required.

Expected outputs: src/faultline/evaluation/baselines.py; tests/integration/test_budget_parity.py.

Build: Implement frozen and random-ingestion methods with matched catalog/budget and fixed seeds. Prefer a same-evidence text/semantic retriever before polish; label the actual algorithm precisely.

Acceptance: Same scenario inputs/context budgets and source access for each method; actual and capped costs saved. Frozen graph never learns. Random runs reproducibly. Any missing text baseline remains an explicit limitation.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T14 — Failure handling and no-leakage checks

Phase: P4. Depends on: T08, T11, T12. Required.

Expected outputs: tests/integration/test_failure_modes.py; tests/integration/test_no_leakage.py.

Build: Exercise malformed records, duplicate sources, interrupted writes, stale evidence, unavailable database, truncated results, reset/restart, and private/public DTO boundaries.

Acceptance: Focused failure checks pass against real HydraDB where relevant; learner inputs are captured and audited; incomplete reads do not produce supported diagnoses; no unredacted credential appears in artifacts.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T15 — Freeze final experiment protocol

Phase: P4. Depends on: T06, T12, T13, T14. Required.

Expected outputs: protocol/v1/; artifacts/protocol-freeze.json.

Build: Choose remaining constants on development data; freeze splits, budgets, ranking, seeds, evidence policy and source versions with hashes. Record remaining time. No final holdout tuning.

Acceptance: Protocol manifest is complete, reproducible and immutable for the final run; six learning incidents yield seven snapshot points including round 0. This task records hashes and date before T16 starts.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T16 — Held-out curve and graph ablation

Phase: P4. Depends on: T15. Required.

Expected outputs: artifacts/eval/; src/faultline/evaluation/report.py.

Build: Run actual read-only held-out evaluations at each frozen snapshot across required baselines. Verify state hashes; run structural ablation. Preserve all points, errors, seeds and failed runs.

Acceptance: Raw predictions reproduce aggregate counts; holdout cannot write learner state; complete curve includes errors/abstentions; structural effect and acquisition effect are separately discussed. No requirement to fabricate improvement if results disappoint.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T17 — Public API for demo and investigations

Phase: P5. Depends on: T12, T14. Required.

Expected outputs: src/faultline/api.py; tests/integration/test_public_api.py.

Build: Expose health, public observations, investigations, returned graph paths and sanitized results. Isolate local fault controls. Do not expose arbitrary Cypher, files, shell or private labels.

Acceptance: API contract tests pass; public endpoints cannot retrieve private scenarios or secrets; errors are distinct from empty data; controls affect sandbox only.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T18 — Minimal live graph investigation UI

Phase: P5. Depends on: T17. Required.

Expected outputs: web/.

Build: Render three panels: app health, investigation/evidence, actual HydraDB subgraph. Add reset/trigger/investigate/restore controls with explicit states. No invented graph topology.

Acceptance: A browser run completes the real local workflow. Nodes/edges correlate to backend IDs and committed evidence. Failed calls show explicit errors. Build/type checks run and visual behavior inspected.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T19 — Measured comparison and trace replay

Phase: P5. Depends on: T16, T18. Required.

Expected outputs: web/; artifacts/demo/.

Build: Render the real held-out results with labeled axes, method legend, counts and protocol caption. Add recorded-run replay clearly distinguished from live investigation.

Acceptance: Every displayed numeric result can be traced to raw artifacts. Chart contains actual measured rounds and no invented values. Replay/live status is visible.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T20 — Bounded retrieval load evidence

Phase: P5. Depends on: T14. Required.

Expected outputs: scripts/load_retrieval.py; artifacts/load/.

Build: Run separate 1/5/10-client graph tests on labeled generated data and the actual deployment. Record request counts, hardware, limits, throughput, p50/p95, errors, cold/warm state and update visibility.

Acceptance: Actual raw timings/summary and commands saved. Scale claim states graph size and test limits. LLM work and diagnostic accuracy are not conflated with retrieval load.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T21 — Optional LLM explanation layer

Phase: P5. Depends on: T12. Optional.

Expected outputs: src/faultline/diagnosis/explainer.py; tests/unit/test_explainer.py.

Build: Optional only after transfer gate: format deterministic candidate/evidence output or choose among bounded inspections. Model must not override structural scoring or invent citations. Record model/prompt/cost cap if enabled.

Acceptance: Explanation references only returned evidence and preserves ambiguity; missing key has a deterministic fallback. Can be SKIPPED with reason. No impact on held-out scoring without a new protocol.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T22 — Clean-start documentation and buyer pitch

Phase: P6. Depends on: T16, T19, T20. Required.

Expected outputs: README.md; scripts/verify_demo.*; docs/DEMO.md.

Build: Write only commands actually implemented and verified. Pin dependencies, add setup/reset/evaluate/demo instructions, results, source citations and limitations. Prepare a shadow-mode buyer pitch.

Acceptance: A clean environment or isolated fresh app scope reproduces setup and one demo. Another agent can map each result to artifacts. No API key or fabricated customer quote in package.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

### T23 — Rehearsal and submission-ready package

Phase: P6. Depends on: T22. Required.

Expected outputs: artifacts/submission/; HANDOFF.md; STATE.json.

Build: Rehearse three-minute script, record fallback, verify organizer requirements and confirmed deadline. Assemble required links/files. Resolve or explicitly list open limitations. Publication/upload only when separately authorized or already explicitly in scope.

Acceptance: Live/reset/replay runs verified; package checklist complete; actual files/links present; final report states measured results and limitations. Do not mark submitted unless a real submission confirmation exists.

Completion evidence: exact executed command(s), exit status, redacted output path, inspected artifact(s), and relevant remaining limitations in STATE.json.

## Gate failure and scope cuts
If G0 is blocked, record missing access and continue sandbox/contracts/evaluation work; do not claim the integration exists. Ask the organizer/user for the exact missing credential or runtime support without requesting secret values in chat.

If G2 fails, inspect development evidence and adjust one design choice at a time. Record changes and re-run pilots. Do not unlock UI work or touch final holdout to find a prettier demonstration. If actual remaining time forces a cut, notify the user and record a narrower honest scope; G2 failure is not permission to fabricate transfer.

Before T15, reduce to two flows/two resources/six held-out cases if necessary and record the amendment. After protocol freeze, do not silently shrink the denominator or redefine success. Extra LLM prose, animations, containerization and integrations are first to cut. T21 can be explicitly SKIPPED and does not block required completion.

At T23 complete a submission-ready package. Submission itself requires an actual confirmation and must not be inferred from prepared artifacts.

### T24 — Adapt Origyn frontend design for FAULTLINE

Phase: P6. Depends on: T19, T22. Required by the user's November 15 design request; T23 remains blocked on external public-delivery prerequisites.

Build: Inspect the user's Origyn frontend at github.com/ParthMalhotra07/origyn. Bring its workspace layout, restrained dark palette, typography, navigation and evidence-graph treatment into FAULTLINE while keeping FAULTLINE identity, real HydraDB responses, existing sandbox controls and measured evaluation artifacts. Do not import Origyn's backend, mock data, research-domain workflows, or evaluation labels.

Acceptance: Real trigger → abstain → bounded learn → restore → transfer remains usable; actual returned graph nodes/edges and measured counts render; replay stays labeled; desktop and mobile layouts are readable; no unexpected console/page errors. Capture and inspect rendered screenshots. Record source reference commit and actual test output. Rebuild the demo image if frontend assets are packaged there.

Completion evidence: exact commands, exits, browser report/screenshots, changed files and remaining limitations in STATE.json and HANDOFF.md. Do not treat T23's public-host blockers as solved by a visual change.

### T25 — Prepare Railway Docker deployment

Phase: P6. Depends on: T24. Required by the user's November 15 Railway decision.

Build: Keep `Dockerfile.demo` and the bundled self-run HydraDB engine. Permit Railway's documented healthcheck Host only for a read-only health route, preserve Host and same-origin restrictions elsewhere, and document exact Railway dashboard settings and post-deploy validation commands. Keep the GitHub repository private until the user changes visibility.

Acceptance: A failing test demonstrates the healthcheck issue, then a passing test proves its narrow fix. Rebuild the bundled image and exercise the real graph workflow through a fresh local container with a durable `/data` volume, including restart persistence and a Railway-style health request. Do not claim a Railway deployment without its URL and actual remote checks.

Completion evidence: exact commands, exits, local container output, changed files, and remaining public-delivery limitations in STATE.json and HANDOFF.md.

### T26 — Restore the Origyn-style landing experience

Phase: P6. Depends on: T24, T25. Required by the user's correction to the frontend request.

Build: Make the root URL a FAULTLINE landing page that preserves Origyn's large hero, animated particle field, staged scroll reveals, live product preview, capability-section rhythm and closing workspace CTA. Remove Origyn research features that FAULTLINE does not implement. Keep the verified incident workspace at `/workspace` and retain its real HydraDB/API interactions. All displayed live facts must come from FAULTLINE's public API; schematic sections must be labeled as explanation, not live results.

Acceptance: Root landing and workspace routes both work in the selected Docker image; landing CTAs navigate to the working demo; live preview matches public API responses; motion runs when enabled and respects reduced-motion preference; desktop and mobile render without page overflow or browser errors. The original nine workflow checks still pass from `/workspace`. Capture and inspect screenshots before DONE.

Completion evidence: exact commands, exits, browser report/screenshots, changed files and remaining limitations in STATE.json and HANDOFF.md. T23 remains blocked on public deployment and submission artifacts.

### T27 — Exploratory same-evidence vector-store comparison

Phase: P6. Depends on: T22, T26. Required by the user's November 15 request after the host emphasized HydraDB's value over a vector store. T23 remains blocked on final submission deliverables.

Build: Keep frozen protocol v1, its learned snapshots, raw predictions and `latest.json` unchanged. Use a local Qdrant vector store with a pinned published embedding model. Index only evidence records acquired in each adaptive snapshot. Query from the public incident DTO, rank only recent public candidates, preserve abstention and count all cases. Put experiment rules and code hashes in a separate exploratory protocol before reading results.

Acceptance: Verify the selected Qdrant/FastEmbed APIs with a live smoke test; run all 7 adaptive snapshot points across the 3 original seeds and 12 cases without learner access to gold labels. Record raw predictions, aggregate counts, exact versions, model/cache details, snapshot hashes, and limitations. Compare to v1 adaptive on the same cases only as a **retrospective exploratory** result; do not claim a fresh confirmatory holdout or general superiority over vector systems.

Completion evidence: exact commands, exits, protocol hash, raw output paths, unchanged v1 hashes, changed files and remaining limitations in STATE.json and HANDOFF.md.
