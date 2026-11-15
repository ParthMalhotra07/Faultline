# FAULTLINE: start or resume here

“Break the app. Watch its graph learn why.”

This folder contains the implemented FAULTLINE prototype and its evidence ledger. Read README.md for verified setup and demo commands, then HANDOFF.md and STATE.json for the current task. Real HydraDB integration, development transfer, frozen evaluation and rendered UI checks have run; verify the referenced artifacts before trusting completion.

## Start a coding session
Open this Faultline folder as the workspace. Read AGENTS.md, HANDOFF.md, STATE.json, docs/CONTEXT.md, and the current task in docs/BUILD_PLAN.md. Read the relevant architecture and evaluation sections before changing behavior.

Paste this prompt into the implementation agent:

> Work on FAULTLINE in this folder. Read AGENTS.md, START_HERE.md, HANDOFF.md, STATE.json, and the referenced project docs. Audit the actual repository and recorded evidence before trusting completion. Select the first unfinished task with completed dependencies; initially this is T00. Implement and verify it, update STATE.json and HANDOFF.md, then continue through ready tasks within scope. Use real HydraDB traversal. Keep evaluation labels isolated. Never invent API behavior, completed work, test results, or accuracy numbers. If runtime access is blocked, identify the exact missing prerequisite and continue independent work. Do not build the UI before the headless learning gate passes. This request authorizes routine reversible local implementation; respect required tool approvals and never ask me to paste secrets.

## File map
- AGENTS.md: mandatory behavior and engineering rules.
- docs/CONTEXT.md: product, judging criteria, scope, and non-goals.
- docs/ARCHITECTURE.md: components, trust boundaries, records, and execution flow.
- docs/BUILD_PLAN.md: small ordered tasks with acceptance criteria and phase gates.
- docs/EVALUATION.md: frozen protocol, fair baselines, leakage prevention, and scoring.
- STATE.json: machine-readable task status and evidence ledger.
- HANDOFF.md: compact current state and immediate next step.
- docs/DECISIONS.md: decisions, assumptions, and change process.
- docs/REFERENCES.md: primary-source links and API verification policy.
- docs/DEMO.md: demo script, buyer hypothesis, and submission checklist.
- CLAUDE.md and .cursor/rules/faultline.mdc: entry points for agents that read those formats.

## Current task
Consult HANDOFF.md and STATE.json. T00 is implemented and verified; preserve its initial failed preflight attempts. Do not restart implementation from the original handoff specification.

Use the event's confirmed actual remaining time. Do not assume a fresh 48 hours remains on resumption. User confirmed submission is November 15, 2026 IST and relayed the host's required live link, public GitHub repo and Loom walkthrough. Exact cutoff remains unconfirmed; do not infer remaining hours. See docs/SUBMISSION.md.
