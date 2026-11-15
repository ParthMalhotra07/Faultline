# Hosted judge demo

`Dockerfile.demo` builds one Linux container containing the pinned **open-source
HydraDB 0.4.0 repository engine** and the FAULTLINE Python API/UI. The engine's
HTTP query endpoint stays on container loopback; the app uses port 8765 in
local Docker and port 10000 on Render. A persistent `/data` mount can hold the
HydraDB store/cache, auth file and graph manifest. The container is for a controlled judge demo,
not a production multi-user incident service.

The image was built locally and tested on November 15, 2026: a fresh container
served the 29 measured result points and recorded replay, rejected a request
with a different Origin, performed a real trigger/abstain/learn workflow through
HydraDB, restarted, retained the graph manifest, and transferred learning to a
different incident without another inspection. See `artifacts/T23-docker-build.log`,
`T23-hosted-first.log` and `T23-hosted-after.log`. This is **local Docker proof**;
the later Render deployment and browser checks are documented below.

## Required host settings

- Build from `Dockerfile.demo` (some providers need an explicit Dockerfile path).
- For restart persistence, mount durable writable storage at `/data`; allow one long-running service with
  enough memory for HydraDB and Python (local test used a 4 GiB cap).
- Route the container's `PORT` (local default 8765; Render 10000) through the provider's HTTPS URL.
- Set `HYDRADB_TOKEN` to a freshly generated 32+ character secret **inside the
  host's environment/secret settings**. Do not put it in Git, the browser, or
  chat. The entrypoint writes it to `/data/auth-token` for the bundled engine.
- Set `FAULTLINE_PUBLIC_ORIGIN` to the exact HTTPS origin shown to visitors,
  such as `https://your-app.example`. No path or trailing slash. The app accepts
  that Host and matching browser Origin for its bounded sandbox controls.
- Keep one replica/one writer. Do not expose the engine's 8443/9090 ports as
  public ingress. Health and actual learning must be checked after deployment.

## Verified Render web service

The user started a Render Docker web-service deployment from commit `ae667f7`
at `https://faultline-j7kn.onrender.com`. The first build started HydraDB and
FAULTLINE but failed its health check because Render expected port 10000 while
the app listened on 8765. The authenticated Render API changed **only** the
service's `PORT` setting to 10000; a new deploy of commit `5320daf` reported
Live on November 15. Public checks returned HTTP 200 for health, landing,
workspace, results and graph. Isolated Chromium passed 8 landing and 9
workspace checks, and the hosted API completed real trigger, abstain, learn and
HydraDB traversal. See `artifacts/T23-render-public-*.log` and the latest UI
reports. These checks establish a usable live demo, not durable graph storage.

In Render's web-service settings, select **Docker** and `Dockerfile.demo` as
the Dockerfile path. Leave the Docker command unset. For the new image, set
`PORT=10000` explicitly or leave `PORT` unset; the entrypoint also corrects an
earlier `PORT=8765` override on Render. Set
`FAULTLINE_PUBLIC_ORIGIN=https://faultline-j7kn.onrender.com` exactly, and
configure `HYDRADB_TOKEN` as a freshly generated 32+ character
secret in Render's Environment tab. Do not put its value in chat or Git.
Set the HTTP health-check path to `/api/health`. The image binds to `0.0.0.0`
and the configured `PORT`. A Render health check uses the service's public
`onrender.com` Host. Render's own `RENDER_EXTERNAL_URL` takes precedence at
runtime for this service, so its public Host is used even if an older dashboard
origin is stale.
To repeat the checks, use the Render origin and `--timeout 90` for possible
free-instance cold starts, and inspect `/` and `/workspace` in a signed-out
browser. The `first` hosted check resets the controlled demo graph, so run it
before recording the Loom and avoid concurrent viewers.

**Persistence constraint:** Render currently permits persistent disks only
on paid web services. The user's screenshot shows a free instance, so `/data`
there is ephemeral and the graph can reset when Render spins down or redeploys.
That is a material demo limitation. To meet the original persistent-volume
requirement on Render, use a paid web service with one disk mounted at `/data`
and one instance. Do not claim restart persistence on the free instance.

Render documentation: [Docker service and Dockerfile path](https://render.com/docs/docker),
[port binding](https://render.com/docs/web-services#port-binding),
[health checks](https://render.com/docs/health-checks), and
[persistent disks](https://render.com/docs/disks).

## Railway settings prepared earlier

The user initially selected Railway, then began a Render deployment. These
Railway settings remain a tested alternative. The GitHub repo remains private
until the user manually changes its visibility before submission. Do not select
Vercel for this service.

In the Railway service dashboard:

1. Connect this GitHub repo and set `RAILWAY_DOCKERFILE_PATH=Dockerfile.demo`.
   Railway's default detector only looks for a root file named `Dockerfile`.
2. Attach one persistent volume mounted at `/data`. Use one service replica in
   one region; the graph engine and API share this volume and are single writer.
3. Generate a Railway HTTPS domain before setting the exact origin. Set
   `FAULTLINE_PUBLIC_ORIGIN=https://<the-generated-domain>` with no trailing
   slash or path. The browser writes require an exact Origin match.
4. Set `HYDRADB_TOKEN` as a newly generated 32+ character secret in Railway's
   Variables tab. Never paste it into chat or commit it. Set `PORT=8765` and
   `FAULTLINE_RAILWAY_HEALTHCHECK=1`. The image already has its start command.
5. Configure the deployment healthcheck path `/api/health`. FAULTLINE accepts
   Railway's `healthcheck.railway.app` Host only for that read-only GET route;
   graph, results, and sandbox controls remain blocked for that Host. Railway's
   default healthcheck timeout is 300 seconds, while the bundled engine waits up
   to 90 seconds for its own readiness.
6. Confirm the build log selected `Dockerfile.demo`, the volume path is `/data`,
   and only the app's port 8765 is publicly routed. No pre-deploy command is
   needed; Railway volumes are mounted at start, not during build or pre-deploy.

Railway documentation: [custom Dockerfile path](https://docs.railway.com/builds/dockerfiles),
[volumes](https://docs.railway.com/volumes),
[healthchecks](https://docs.railway.com/deployments/healthchecks), and
[public domains](https://docs.railway.com/networking/public-networking).
Railway's older `railway.json` config-as-code format is deprecated, so these
settings are recorded for the dashboard rather than added as a new config file.

## Local image check and public URL commands

The fresh-container local check runs the rebuilt image with a durable Docker
volume, a loopback port, the Railway healthcheck flag, then restarts the same
volume and verifies transfer. Its executed output is recorded in T25; it does
not prove Railway deployed successfully. To reproduce it without writing a
secret to Git, create an ignored `.runtime/railway-local.env` containing a
locally generated `HYDRADB_TOKEN` and
`FAULTLINE_PUBLIC_ORIGIN=https://faultline.example`. Then run:

```powershell
docker build -f Dockerfile.demo -t faultline-demo:railway-local .
docker volume create faultline-railway-check
docker run -d --name faultline-railway-check --mount type=volume,source=faultline-railway-check,target=/data --env-file .runtime/railway-local.env -e FAULTLINE_RAILWAY_HEALTHCHECK=1 -e PORT=8765 -p 127.0.0.1:18767:8765 faultline-demo:railway-local
# Wait until the container reports "HydraDB ready" and /api/health responds.
New-Item -ItemType Directory -Path .runtime/railway-check -Force | Out-Null
.venv/Scripts/python.exe scripts/verify_hosted.py --base http://127.0.0.1:18767 --origin https://faultline.example --phase first --state .runtime/railway-check/manifest.json --railway-healthcheck
docker restart faultline-railway-check
# Wait for /api/health again before the post-restart check.
.venv/Scripts/python.exe scripts/verify_hosted.py --base http://127.0.0.1:18767 --origin https://faultline.example --phase after --state .runtime/railway-check/manifest.json --railway-healthcheck
docker stop faultline-railway-check
docker rm faultline-railway-check
```

After a Render or Railway deployment is active, use its actual HTTPS domain below.
This script **resets the controlled demo graph** in its first phase, so run it
before recording the Loom and avoid concurrent viewers. It checks results,
replay, private-route rejection, wrong-Origin rejection, abstention, learning,
real HydraDB graph paths, and post-restart transfer. Keep the state file local.

```powershell
$origin = 'https://<your-actual-railway-domain>'
.venv/Scripts/python.exe scripts/verify_hosted.py --base $origin --origin $origin --phase first --state .runtime/railway-public-manifest.json
# Restart the Railway service in its dashboard, retaining the same /data volume.
.venv/Scripts/python.exe scripts/verify_hosted.py --base $origin --origin $origin --phase after --state .runtime/railway-public-manifest.json
```

For Render, set `$origin = 'https://faultline-j7kn.onrender.com'`, use a
Render-specific local state path, and append `--timeout 90` to both commands.
Only run the `after` phase after a restart with an attached persistent disk;
the free instance cannot establish that persistence claim.

The Railway healthcheck Host probe is for a directly reachable local container:
add `--railway-healthcheck` to `verify_hosted.py` in that local check. The public
Railway proxy has its own Host routing, so do not send that internal Host to the
public URL as a substitute for Railway's actual deployment healthcheck.

## Verify the real public URL

Open the HTTPS URL in a signed-out browser, verify the landing motion and live
preview, click **Open workspace**, and run: Reset experiment graph →
Checkout/shared currency → Trigger → Investigate (abstains) → Inspect & learn
(source-backed READS_CONFIG edges) → Restore → Refunds/transfer → Trigger →
Investigate (selects currency without another inspection). Also check Results
and Replay, browser console, and mobile width. Then restart the service and
verify learned graph persistence. Record the URL, provider, image digest,
timestamp and actual check output in `STATE.json` before calling the link usable.

The local source bundle and three-minute silent fallback video are in
`artifacts/submission/`. A Loom walkthrough still needs narration and an actual
uploaded share link.
