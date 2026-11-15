# Verification evidence

Selected outputs for the public prototype. The scripts under `scripts/` and
frozen protocol under `protocol/` reproduce these checks. Each log describes
one completed run, not continuous availability.

| Check | Result | Output |
| --- | --- | --- |
| Python unit and real-HydraDB integration tests | 50 passed | [python-tests.log](python-tests.log) |
| Fresh bundled-image graph workflow | Trigger, abstain, learn and HydraDB traversal passed | [docker-graph.log](docker-graph.log) |
| Render landing page in isolated Chromium | 8 checks passed | [hosted-landing.log](hosted-landing.log) |
| Render workspace in isolated Chromium | 10 checks passed | [hosted-workspace.log](hosted-workspace.log) |
| README Mermaid diagrams in isolated Chromium | 4 diagrams produced SVG | [readme-diagrams.log](readme-diagrams.log) |

The [frozen evaluation](../eval/latest.json) includes raw predictions,
aggregates and snapshots. Its [verifier](../../scripts/verify_evaluation.py)
recounts 1,044 predictions and checks read-only snapshot hashes. The
[exploratory vector comparison](../eval/vector-exploratory/latest.json) has a
separate protocol and verifier. The Render free instance has ephemeral storage;
local Docker restart evidence does not establish hosted persistence.
