# Decisions and unresolved assumptions

Status labels: ACCEPTED_DESIGN means intended project behavior, not implemented; OPEN needs resolution; VERIFIED needs evidence.

ADR-001 — ACCEPTED_DESIGN: Track 1, FAULTLINE, single mechanism of gap-driven ingestion. This supersedes CasePath as the recommendation. User requested this agent handoff pack; no application build has been completed.

ADR-002 — OPEN, T00/T02: HydraDB access and dialect. Prefer an organizer-supported property-graph endpoint if available. Otherwise use the repository engine on a proven local WSL/Linux runtime. Record actual endpoint family, version/commit/image, auth method, query examples, errors, consistency behavior, and smoke output. Do not treat hosted memory search as the required graph implementation. No credentials or runtime access are confirmed.

ADR-003 — OPEN, T05: provenance representation. Use reified DependencyClaim nodes as authority. Either traverse them directly or materialize direct edges only with an explicit committed-claim gate and reconciliation. Pick the simplest verified query shape. Document any dual-write failure boundary.

ADR-004 — ACCEPTED_DESIGN: deterministic structural core; LLM prose optional and later. No need for an LLM API to begin developing contracts, fixtures, and evaluation. Provider, model, and spending cap are OPEN if adding one.

ADR-005 — ACCEPTED_DESIGN: Python backend/evaluation by default, React/TypeScript optional. T00 confirms installed toolchain; a different familiar stack can be recorded before substantial code. No Python/library version has been inspected or installed yet.

ADR-006 — ACCEPTED_DESIGN: use development pilots for the go/no-go gate; final holdout remains untouched until protocol freeze. Fixed graph snapshot scoring disallows fresh inspection during held-out diagnosis v1.

ADR-007 — ACCEPTED_DESIGN: six learning incidents plus round 0 yield seven evaluated snapshot points. Three fixed seeds desired; report actual counts. Budget constants remain OPEN until development calibration.

ADR-008 — OPEN, T00: remaining hackathon time, submission format, exact cutoff, organizer-approved access, and synthetic-data policy. Supplied event dates are November 14–16, 9 AM IST, 2026. Do not infer that the full 48 hours remain now.

ADR-009 — ACCEPTED_DESIGN: isolated sandbox only; no automatic production remediation. Human/demo controller restores configuration. No secret values enter graph evidence.

ADR-010 — ACCEPTED_DESIGN: docs are a navigation contract; executable truth and observed outputs override stale progress claims. If code conflicts with design, investigate and record a decision rather than silently rewriting acceptance criteria.

## New decision template
ID / date / status / concrete question / alternatives / chosen option / reason / evidence paths / affected tasks / validation / limitations.

Routine reversible choices within scope can be resolved autonomously and recorded. A material product or evaluation change requires clearly notifying the user; no elapsed wait counts as approval when approval is actually necessary. Required tool approval boundaries remain in force.

ADR-002 — VERIFIED 2026-11-14: selected the repository-engine HTTP API, official
release 0.4.0, commit 916637477f3f34766b4905b270bd4292109d77e6,
image ghcr.io/hydra-db/hydradb@sha256:ab71d651fefee13ebb23eb56d72316065bdca563ff7587442e07be663f2bf880.
Isolated Docker container faultline-hydra, Windows bind-mounted local store;
query port 127.0.0.1:18443, admin 127.0.0.1:19090. Random local bearer token
in ignored .runtime/hydra/auth-token; configure HYDRADB_TOKEN_FILE locally.
No hosted credentials required. scripts/start_hydra.py creates needed directories.
First start failed because store directory did not exist; preserved in artifacts.
Evidence: artifacts/hydra-smoke/image.txt, runtime.log, responses.json,
smoke-retry.log and adapter-tests.log. Multi-hop typed directed MATCH, MERGE,
label-anchored node read, SET update, immediate read-after-write and repeated
idempotent seed verified live. Fixed templates carry parameters, timeout_ms,
page_size and LIMIT for reads. Adapter rejects pagination, overflow, malformed
responses and HTTP failures; does not silently truncate. No transaction or
historical snapshot support inferred. Source docs captured from same commit.

ADR-005 — VERIFIED 2026-11-14: Windows Python 3.12.10; Pydantic 2.12.5,
pytest 9.0.3 and setuptools 80.9.0 installed in workspace .venv. Exact installed
versions in requirements.lock. Public payloads are strict allowlisted DTOs;
raw evidence is typed config-access telemetry with config identity and no values.

ADR-003 — VERIFIED 2026-11-14: reified Claim nodes are authoritative. Traverse
Entity <-FROM_ENTITY- Claim -TO_ENTITY-> Entity and join SUPPORTED_BY Evidence
in HydraDB. Fixed one/two/three-domain-edge templates passed live (including
reverse directed hops and comma evidence joins). No materialized dependency graph.
Pending claims and a durable application snapshot manifest both gate visibility.
No transaction is assumed; ownership IDs are journaled before writes. Interrupted
writes can be retried with the same deterministic keys. Experiment namespaces use
SHA-256-derived 48-bit IDs with per-manifest collision checking; no global scans.
Source version mismatches require a new experiment. Evidence: T05-green.log.
Development pilots monitor checkout/renewals and refunds/renewals respectively;
all real flows still execute and telemetry is collected, with public monitoring
scopes disclosed in the private pilot definitions. Holdout uses all endpoints.

ADR-011 — VERIFIED 2026-11-14: development transfer gate passed. A monitors
checkout and healthy renewals; B monitors refunds and healthy renewals. They use
different fault values and workloads. At snapshot 0, B abstained for insufficient
evidence. One budgeted shared-service telemetry inspection during A learned
pricing READS_CONFIG currency (and billing READS_CONFIG billing). B then selected
config:currency through endpoint:refunds -> service:refunds -> service:pricing ->
config:currency with returned claim/evidence IDs. Snapshot contents stayed fixed
during B diagnosis. Evidence: artifacts/pilot-transfer/result.json and T12-pilot.log.
This is a small controlled development transfer demonstration, not held-out
accuracy or a claim of general incident diversity. UI is now eligible after its
remaining dependencies; evaluation freeze and failure gates still required.

ADR-008 update — USER-CONFIRMED 2026-11-14: submission is tomorrow,
November 15, 2026 IST. Exact cutoff time and submission format have not been
provided by the organizer. This supersedes the initial supplied November 14–16
schedule as the working delivery date. Do not invent remaining hours or mark
submission complete. Continue local implementation and prepare a fallback.

ADR-012 — VERIFIED 2026-11-14: chose the Python standard-library loopback HTTP
server for the small local public API; FastAPI was a proposal and not required.
No extra backend framework or agent framework was added. Controls are bounded
sandbox operations with explicit DTOs, loopback Host checks and same-origin
write headers. Integration and headless UI checks verify the actual workflow.

ADR-013 — VERIFIED 2026-11-14: user explicitly authorized Playwright with its own
browser after unreliable desktop browser controls. Headless Chromium in the
pinned official Playwright 1.65.2 Linux container passes UI checks without active
desktop input. A temporary signed Chrome headless instance also exposed real UI
failures, preserved in artifacts. Native Computer Use was stopped and reset.
No screen-capture privacy settings or managed restrictions were weakened.

ADR-014 — USER-RELAYED 2026-11-15: host clarified that Track 1 must use the
self-run open-source repository engine, judging is equally technical and
go-to-market, and submission requires a usable live link, public GitHub repo,
and Loom walkthrough. Technical emphasis is a meaningful metric, continual
improvement against a baseline, and an actual contribution from HydraDB graph
traversal. Go-to-market asks for social posts tagging HydraDB and evidence of a
plausible paying buyer. These are requirements relayed by the user, not a
completed publication or independently confirmed organizer page. The pinned
0.4.0 repository engine already satisfies the database choice. Exact cutoff,
hosting account, GitHub identity and Loom upload remain unconfirmed.

ADR-015 — VERIFIED 2026-11-15: bounded public demo mode accepts one exact HTTPS
origin configured at launch; all other remote Host headers are rejected. Remote
writes require a matching Origin and the existing narrow control header. Default
binding and Host checks remain loopback-only. The actual remote-host workflow
through trigger, diagnose and learn passed tests/integration/test_public_api.py.
This mode still needs a live host and an external end-to-end check before any
public URL can be called usable. Shared sandbox state and demo-only access are
limitations; it is not a production multi-user service.
