# Architecture and implementation contracts

Status: historical design contract, written before implementation. Names and signatures below are application-owned specifications, not claims about existing HydraDB or third-party APIs. The implemented architecture and runnable commands are documented in [README.md](../README.md#architecture-at-four-levels). In particular, the project now requires Python 3.12+, uses the standard-library HTTP server and buildless frontend, and tests the pinned HydraDB repository engine. Earlier framework and CLI suggestions below remain design history, not claims that those interfaces exist.

## Component map

Sandbox app -> public observations -> investigator -> HydraDB adapter -> bounded subgraph
                                      |                    ^
                                      v                    |
                                gap selector -> inspector -> parser/validator

Private fault controller -> sandbox mutation
Private evaluator <- expected origin + public diagnosis
Read-only UI <- public observations, diagnosis, graph paths, evaluation aggregates

The controller/evaluator can access private scenario manifests. Investigator and inspector cannot. Use narrow DTOs, separate construction of public/private views, and tests that record every investigator input. Do not give an LLM the implementation workspace or private evaluator files.

## Proposed source layout (create incrementally)

src/faultline/contracts.py                  public records and validation
src/faultline/sandbox/                      flows, config reads, checks
src/faultline/graph/adapter.py               chosen HydraDB transport boundary
src/faultline/graph/queries/                fixed verified query templates
src/faultline/graph/store.py                 domain persistence and graph projection
src/faultline/ingestion/                    source catalog, inspector, parser
src/faultline/diagnosis/                    candidate ranking, explanation, gaps
src/faultline/learning/                     inspect/validate/commit orchestration
src/faultline/api.py                        public backend routes
src/faultline/cli.py                        doctor, reset, diagnose, learn, evaluate
src/faultline/evaluation/                   private orchestration and scorers
fixtures/public/                           public topology and evidence sources
fixtures/private/                          gold scenarios, never served publicly
protocol/                                  split, budgets, seeds, frozen hashes
web/                                       minimal UI
scripts/                                   repeatable setup/verification wrappers
artifacts/                                 generated redacted runtime/eval output

File tree is a plan, not evidence files exist. Unit tests may use tiny fixtures, but integration tests must use actual HydraDB and cannot silently fall back to a dictionary or another graph database.

## Public records
All IDs are stable application strings. If the chosen engine needs integer vertex IDs, persist a deterministic ID manifest within safe integer bounds; check collisions. All timestamps are explicit UTC integers supplied by scenario/runtime, never inferred from filenames.

Observation: observation_id, observed_at_ms, endpoint_id, status (healthy/failing/unknown), symptom_code, message, evidence_id.
ChangeRecord: change_id, changed_at_ms, target_entity_id, public_summary, evidence_id. These are realistic observed changes, including distractors, not fault labels.
EvidenceSource: source_id, owner_service_ids, kind, source_version, sha256, estimated_bytes, inspected state. Catalog metadata must not disclose parsed hidden dependencies or the expected root.
EvidenceRecord: evidence_id, source_id, sha256, source_version, observed_at_ms, byte_range/record locator, raw payload. Redact secret values, preserve config-key identity.
DependencyClaim: claim_id, from_id, relationship_type, to_id, evidence_id, source_version, learned_round, valid state. Only allowlisted relationships and known identifiers are accepted.
Diagnosis: investigation_id, snapshot_manifest_hash, ranked_candidates, selected_origin_id or null, status (supported/ambiguous/insufficient_evidence/error), explanation_paths, evidence_ids, gap_reason, timing. Never present a numeric probability unless calibrated.
InspectionBudget: max_sources, max_bytes, max_records, timeout_ms. Charge attempts and returned bytes; rejected/failed attempts remain in the ledger.

## Logical graph
Endpoint HANDLED_BY Service; Service CALLS Service; Service READS_CONFIG ConfigKey; Change MODIFIES ConfigKey/Service; Symptom OBSERVED_AT Endpoint.

Relationship provenance is represented by DependencyClaim nodes: Claim FROM_ENTITY entity, Claim TO_ENTITY entity, Claim SUPPORTED_BY Evidence. A verified direct dependency edge may accelerate traversal, but it is active only when a committed claim and evidence support it. Return claim/evidence IDs with explanation paths. This avoids pretending a relationship can itself be the endpoint of another relationship.

Prefer one authoritative representation if dual-writing proves risky: traverse reified Claim hops directly. Choose and record in ADR-003 during T05. Account for reified hops in query bounds. Do not maintain two inconsistent graphs.

## Initial graph and learning
Seed all public service/endpoint/config identities and legitimately known call/handler links. Configuration-read relationships start unobserved because that source class has not been ingested; disclose this. Initial omissions follow a frozen evidence availability policy, not a handpicked wrong-answer script. Preserve healthy observations. Source inspection emits real READS_CONFIG relationships from config access telemetry or explicit references.

Graph-derived topology uses the app source version. On app reset restore scenario runtime state without erasing learned topology; on experiment reset restore the defined learning snapshot as well. These are different commands with different target scopes.

## Ranking v1
Candidates are publicly observed recent change targets in the fixed time window; include all such targets, not only the hidden fault. Add directly failing services when no change evidence exists. HydraDB retrieves bounded paths from observed endpoints through handler/call/read dependencies to candidates. Application code computes distinct failing endpoints explained, healthy endpoints contradicted, recent-change eligibility, and path length. Deduplicate endpoints before counting.

Rank by descending failing coverage, ascending healthy contradictions, then shortest path. A stable ID orders output only; it must not resolve evidential ties. Return ambiguous for equal best evidence scores. Return insufficient_evidence when no candidate has a supporting path or retrieval is incomplete. Graph reachability is a heuristic; no claim of causal proof. Fix this algorithm before evaluation; no learned weights in the MVP.

## Gap selection v1
Trigger on insufficient evidence, tied candidates, or a failing service with no inspected configuration evidence. Select an unseen source associated with the unresolved failing services; prioritize number of unresolved services covered, then smaller estimated size, then stable source ID. This policy uses public source metadata only. Treat the first test as an experiment: it may fail to outperform random.

Enforce the same attempts/byte/record limits for adaptive and random ingestion. Parser output must match actual source content and known IDs. Persist evidence and claims idempotently before making them query-visible. Skip an already ingested source hash. If a partial multi-request write occurs, mark the ingestion incomplete and prevent that claim from contributing until reconciliation succeeds. Do not assume multi-request transactions exist.

## Snapshots and freshness
A snapshot is an immutable application manifest of seed hash, source hashes, active claim IDs, source version, and learning round. A server read epoch/bookmark is diagnostic consistency metadata, not automatically a portable historical snapshot. Isolate/reseed application snapshots using capabilities proven on the selected interface. Poll or honor proven read-your-writes mechanisms. Do not guess timestamp-as-of syntax.

## Proposed CLI contract
python -m faultline doctor; reset --scope sandbox|experiment; diagnose --case PUBLIC_ID; learn --case LEARNING_ID; evaluate --protocol PATH; serve.

This is a proposed interface contract, not a claim that every command is implemented. Use the runnable commands in README.md and the scripts directory; verify behavior from recorded artifacts.

## API/UI boundary
The public API exposes health, current app observations, investigations, allowlisted source inspection, current explanation subgraph, and aggregate benchmark artifacts. Fault controls are local developer/demo controls restricted to the sandbox. No private manifests, arbitrary Cypher, shell commands, credential values, or arbitrary file paths are exposed. The UI renders backend-returned paths, not a separately invented topology. Missing benchmark output means omit the chart until real data exists.
