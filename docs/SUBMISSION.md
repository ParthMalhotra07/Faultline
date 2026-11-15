# Submission checklist — FAULTLINE

The host requires three links: a **usable live app**, an **open-source GitHub
repository**, and a **Loom walkthrough**. The user confirmed November 15, 2026
IST as the submission date; the exact cutoff is still unknown. None of the three
public links is recorded as delivered. Do not put a localhost or silent fallback
video URL into a submission form as if it were a live app or Loom.

## Ready local evidence

- Live local app: `http://127.0.0.1:8765`, backed by the self-run open-source
  HydraDB 0.4.0 repository engine (pinned image digest in README.md).
- Silent three-minute headless rehearsal: `artifacts/submission/fallback-demo.webm`.
  This is a fallback, **not** a Loom upload or narrated pitch.
- Rehearsal report: `artifacts/submission/rehearsal.json` records 180 seconds,
  each stage, and zero console/page errors.
- Source/evidence archive: `artifacts/submission/FAULTLINE-source-and-evidence.zip`.
  Its manifest records an actual integrity check and excludes runtime secrets.
- Frozen-protocol evaluation: `artifacts/eval/latest.json` selects the newest
  complete run. `python scripts/verify_evaluation.py` checks 1,044 predictions,
  29 aggregate points and 63 unchanged read-only snapshot hashes. The exact
  rerun matched all structural predictions and aggregate counts.

## Technical story for judges

Primary metric is held-out top-1 diagnosis, **correct/all attempted cases**;
abstentions and errors remain in the denominator. Twelve distinct controlled
fixtures are repeated across three fixed seeds (36 predictions per point, not
36 independent incident types). Adaptive acquisition scored 24/36 after one
learning incident, compared with 16/36 for the equal-budget random source
selector and 0/36 for the frozen graph. After both available telemetry sources
were acquired, adaptive and random both scored 36/36. Same-evidence token
overlap scored 12/36 at the final point; it is a lexical baseline, not semantic
retrieval. Removing pricing-to-currency graph claims reduced final top-1 to
24/36. These controlled results show genuine improvement and graph dependence
inside this sandbox, while the tiny two-source topology limits generality.

The graph does real work in HydraDB: bounded paths traverse reified Claim nodes
and join source-hashed Evidence nodes to connect failing endpoints, services and
candidate configuration changes. The public response returns these exact path,
claim and evidence IDs. Reachability is a hypothesis, not causal proof. Read
the full protocol and limitations in docs/EVALUATION.md and README.md.

## Go-to-market story

The proposed buyer is a small platform team that repeatedly investigates
undocumented shared configuration dependencies. The first possible product
would ingest approved exported telemetry and service metadata in shadow mode,
present evidence-backed hypotheses, and let a human decide what to do. No
customer interview, willingness-to-pay result, revenue, or time-saved figure
has been measured. Use docs/SOCIAL_POSTS.md for truthful draft posts and buyer
questions; publish only after the links exist and an account owner authorizes it.

## Remaining public delivery

1. Deploy the Python app **and** the self-run HydraDB engine to a host with a
   durable graph volume, or provide a verified temporary tunnel while the
   machine stays online. Configure `FAULTLINE_PUBLIC_ORIGIN` to the exact HTTPS
   app origin and test the actual public workflow. A temporary tunnel has no
   uptime guarantee and is unsuitable as a durable judge link.
2. Create and inspect a public GitHub repository from the reviewed source
   package. The workspace currently has no Git repository or GitHub CLI. Do not
   commit runtime credentials, local browser profiles, or large test recordings.
3. Record a narrated Loom using docs/DEMO.md. Verify the Loom share link loads
   for a viewer and includes the live workflow, real counts, buyer pitch and
   limitations. The silent fallback can guide this recording.
4. Verify all three links in a signed-out browser, add exact URLs and the real
   cutoff to the submission record, then submit. Record the actual organizer
   confirmation; do not infer it from prepared artifacts.
