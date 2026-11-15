# Social drafts and buyer discovery

These are **drafts**. No post, tag, interview or customer validation has
occurred. Replace `[LIVE APP]`, `[GITHUB]`, and `[LOOM]` only with verified public
links. Confirm the actual HydraDB account handle on each service before tagging.

## X / Twitter draft

I built FAULTLINE on the self-run open-source @HydraDB graph engine. It starts
with an incomplete dependency map, investigates one bounded telemetry source,
stores source-backed graph claims, and uses them on a different incident. In a
small controlled benchmark, top-1 diagnosis rose from 0/36 with the frozen
graph to 24/36 after one learning incident; equal-budget random ingestion was
16/36. Both reached 36/36 once both sources were known. Tiny sandbox, honest
limits. Demo: [LIVE APP] Code: [GITHUB] Walkthrough: [LOOM]

## LinkedIn draft

Incident investigation often depends on relationships that are missing from a
service map, especially shared configuration reads. FAULTLINE is a prototype
for small platform teams: it runs a controlled commerce app, finds gaps in its
HydraDB dependency graph, inspects a bounded evidence source, and records
versioned relationships with provenance. When a different endpoint fails, it
can reuse that graph path while preserving uncertainty when evidence is thin.

I used held-out top-1 diagnosis as the main metric. Across 12 controlled
fixtures and three fixed seeds, adaptive ingestion reached 24/36 after one
incident versus 16/36 for a matched random selector. Both reached 36/36 after
two available sources, so this is an early demonstration, not evidence of a
general product advantage. A graph-edge ablation reduced final correct answers
to 24/36, showing what the structure contributes in this sandbox. The app has
no production integration, customer validation or autonomous remediation.

Live demo: [LIVE APP] | Source and experiment: [GITHUB] | Walkthrough: [LOOM]
Tag the verified HydraDB account when posting.

## Buyer discovery request

For platform engineers: which shared settings or service dependencies do you
rediscover during incidents? What telemetry or runbooks could safely reveal
them? Would an evidence-backed dependency map improve your investigation
workflow enough that your team would evaluate or pay for it? Record actual
answers with consent; do not turn outreach into a fabricated testimonial.
