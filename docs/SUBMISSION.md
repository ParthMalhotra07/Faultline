# Submission checklist — FAULTLINE

The host requires three links: a **usable live app**, an **open-source GitHub
repository**, and a **Loom walkthrough**. The [November event page](https://luma.com/bqwllms4)
sets the end of the 48-hour build at **November 16, 2026, 9:00 AM IST**. Confirm
the official submission form's cutoff in Discord if it differs. The live app
link is verified at `https://faultline-j7kn.onrender.com`; the public GitHub
and Loom links remain undelivered. Source was pushed to the user's private
repo at `https://github.com/ParthMalhotra07/Faultline`; make it public only
after the owner reviews the disclosure. Do not put a localhost or silent fallback
video URL into a submission form as if it were a live app or Loom.

The judge flow starts at the landing page. Select **Open workspace**, enter
with the prefilled public test values, then complete or skip the first-visit
tour before resetting and triggering the demonstration fault. These values
open an in-memory public demo session; they are not private accounts or
HydraDB credentials. The hosted T30 browser run passed ten checks after the
new revision deployed; see `artifacts/T30-browser-report.json`. The
[judge's quick guide](JUDGE_GUIDE.md) explains the problem, the exact demo
steps, the real graph traversal, and the measured comparison in one place.

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

An exploratory Qdrant/FastEmbed comparison on the same previously used cases
indexes only acquired config-access record text. It scored 12/36 from the first
acquisition onward versus the adaptive HydraDB method's 24/36 then 36/36.
The 252 vector predictions and 21 source snapshots were recounted from raw
artifacts. This is a fixed narrow vector setup, **not** a fresh held-out result
or a general vector-store defeat. HydraDB also uses eight seeded topology
claims that the vector corpus does not contain. The first exploratory runner
failed before aggregation; v2 corrected its snapshot-round check and preserves
the failed attempt. See the separate protocol and verifier in README.md.

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
questions. The user reports that the X thread is already live, but no link or
independent content/tag check has been recorded. LinkedIn and other publication
remain unverified; do not claim those posts or buyer validation.

## Remaining public delivery

1. The Render app is live and its public health, landing, workspace, measured
   results, graph traversal and browser workflow passed. The service uses the
   free plan, which cannot mount the required persistent `/data` disk. Use a
   paid disk-backed instance for restart persistence, or disclose the
   ephemeral limitation in the Loom and submission. Do not claim restart
   persistence from the public service until it is tested with a disk.
2. Keep the pushed GitHub repository private until the user manually changes
   its visibility to public immediately before the cutoff. Do not publish runtime
   credentials, local browser profiles, or large test recordings.
3. The user will record a narrated Loom using docs/LOOM_SCRIPT.md after the
   live URL is active. Verify the Loom share link loads
   for a viewer and includes the live workflow, real counts, buyer pitch and
   limitations. The silent fallback can guide this recording.
4. Verify all three links in a signed-out browser, add exact URLs and the real
   cutoff to the submission record, then submit. Record the actual organizer
   confirmation; do not infer it from prepared artifacts.
