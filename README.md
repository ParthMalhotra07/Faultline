# FAULTLINE

An incident-search prototype that discovers missing configuration dependencies from bounded telemetry inspection, stores verified claims in HydraDB, and uses those relationships in later investigations.

The executable sandbox has checkout, refunds and renewals. It uses no real payment provider. The diagnostic core is deterministic; no LLM or hosted API key is required. The buyer hypothesis is small platform teams rediscovering undocumented shared dependencies. There are no validated customers, savings estimates or production-performance claims.

## Run locally on Windows

Verified environment: Windows 11, Python 3.12.10, Docker Desktop 29.7.2. Commands below run from this project directory in PowerShell.

```powershell
docker desktop start
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements-repro.txt
.venv/Scripts/python.exe -m pip install --no-build-isolation --no-deps -e .
python scripts/start_hydra.py
$env:HYDRADB_TOKEN_FILE = Join-Path (Get-Location) '.runtime/hydra/auth-token'
.venv/Scripts/python.exe scripts/verify_demo.py
.venv/Scripts/python.exe scripts/serve.py
```

Open http://127.0.0.1:8765. The default database and API bind only to loopback. The launcher generates a random local authentication file inside ignored `.runtime/`; never print or copy its value. No credentials are included in the source package. A separate, tested single-container judge deployment path is documented in [docs/HOSTING.md](docs/HOSTING.md); no cloud URL has yet been verified.

HydraDB is the official 0.4.0 repository-engine image pinned to `sha256:ab71d651fefee13ebb23eb56d72316065bdca563ff7587442e07be663f2bf880`, commit `916637477f3f34766b4905b270bd4292109d77e6`. It uses the engine HTTP API, not hosted memory search. See [the vendor application guide](https://github.com/hydra-db/hydradb/blob/916637477f3f34766b4905b270bd4292109d77e6/USING-HYDRADB.md) and captured smoke evidence in `artifacts/hydra-smoke/`.

## Demonstrate the learning loop

1. Click **Reset experiment graph**. All three real acceptance checks recover; configuration-read evidence starts uninspected.
2. Select **Checkout · shared currency fault**, then **Trigger fault** and **Investigate**. The initial graph abstains for insufficient evidence.
3. Click **Inspect & learn**. One bounded shared-service telemetry source verifies configuration reads. HydraDB returns the new claim/evidence paths, and diagnosis selects `config:currency`.
4. Click **Restore app**. Runtime health recovers and learned claims persist.
5. Select **Refunds · transfer incident**, trigger it and investigate. A different monitored endpoint uses the learned relationship without fresh inspection.
6. Inspect the measured curve and the recorded development replay. Replay is labeled and does not mutate the live graph.

The web controls operate the live demo process. CLI sandbox state is a separate ephemeral process; its reset does not restore the web process. Do not use a second CLI writer against the running web experiment. Use the web reset controls for that scope.

## Verification and evidence

```powershell
.venv/Scripts/python.exe -m pytest -q
.venv/Scripts/python.exe scripts/verify_evaluation.py
```

The clean-environment check in `artifacts/T22-clean-demo.log` reproduces abstention, actual graph learning, restart persistence, runtime restoration and transfer in a fresh disposable namespace. The browser checks capture screenshots, a video, a trace and console events in `artifacts/ui/`; `latest-attempt.json` points to the last attempt, whose `report.json` explicitly says PASS or FAIL.

For repeatable headless browser QA, without desktop input:

```powershell
.venv/Scripts/python.exe -m pip install -r requirements-ui.txt
python scripts/start_ui_browser.py
$env:FAULTLINE_PLAYWRIGHT_WS = 'ws://127.0.0.1:13000/'
.venv/Scripts/python.exe scripts/verify_ui.py --results
docker stop faultline-ui-browser
```

This uses the pinned official Playwright 1.65.2 Linux image, isolated contexts and a loopback-only local service. It does not connect to a signed-in Chrome profile. Native desktop automation was unreliable here; Windows bundled Chromium failed to launch. Both failures are preserved rather than counted as UI passes.

## Frozen experiment and measured limits

Protocol v1 is frozen in `protocol/v1/`. Learning processes six incidents, yielding seven snapshot points. Final evaluation uses twelve distinct controlled fixtures and three fixed seeds; each aggregate point pools 36 predictions, which are not 36 independent incident types. Final held-out diagnosis is read-only and cannot inspect fresh evidence.

The original completed run is `artifacts/eval/v1-20261114T060320Z-2f47a2/`: 1,044 prediction records, 29 aggregate points and 63 unchanged evaluation snapshot hashes. Adaptive ingestion scored 24/36 after one learning incident versus random ingestion's 16/36; both scored 36/36 after acquiring both sources. Frozen stayed at 0/36. Same-evidence token overlap reached 12/36; it is lexical retrieval, not a vector/semantic baseline. Removing pricing-to-currency claims from the final graph reduced correct predictions to 24/36. These are small synthetic-fixture results, not evidence of general superiority.

The first completed scoring process exited with an error during temporary-directory cleanup after saving its complete results. Those artifacts independently pass `verify_evaluation.py`. Earlier failed startup/scoring attempts are retained. Original text-baseline rows inherited graph timing/citation metadata; corrected rows mark text timing unmeasured and remove those citations, while preserving the originals. No selected answer or scoring count changed. An exact-protocol rerun completed with identical 29 aggregate points and 1,044 structural prediction rows; `artifacts/eval/latest.json` selects it.

To run the unchanged frozen experiment again:

```powershell
.venv/Scripts/python.exe scripts/evaluate.py
.venv/Scripts/python.exe scripts/verify_evaluation.py
```

The runner verifies input hashes before and after execution and reconstructs isolated HydraDB snapshots. Do not tune ranking, selection, budgets or fixtures on these held-out results. Changes to experimental rules need a new experiment version and fresh holdout or an exploratory label.

Load evidence in `artifacts/load/` is separate: 500 requests at each of 1/5/10 clients, on a generated 300-node/200-edge graph, with zero errors in the recorded run. It measures bounded warm two-hop retrieval on this local Docker deployment, not production incident diversity or scale. Raw timings and hardware/resource limits are saved there.

## Boundaries and remaining work

Only two telemetry sources exist in this prototype, so knowledge saturates quickly. Faults vary values, workloads and change order on one fixed topology with generic symptom vocabulary. Reified claims are committed only with evidence, source hashes and versions; graph reachability supports hypotheses and does not prove causation. Ambiguity, abstention and infrastructure errors are preserved.

This is a single-writer local demo with function-level acceptance checks. It is not a production service, remediation agent or authenticated multi-user application. `.runtime/` stores local graph manifests and credentials and is excluded from source packaging. Private evaluator fixtures and raw predictions are never served through the public API or source catalog.

The host requires a usable live app link, an open-source GitHub repo and a Loom walkthrough, according to the user. Submission date is November 15, 2026 IST; exact cutoff and hosting/account access remain unconfirmed. The app is currently local-only. No submission, publication, commit or push has been performed. See `docs/SUBMISSION.md`, `STATE.json` and `HANDOFF.md` for evidence and remaining delivery steps.
