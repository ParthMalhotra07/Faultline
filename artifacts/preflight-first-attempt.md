# FAULTLINE preflight — T00 blocked

Checked 2026-11-14T05:40:40.503Z. Workspace: `C:/Users/am/Desktop/Faultline`.

## Observed

- Windows 10.0.26200 (x64), obtained through Node OS API.
- Initial recursive inventory contains 14 instruction/specification files; no application, tests, dependencies, or runtime artifacts. Full inventory in preflight-probes.json.
- No `.git` marker exists at workspace or any ancestor up to C:/. Git could not execute, so Git configuration and working-tree status remain unverified. No repository initialized.
- Filesystem reads/writes through Node REPL work. Shell execution does not.
- Primary-source browser read of https://github.com/hydra-db/hydradb succeeded. This establishes browser access only, not application network or live HydraDB availability. No runtime/interface selected or pinned.

## Actual failed checks

Terminal attempted the instruction read command recorded in preflight-probes.json: process creation failed with Windows error 5 (Access is denied); no process exit code exists. Explicit alternate shell selection also failed.

Node child_process.execFile attempted `python --version`, `node --version`, `git -C C:/Users/am/Desktop/Faultline rev-parse --show-toplevel`, `git -C C:/Users/am/Desktop/Faultline status --short`, `wsl.exe --list --quiet`, and `docker --version`, each with a 15-second timeout. Every attempt failed at spawn with EPERM. None ran; no version or exit code was observed. These failures do not prove the tools are uninstalled.

## Unverified prerequisites

Credential presence cannot be checked through the available runtime: process is undefined in Node REPL, and subprocess access failed. No secret files or values were read. HydraDB access, Python version, dependency versions, WSL/Docker state and application network remain unknown. No live smoke or application tests ran.

Exact organizer cutoff, submission format and actual remaining time are unconfirmed. Supplied schedule is not treated as a confirmed deadline.

## Unblock and exact next steps

Restore terminal/process execution for this workspace, then run `python --version`, `node --version`, `git rev-parse --show-toplevel`, `git status --short`, `wsl.exe --list --quiet`, and `docker --version`. Check HydraDB configuration by environment-variable presence only, never values. Refresh this report and complete T00 before T01/T02. Do not initialize git until the Git boundary probe succeeds.

T00 remains BLOCKED because required runtime/credential inspection is incomplete. All dependent tasks remain PENDING. No UI, learner, evaluation or database integration has been built or claimed.
