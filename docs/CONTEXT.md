# Product context and scope

## Goal and judging
Track 1 requires a graph search system that improves what it ingests/how it queries and a measured accuracy curve over iterations. The required database is the self-run open-source engine at github.com/hydra-db/hydradb. Engineering and go-to-market have equal judging weight, according to the host clarification relayed by the builder. The host requests a usable live app link, an open-source GitHub repo, and a Loom walkthrough. Exact cutoff and account access remain unconfirmed.

FAULTLINE diagnoses incidents in a small executable commerce app, discovers missing dependencies through targeted evidence inspection, and remembers verified relationships in HydraDB for future investigations.

## Product promise
Find shared configuration dependencies behind apparently unrelated failures. Explain the path and its evidence. Learn a better dependency map from each investigation.

## Solo MVP
- One Python app, three business flows: checkout, refunds, renewals.
- Three shared resources: currency configuration, sandbox billing credential, inventory flag. A fourth is optional.
- Local-only controlled faults that change real function/HTTP behavior and fail acceptance checks.
- A real HydraDB graph containing known topology and newly verified configuration dependencies.
- Deterministic candidate ranking and gap-driven evidence selection. One LLM integration is optional for explanations, after the core works.
- Six learning scenarios, development-only pilots, and twelve held-out scenarios frozen before final evaluation.
- Frozen graph, equal-budget random ingestion, and adaptive ingestion baselines. Same-evidence semantic retrieval is strongly preferred before visual polish.
- A UI showing app health, investigation/evidence, actual graph paths, and measured evaluation results.

## Demo story
Trigger a shared config fault. Diagnose honestly using the current graph. Notice a specific evidence gap. Inspect one bounded source, ingest justified edges, and revise the hypothesis. Restore the sandbox and observe acceptance checks recover. Trigger a different incident and demonstrate transfer. Show the actual full held-out curve.

## Non-goals
Production incident remediation; real payments; Kubernetes; a general observability platform; broad connectors; multi-agent systems; model fine-tuning; entity merging; claims of universal causal diagnosis. No second learning mechanism before required gates pass.

## Why graph retrieval
The query joins failing endpoint paths to shared resources and recent changes, retaining provenance. Similar error text alone may not expose those connections. SQL could implement relationships too; we demonstrate graph value by executing traversal in HydraDB and by edge-ablation experiments, not by claiming graphs are the only possible solution.

## Commercial thesis — unvalidated
Buyer: small platform teams repeatedly rediscovering undocumented shared dependencies. First product: shadow-mode investigation over exported telemetry/runbooks. Value: less repeated investigation and a better dependency map. No validated customers, pricing, savings, or production performance exist. Interview three potential users if accessible; never invent quotes.

## Definition of successful submission
A clean-start run produces a genuine failure; HydraDB-backed diagnosis explains its evidence; a budgeted investigation updates the graph; different incidents benefit; fair baselines and full counts are reproducible; limitations are explicit; a three-minute demo and fallback recording work. Winning cannot be guaranteed.

## Time and scope cuts
Hours are elapsed-budget guides, not calendar promises. Protect six hours for rest and at least four hours for rehearsal/submission. If behind, use two flows/two configs and six held-out scenarios through a pre-evaluation protocol amendment. Cut UI complexity, integrations, and LLM prose before graph correctness, evaluation integrity, or a working reset.
