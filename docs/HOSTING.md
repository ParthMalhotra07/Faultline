# Hosting FAULTLINE

`Dockerfile.demo` packages FAULTLINE with a pinned image of the open-source
HydraDB engine. The container runs the graph node and the Python HTTP server;
only the application port should be public. This deployment is a shared,
single-writer demonstration, not a production multi-tenant service.

## Required settings

| Setting | Value or purpose |
| --- | --- |
| Dockerfile | `Dockerfile.demo` |
| Health check | `GET /api/health` |
| Web port | `PORT` (8765 by default; 10000 on the current Render service) |
| Public origin | `FAULTLINE_PUBLIC_ORIGIN`, the exact external HTTPS origin without a trailing slash |
| Graph token | `HYDRADB_TOKEN`, a fresh private value set in the host's secret settings |
| Durable state | Mount a writable persistent volume at `/data` if restart persistence is required |
| Replicas | One application instance and one graph writer |

The entrypoint writes the token to `/data/auth-token` for the bundled engine,
starts HydraDB on container loopback, waits for readiness, and then starts the
web server. Do not expose the graph's 8443 or 9090 ports as public ingress.
Do not place the token in Git, the browser, or a URL.

## Current public demo

The live application is [faultline-j7kn.onrender.com](https://faultline-j7kn.onrender.com).
Its health, landing page, workspace, sign-in, tour, mobile layout and live
HydraDB learning workflow passed isolated browser checks. The selected check
outputs are in [verification evidence](../artifacts/verification/).

The current Render free instance has no persistent disk. A spin-down or
redeploy may reset graph state and ends in-memory demo sessions. Local Docker
restart persistence was verified with a mounted volume; that result does not
establish persistence for this hosted instance.

## Verify a deployment

1. Open the public URL in a signed-out browser. Enter the prefilled public demo
   values, complete or skip the tour, and follow the [judge guide](JUDGE_GUIDE.md).
2. Check `/api/health`, `/`, and `/workspace` over HTTPS.
3. Run the bounded hosted workflow check only when the shared demo may be reset:

   ```powershell
   New-Item -ItemType Directory -Force .runtime/host-smoke | Out-Null
   .venv/Scripts/python.exe scripts/verify_hosted.py `
     --base https://faultline-j7kn.onrender.com `
     --origin https://faultline-j7kn.onrender.com `
     --phase first --timeout 90
   ```

The `first` phase resets the demo graph, triggers a controlled fault, checks
abstention, inspects evidence, and verifies a live HydraDB path. Coordinate
that run with anyone recording or viewing the shared demo.
