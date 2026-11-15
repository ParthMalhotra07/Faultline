# Development timeline and Git provenance

FAULTLINE implementation and checks ran on November 14, 2026 IST before this
workspace was initialized as a Git repository. The first actual Git commit was
`998e206` on November 15 at 10:34:09 IST. Every commit currently in `main` has
an actual November 15 author and committer date. There are no November 14 Git
commits, and this record does not present local work artifacts as commits.

Selected November 14 artifacts, using their recorded local file modification
times (IST):

- 11:12:34 — [preflight](../artifacts/preflight.md) recorded the toolchain and
  initial runtime checks.
- 11:20:26 — [T05 graph integration](../artifacts/T05-green.log) recorded the
  live evidence-backed HydraDB claim traversal check.
- 11:25:54 — [T12 transfer pilot](../artifacts/T12-pilot.log) recorded a different
  incident benefiting from a learned graph path.
- 11:30:13 — [T15 protocol freeze](../artifacts/T15-freeze.log) recorded the
  evaluation freeze.
- 11:43:09 — [T16 verification](../artifacts/T16-verification.log) checked the
  completed held-out evaluation artifacts.
- 12:13:14 — [T19 browser check](../artifacts/T19-browser-check.log) recorded
  nine rendered workflow checks.
- 12:15:25 — [T22 clean demo](../artifacts/T22-clean-demo.log) recorded a fresh
  demo run and restart persistence.

The recorded artifact logs document checks and work done before Git setup;
filesystem timestamps are mutable and cannot substitute for a historical Git
commit or an organizer's own timestamped record. Use the repository's true Git
history and these separate artifacts when explaining the sequence.
