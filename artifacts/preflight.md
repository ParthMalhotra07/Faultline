# T00 preflight — verified

The process-execution blocker is resolved. `python scripts/preflight.py` exited 0;
individual probe results are recorded in preflight-retry.json (including failures).
Windows Python 3.12.10, Node v24.16.0, Git 2.54.0.windows.1, Docker CLI 29.7.2;
Ubuntu WSL Python 3.14.4. Git confirms this workspace is outside a repository.
No git initialization, commit, or push performed. No HydraDB or LLM configuration
variables were present in the inherited Windows environment; no values or secret
files read. Application HTTPS access to the primary HydraDB GitHub API succeeded.

Docker daemon is initially stopped. Ubuntu lacks cargo; sudo requires interactive
authentication for the ordinary WSL user. Investigate a local Docker runtime before
requesting hosted access. HydraDB interface and runtime remain unverified until T02.
The initial 14 files were instructions only. Failed initial process attempts remain
in preflight-probes.json and preflight-first-attempt.md.

Organizer cutoff, submission rules, and actual remaining time remain unconfirmed.
Next: create T01 contracts and run their negative/boundary tests using Windows
Python in a workspace-local virtual environment. Then attempt T02 live HydraDB.
