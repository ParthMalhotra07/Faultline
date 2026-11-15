# Demo and submission playbook

## Working pitch
“Your service map shows who calls whom. It can miss the shared settings that make multiple features fail together. FAULTLINE investigates those gaps and stores verified connections in HydraDB, so the next incident starts with a better map.”

## Three-minute script
0:00–0:20: show healthy executable app and explain the missing-dependency problem.
0:20–0:45: trigger a local configuration fault and show failing real checks.
0:45–1:20: run honest diagnosis, display uncertainty and chosen evidence inspection.
1:20–1:50: show newly committed HydraDB edges with source evidence and revised diagnosis.
1:50–2:10: human restores configuration; checks recover. Different incident uses the learned relationship.
2:10–2:40: show measured held-out curve and baselines, including counts, budget, and limitations.
2:40–3:00: explain target buyer, first integration path, and what is production work versus prototype.

Choose live examples from development or predeclared demonstration cases. Do not conceal failure in the full held-out benchmark by showing only selected successful cases. Replay is allowed if labeled replay; never present a recording as live execution.

## What makes the engineering credible
Actual graph traversals and provenance; real behavioral faults; equal-budget controls; no answer oracle; a transfer case; clean reset; explicit failure handling; generated scale data clearly separated from executable-app accuracy.

## Buyer validation
Ask potential platform engineers: which dependencies do you rediscover during incidents, what evidence is available, and would another tool improve on your current observability setup? Record consented notes accurately. Price and willingness to pay remain hypotheses until validated. No invented customer names or quotes.

## Before submission
Confirm current organizer requirements and cutoff. Verify public repo has no credentials or private data. Write exact setup/reset/evaluate/demo commands proven from a clean environment. Include pinned dependencies, protocol hashes, real aggregate results, architectural explanation, limitations, and a fallback recording. Retain raw redacted output behind every result claim. Verify demo graph survives an app restart and resets intentionally.

## Scope protection
Stop new features before rehearsal. Prefer one reliable evidence-to-edge-to-better-answer sequence over many half-working integrations. If the learning gate fails, state that honestly and seek a focused design adjustment; do not ship invented improvement numbers.

## Verified local delivery

The implementation uses a Python standard-library loopback HTTP server and a
buildless HTML/CSS/JavaScript UI. The headless development-transfer gate passed
before UI implementation. Browser QA now runs in isolated headless Chromium via
the official pinned Playwright container, without controlling the active desktop.
All 46 Python tests pass; the fresh environment demo is recorded in
artifacts/T22-clean-demo.log. UI report artifacts include screenshots, trace,
video, actual API-to-rendered-graph checks, mobile layout and explicit errors.

## Exact rehearsal controls

Before presenting, open http://127.0.0.1:8765 and use Reset experiment graph.
Choose Checkout / shared currency fault. Trigger -> Investigate must abstain.
Inspect & learn must show config:currency and actual orange READS_CONFIG claims.
Restore app must show all healthy while retaining learned claims.
Choose Refunds / transfer incident. Trigger -> Investigate uses the existing
pricing-to-currency path without another inspection. The pilot monitoring scopes
are checkout+renewals and refunds+renewals; all flows are real functions.

Show all seven curve points and all methods. Explain twelve distinct fixtures
repeated over three seeds, the two-source catalog and quick saturation. Both
adaptive and random ingestion reach the same final score. The lexical comparator
is token overlap, not semantic search. The structural ablation is separate from
acquisition-policy comparison. Every displayed count comes from actual artifacts.

Recorded development replay is a labeled fallback and does not mutate live state.
The silent UI QA video is not a narrated pitch. A dedicated three-minute silent
rehearsal/fallback now exists at `artifacts/submission/fallback-demo.webm`; its
report says PASS with zero console/page errors. It is not a Loom upload.

## Buyer pitch, still a hypothesis

For a small platform team, the first integration would run in shadow mode over
exported configuration-access telemetry and existing service metadata. The user
reviews hypotheses and evidence; there is no production remediation. Discovery
questions: which shared settings are repeatedly rediscovered, what telemetry can
be exported safely, and does an evidence-backed dependency map reduce repeated
investigation? No interviews, customer quotes, willingness-to-pay or time savings
have been measured. Do not invent any.

## Organizer status

User confirmed submission November 15, 2026 IST and relayed the host's three
required public deliverables: usable live link, open-source GitHub repo, and
Loom walkthrough. Exact cutoff and hosting account access remain unknown.
Focused commits were pushed to the user's private GitHub repo, which does not
yet satisfy the public-repo requirement. No live public link, Loom, social post
or organizer submission has been verified. See
`docs/SUBMISSION.md` for the concrete checklist and `docs/SOCIAL_POSTS.md` for
truthful draft posts. `docs/LOOM_SCRIPT.md` has a complete timed narration.
Prepared files are not a completed submission.
