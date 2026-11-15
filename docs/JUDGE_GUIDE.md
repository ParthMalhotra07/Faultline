# FAULTLINE: judge's quick guide

## The 30-second explanation

A checkout failure can come from a shared setting that the team's existing map
does not show. FAULTLINE checks a limited evidence source, saves a supported
connection in the self-run HydraDB graph, and uses that connection when a later
refunds incident needs it. This is a controlled executable demo, not a
production integration or a system that edits its own algorithm.

This project addresses the November [HydraDB hackathon Track 1](https://luma.com/bqwllms4):
a graph that improves through use and earns its place over a vector store.
Learning begins when the operator selects **Inspect & learn**. The source
selection, validation and graph write happen within that bounded step.

## See it work

Open [the live app](https://faultline-j7kn.onrender.com), select **Open
workspace**, and use the prefilled public test values. Complete or skip the
five-step tour. Then:

1. Select **Reset experiment graph**. The three app checks are healthy, and
   configuration-read evidence is not yet inspected.
2. With **Checkout · shared currency fault** selected, choose **Trigger fault**.
   Checkout's executed check fails.
3. Choose **Investigate**. The incomplete graph reports **insufficient
   evidence**.
4. Choose **Inspect & learn**. A source-backed relationship is added, and the
   diagnosis supports `config:currency`. Expand **Inspect evidence IDs & source
   versions** to see provenance.
5. Choose **Restore app**. Checks recover while learned claims remain. Select
   **Refunds · transfer incident**, trigger it, and investigate. The earlier
   relationship supports this different incident without another inspection.

The app is a shared single-writer demo. Reset before recording, and avoid a
second viewer changing its state during the walkthrough. Render's free disk is
ephemeral, so a cold start or redeploy can reset the hosted graph.

## Where the graph does real work

- [`Dockerfile.demo`](../Dockerfile.demo) starts the pinned open-source HydraDB
  engine with the Python app. This is the repository engine, not the hosted
  HydraDB service.
- [`graph/store.py`](../src/faultline/graph/store.py) writes Claim and Evidence
  nodes and executes bounded relationship traversal in HydraDB.
- [`graph/adapter.py`](../src/faultline/graph/adapter.py) is the actual HTTP
  transport to the pinned engine.
- [`learning/runner.py`](../src/faultline/learning/runner.py) finds a gap,
  chooses one allowed source, inspects under budget and commits validated
  claims. [`ingestion/commit.py`](../src/faultline/ingestion/commit.py) enforces
  source/evidence identity.
- [`diagnosis/ranker.py`](../src/faultline/diagnosis/ranker.py) reads graph paths
  and preserves abstention, ties and retrieval errors. The private expected
  answer stays outside this path.

The application needs the stored relationships and their provenance to produce
its supported paths. A plain text search would need to reconstruct those
connections. This does not prove that only a graph database could implement
the workflow.

## What was measured

The frozen [protocol](../protocol/v1/protocol.json) scores the actual top-ranked
diagnosis over twelve distinct controlled cases, repeated under three fixed
seeds. Every point therefore has 36 predictions, not 36 independent incident
types. Wrong answers, abstentions and errors count as misses.

- Before learning: adaptive, random and frozen graph each scored **0/36**.
- After one learning incident: gap-driven acquisition **24/36**; equal-budget
  random acquisition **16/36**; unchanged graph **0/36**.
- After both available sources were acquired: gap-driven and random each
  reached **36/36**. The small source catalog saturates quickly.
- Removing one pricing-to-currency graph relationship from the final graph
  reduced correct answers to **24/36** on these fixtures.

The selected [aggregate](../artifacts/eval/v1-20261114T064609Z-31b50c/aggregate.json),
[raw predictions](../artifacts/eval/v1-20261114T064609Z-31b50c/predictions.jsonl),
and [`verify_evaluation.py`](../scripts/verify_evaluation.py) support those
counts. The verifier checks 1,044 predictions and 63 unchanged read-only
evaluation snapshots. See [EVALUATION.md](EVALUATION.md) for leakage boundaries.

An additional [Qdrant/FastEmbed comparison](../protocol/vector-exploratory-v2.json)
is **retrospective and exploratory** on the same already-used controlled cases.
One fixed vector representation of acquired record text reached 12/36 after
acquisition. HydraDB also had eight seeded topology claims absent from that
vector corpus. This comparison does not establish general superiority over
vector stores or a fresh held-out win.

## Practical limits and product path

The app has no connector to a customer's production systems, no customer
validation, and no autonomous remediation. The first possible buyer is a small
platform team that repeatedly rediscovers shared settings during incidents.
The next product step would read approved exported telemetry in shadow mode,
show evidence-backed suggestions, and let engineers decide what to fix. This
is a buyer hypothesis, not a measured sales result.

The [README](../README.md) has setup commands, exact versions, reproduction
notes, screenshots and hosting details. The [verification summary](../artifacts/verification/)
links the ten passing Render workspace checks and other selected outputs.
