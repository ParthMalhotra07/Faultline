# FAULTLINE — agent operating rules

Scope: every file in this FAULTLINE project. Read START_HERE.md and HANDOFF.md, then STATE.json before acting. This is a standalone hackathon project, not ReliefGrid; do not import its Go/Raft architecture or modify its files. Applicable higher-priority instructions still apply.

## Objective
Build a Track 1 HydraDB incident-search prototype that improves through evidence-backed, gap-driven ingestion. Optimize for a reliable demonstration, defensible held-out results, and a clear buyer. Winning is an aspiration, never a promised result.

## Required reading
- Product and scope: docs/CONTEXT.md.
- Component contracts: docs/ARCHITECTURE.md.
- Ordered tasks and gates: docs/BUILD_PLAN.md.
- Experiment integrity: docs/EVALUATION.md.
- Accepted and unresolved choices: docs/DECISIONS.md.
- External sources and verification: docs/REFERENCES.md.

## Work protocol
1. Inspect actual files and local changes. Treat STATE.json as a navigation index, not proof.
2. Verify any task marked DONE against its artifact and recorded check. Report discrepancies and reopen it.
3. Pick the first unfinished task whose dependencies are DONE. Keep at most one task IN_PROGRESS.
4. Read the relevant contracts. Implement the smallest vertical slice. For behavior changes, reproduce the failure or write a meaningful failing test first.
5. Run the targeted check. A failed/unrun check cannot establish completion.
6. Record actual command, exit result, output artifact, changed files, and remaining limitations in STATE.json. Update HANDOFF.md with the next executable step.
7. Continue to the next authorized task. Do not repeatedly ask permission for routine reversible implementation. Ask only for genuinely missing credentials, material scope decisions, destructive operations, or required approvals.

## Engineering invariants
- HydraDB is the sole graph DB. Real retrieval traverses relationships in HydraDB; an in-memory graph cannot substitute for integration evidence.
- Verify the selected API, dialect, and dependency versions from primary sources and a live smoke test. Hosted graph, hosted memory, and the repository engine are different interfaces.
- Use bounded parameterized query templates, explicit timeouts and result limits. An error, timeout, truncation, or incomplete scan is never an empty successful answer.
- Every learned edge has a source hash/version and evidence ID. Model confidence is not verification. Never synthesize evidence to support a desired diagnosis.
- Graph reachability supports hypotheses; it does not prove causation. Preserve abstention and ambiguity. Report the actual top-ranked answer, even when wrong.
- Learning and evaluation are separate. Gold labels, fault IDs, private manifests, and held-out outcomes cannot enter learner inputs, graph writes, prompts, or logs exposed to the learner.
- Freeze experiment rules before held-out evaluation. Do not tune on held-out results. Changes require an explicit new experiment version and fresh holdout or an exploratory label.
- No fabricated charts, test output, benchmarks, customer quotes, API behavior, or completeness claims. Label estimates, synthetic scale data, hypotheses, and unverified assumptions.
- No production actions, autonomous remediation, shell tools in the diagnostic agent, or unrestricted filesystem/network inspection. Fault injection is limited to the local sandbox.
- Do not read, print, commit, or embed secrets. Ask for configuration through environment variables; never ask users to paste keys into chat.
- Stay within selected scope. No extra agent framework, Kubernetes, model training, automatic entity merging, or new learning mechanism without a recorded decision.

## Honesty and resumption
DONE means implemented and verified, not planned. BLOCKED names the missing prerequisite and an actionable unblock. SKIPPED needs a reason and cannot silently satisfy a required gate. Preserve failed experiments. Record exact counts and limitations when presenting results. Make no commits/pushes unless authorized; never add AI attribution to commits or PRs.
