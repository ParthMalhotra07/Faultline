# Evaluation protocol and integrity rules

Status: protocol v1 is frozen and actual runs are preserved in artifacts/eval/. Use scripts/verify_evaluation.py to validate raw counts and unchanged snapshots. This document defines the protocol; README.md describes measured results and operational failures. No held-out tuning is authorized.

## Separate development, learning, and final evaluation
Use development pilot scenarios to debug selection/ranking and the headless go/no-go gate. The six learning scenarios allow evidence acquisition and verified operator feedback. The twelve held-out scenarios provide final scoring only. All share one disclosed app topology; hold out fault values, change combinations, and symptoms, not merely question wording. Verify scenarios actually differ and produce the intended checks.

Never use final held-out scores to tune ranking, source budgets, omission policy, or example selection. The implementation agent necessarily creates fixtures, so enforce runtime data-flow separation rather than claiming the developer has never seen labels. Audit the public payloads. A second experiment after tuning needs a new untouched holdout or must be labeled exploratory.

## Freeze protocol v1
Record app/source version, full scenario IDs and split, initial graph/evidence policy, public source catalog, ranking/abstention rule, 6 learning rounds (round 0 plus after each incident gives 7 snapshot points), source/byte/record/time budgets, random seeds, model/provider/version/prompt if used, context limits, and scoring definitions. Hash all files. Budget values must be chosen on development pilots and frozen; this document intentionally does not invent measured suitable limits.

A seed defines scenario order and random source selection. Start with three predeclared seeds if affordable; one seed is a pilot and reported as such. Do not silently replace a bad seed. Use one learning incident per round, one inspection per round initially; allow a different fixed budget only through the frozen protocol.

## Methods
1. Frozen: initial graph stays fixed at every learning round.
2. Adaptive: adds only evidence acquired by the gap selector under budget.
3. Random: inspects from the same available catalog, same order of incidents, same maximum attempts/bytes/records, with fixed random seeds. Record actual consumption as well as caps; smaller random sources must not quietly yield more inspections.
4. Same-evidence text/semantic retrieval: index precisely the evidence the adaptive method has accumulated, without graph links. Keep budget/context/model constant and record exact retriever implementation. Strongly preferred before visual polish; do not call keyword search a vector baseline.
5. Optional full-information graph: privileged ceiling, never a fair ordinary baseline.

Frozen versus adaptive measures acquired knowledge plus structure. Adaptive versus random measures acquisition policy. Same-evidence retrieval plus edge ablation measures graph structure. Do not conflate these conclusions.

## Per-snapshot test
Reconstruct an isolated graph from the frozen manifest. Reset sandbox to a healthy version, inject one held-out fault privately, run acceptance checks, construct public observations and public change records, diagnose read-only, and score the selected origin. Restore sandbox before the next case. Do not let evaluation ingest or update persistent learned claims. Record graph manifest before/after; hashes must match. Incident observations may be ephemeral or isolated per case.

Do not allow fresh diagnostic inspections during final held-out scoring v1; the graph snapshot is what is being measured. Learning-round inspections are charged separately. If interactive diagnosis is later measured, report it as a different protocol with matched per-case budgets for every method.

## Metrics
Primary top-1 accuracy = number of cases selecting the expected origin / all attempted held-out cases. Abstention, errors, timeout, and ambiguous output count as non-correct for this metric and are separately tabulated. Do not remove difficult/errored cases from denominator. Ranking ID tie-breaks do not convert ambiguity into success.

Also report: correct/total counts, abstention count, infrastructure error count, failure-endpoint precision/recall when independently labeled, number of inspections, actual bytes/records, model input/output tokens if used, query count, graph retrieval p50/p95, and end-to-end time. Twelve cases means one case is 8.33 percentage points. Do not present small-sample differences as statistically established superiority.

Show every round and method, including regressions. Plot x = learning incidents processed; y = held-out top-1 accuracy (%). Caption must name fixture/protocol version, counts, seeds, and whether aggregate is a mean. No target curve, interpolation masquerading as observations, or decorative invented data.

## Leakage assertions
- Public investigator DTO rejects expected_origin_id, gold_label, private_fault_id, and equivalent private-only fields recursively; use an explicit allowlist, not only key-name denylisting.
- Runtime source catalog excludes private manifests and scenario-controller settings.
- No learner filesystem shell access or tool accepting arbitrary paths/queries.
- No prompt includes the evaluator's expected answer, private fixture filenames, or failure-injector parameters.
- Ordinary public config-key names and realistic change records are allowed, including distractor changes.
- Evaluation performs no learned graph writes and leaves snapshot contents unchanged.
- Independent cases reset runtime and observations; learned snapshots persist only as the protocol specifies.

## Required experiments
Development transfer gate: one learned dependency improves a different development incident with a visible evidence path; no final held-out tuning.
Graph ablation: remove/disable one learned relationship in an isolated copy and re-run relevant cases. Diagnose through alternate valid paths when present; do not assume every ablation should fail.
Deterministic rerun: same fixture/protocol yields same ranked structural output, excluding timestamps and measured latency. Optional LLM wording is not used for exact scoring.
Failure checks: rejected/partial ingestion cannot create verified claims; timeout/truncation cannot mean no dependency; stale-source claims cannot support current-version answers.

## Load evaluation
Separate from accuracy and LLM generation. Use 1/5/10 concurrent retrieval clients, with a predeclared request count (target at least 500 per level if time allows), bounded traversal depth/results, and a labeled generated graph. Record actual node/edge counts, deployment/hardware, warm-up, time range, cold/warm status, successful throughput, errors/timeouts, and p95. Include a write-visible read check. Do not claim a synthetic registry or graph models real incident diversity.

## Artifacts
protocol/v1/*.json and hashes; artifacts/eval/RUN_ID/protocol.json, snapshots.json, predictions.jsonl, inspections.jsonl, aggregate.json, commands.txt, environment.json, and redacted logs. Each prediction identifies method, round, seed, case ID, expected ID (private evaluation output only), selected ID, status, manifest hash, evidence IDs, and durations. Public UI gets aggregate/sanitized outputs only. Preserve raw failed runs and distinguish corrected reruns.

## Publication gate
No measured superiority claim without actual results and reproducible commands. If results are inconclusive, submit the working prototype with accurate limitations. Do not change the experiment to manufacture a rising curve. Favor the honest demonstrable contribution over a false win claim.
