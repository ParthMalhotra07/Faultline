# Three-minute Loom narration

Record the live app at https://faultline-j7kn.onrender.com. The silent
`artifacts/submission/fallback-demo.webm` follows these stages and can guide
timing, but it is not a Loom or narrated pitch. Keep failures, replay labels and
counts visible. If live hosting is unavailable, say so plainly.

**0:00–0:20 — The problem and the three steps.** Show the landing page's
**How FAULTLINE solves it** section. “Checkout fails. The team's map shows
services but misses that pricing reads a shared currency setting. FAULTLINE
shows the failure, checks the missing connection against evidence, then
remembers the supported link for the next incident.” Open the workspace with
the prefilled public test values, complete or skip the tour, then reset the
graph. “This is a controlled commerce sandbox, and I run the open-source
HydraDB engine myself.”

**0:20–0:45 — Real fault.** “I’ll trigger a local currency configuration fault.
The acceptance checks now fail in checkout. Nothing touches production.”

**0:45–1:20 — Honest initial answer.** “Investigate traverses the current
HydraDB graph. The graph lacks a verified path to the changed setting, so it
abstains instead of guessing. The missing path tells the learner which bounded
telemetry source to inspect.”

**1:20–1:50 — Evidence-backed learning.** “One inspection reads a real,
versioned config-access record. FAULTLINE validates its source hash and commits
the dependency as a Claim linked to Evidence in HydraDB. Investigate now
returns the actual path and its claim and evidence IDs. A model’s confidence
alone never creates an edge.”

**1:50–2:10 — Transfer.** “I restore the sandbox; the checks recover while the
learned graph remains. A different refunds incident now uses the shared
pricing-to-currency path without inspecting another source.”

**2:10–2:40 — Metric and baselines.** “The primary metric is top-1 diagnosis
over every attempted held-out case, counting abstentions and errors as misses.
There are 12 distinct controlled cases repeated over three seeds. After one
learning incident, adaptive acquisition scored 24 of 36, equal-budget random
16 of 36, and the frozen graph zero. Once both available sources were known,
adaptive and random both reached 36 of 36. Removing one graph dependency
reduced final correct answers to 24 of 36; same-evidence token overlap reached
12 of 36. A separate retrospective Qdrant vector comparison of acquired
record text also reached 12 of 36. It uses reused synthetic cases, and the
graph also has seeded topology; this is not a general accuracy claim.”

**2:40–3:00 — Buyer and limits.** “The first potential buyer is a small
platform team repeatedly rediscovering shared dependencies. A shadow-mode
product could import approved telemetry and service metadata, show evidence
paths, and leave actions to humans. I have not validated willingness to pay or
production performance. The live demo and full protocol are linked beside
this walkthrough.”
