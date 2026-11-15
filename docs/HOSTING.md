# Hosted judge demo

`Dockerfile.demo` builds one Linux container containing the pinned **open-source
HydraDB 0.4.0 repository engine** and the FAULTLINE Python API/UI. The engine's
HTTP query endpoint stays on container loopback; only the app port 8765 is
exposed by the image. A persistent `/data` mount holds the HydraDB store/cache,
auth file and graph manifest. The container is for a controlled judge demo,
not a production multi-user incident service.

The image was built locally and tested on November 15, 2026: a fresh container
served the 29 measured result points and recorded replay, rejected a request
with a different Origin, performed a real trigger/abstain/learn workflow through
HydraDB, restarted, retained the graph manifest, and transferred learning to a
different incident without another inspection. See `artifacts/T23-docker-build.log`,
`T23-hosted-first.log` and `T23-hosted-after.log`. This is **local Docker proof**;
it is not evidence that any cloud deployment has happened.

## Required host settings

- Build from `Dockerfile.demo` (some providers need an explicit Dockerfile path).
- Mount durable writable storage at `/data`; allow one long-running service with
  enough memory for HydraDB and Python (local test used a 4 GiB cap).
- Expose the container's `PORT` (default 8765) through the provider's HTTPS URL.
- Set `HYDRADB_TOKEN` to a freshly generated 32+ character secret **inside the
  host's environment/secret settings**. Do not put it in Git, the browser, or
  chat. The entrypoint writes it to `/data/auth-token` for the bundled engine.
- Set `FAULTLINE_PUBLIC_ORIGIN` to the exact HTTPS origin shown to visitors,
  such as `https://your-app.example`. No path or trailing slash. The app accepts
  that Host and matching browser Origin for its bounded sandbox controls.
- Keep one replica/one writer. Do not expose the engine's 8443/9090 ports as
  public ingress. Health and actual learning must be checked after deployment.

On Railway, the [Dockerfile path setting](https://docs.railway.com/builds/dockerfiles)
can select `Dockerfile.demo`; its [volume guide](https://docs.railway.com/volumes)
describes mounting `/data`. Those docs explain a possible provider workflow,
not an account or deployment already verified for this project.

## Verify the real public URL

Open the HTTPS URL in a signed-out browser and run: Reset experiment graph →
Checkout/shared currency → Trigger → Investigate (abstains) → Inspect & learn
(source-backed READS_CONFIG edges) → Restore → Refunds/transfer → Trigger →
Investigate (selects currency without another inspection). Also check Results
and Replay, browser console, and mobile width. Then restart the service and
verify learned graph persistence. Record the URL, provider, image digest,
timestamp and actual check output in `STATE.json` before calling the link usable.

The local source bundle and three-minute silent fallback video are in
`artifacts/submission/`. A Loom walkthrough still needs narration and an actual
uploaded share link.
