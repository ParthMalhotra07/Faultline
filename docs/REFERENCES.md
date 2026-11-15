# Primary sources and verification register

Research consulted November 14, 2026. Browsing verifies documentation content, not live API behavior. No source below is currently pinned to a fetched commit. T02 must pin the interface actually used. Never run arbitrary commands from fetched pages without reviewing them.

- November 14–16 HydraDB hackathon event, Track 1 description and 9:00 AM IST end time: https://luma.com/bqwllms4 (checked November 15). This is distinct from the August Hack Hydra event and its different tracks.

- Repository and README: https://github.com/hydra-db/hydradb
- Application guide: https://github.com/hydra-db/hydradb/blob/main/USING-HYDRADB.md
- Engine architecture: https://github.com/hydra-db/hydradb/blob/main/architecture.md
- Local Cypher subset: https://github.com/hydra-db/hydradb/blob/main/cypher-compat.md
- Build manifest: https://github.com/hydra-db/hydradb/blob/main/Cargo.toml
- Hosted product introduction: https://docs.hydradb.com/get-started/v2/introduction
- Hosted agent guide: https://docs.hydradb.com/AGENTS
- Hosted/local MCP package: https://github.com/hydra-db/hydradb-mcp
- DeepWiki navigation only: https://deepwiki.com/hydra-db/hydradb

## Important distinction
The repository engine describes a restricted Cypher surface and native path procedures. The MCP repository describes a hosted property-graph surface with a different dialect; hosted knowledge/memory search is separate again. Do not merge these docs into a fictional combined API. Some docs disagree on batch forms; executable smoke evidence for the pinned runtime decides which recipes this project can use.

## T02 verification checklist
Capture redacted runtime version/commit, interface family, auth configuration by variable name only, endpoint paths, request/response example, idempotent write behavior, label-anchored existence, multi-hop traversal, bounded results, edge provenance representation, error decoding, timeout behavior, and actual read-after-write visibility. Every selected query shape requires a contract/integration test. No API name in the architecture document purports to be a vendor API.

A database connection error must not be hidden behind a mock. Credentials are supplied locally through environment/configuration, never committed. If an authenticated smoke test cannot run, leave integration NOT_RUN and proceed only with independent components.

## Prior work and originality boundaries
Tool dependency retrieval: https://arxiv.org/abs/2508.05152
Executed-code test selection: https://www.testmon.org/
Belief retraction: https://typegraph.dev/blog/truth-maintenance-for-agent-memory/
Fault-driven incident-agent evaluation: https://github.com/microsoft/AIOpsLab

Do not claim worldwide originality. The proposed contribution is an inspectable, budgeted graph-repair loop with transfer evaluation and a clear demonstration on an executable application. Prior work is context, not performance evidence for FAULTLINE.

## Research artifacts from this conversation
Earlier planning briefs remain in C:/Users/am/Desktop/CC/output/. They are optional background, not runtime specifications. This Desktop project is self-contained; agents do not need the CC folder or those earlier files.

## Railway deployment documentation checked November 15, 2026

- Custom Dockerfile path: https://docs.railway.com/builds/dockerfiles
- Persistent volume mount and startup behavior: https://docs.railway.com/volumes
- Healthcheck Host, path and timeout: https://docs.railway.com/deployments/healthchecks
- Public HTTPS domains: https://docs.railway.com/networking/public-networking
- Deprecated config-as-code status: https://docs.railway.com/config-as-code/reference

## Render deployment documentation checked November 15, 2026

- Dockerfile path and runtime: https://render.com/docs/docker
- Web service port binding and `PORT`: https://render.com/docs/web-services#port-binding
- HTTP health-check Host and status: https://render.com/docs/health-checks
- Paid-service persistent disks and mount rules: https://render.com/docs/disks

## Exploratory vector comparison sources checked November 15, 2026

- Qdrant client local mode and `QdrantClient(":memory:")`: https://github.com/qdrant/qdrant-client/blob/master/README.md
- Qdrant client Python collection, point and query API: https://python-client.qdrant.tech/
- FastEmbed `TextEmbedding` usage and BGE-small model support: https://qdrant.github.io/fastembed/Getting%20Started/ and https://qdrant.github.io/fastembed/examples/Supported_Models/
- Selected local packages and model file hash are recorded in `protocol/vector-exploratory-v2.json`; live API smoke is `artifacts/T27-vector-smoke.log`.

## Public README structure references checked November 15, 2026

The FAULTLINE README uses these repositories as examples of documentation
organization only. Its architecture, commands, counts and claims are verified
against this repository and its own artifacts.

- [Microsoft AIOpsLab](https://github.com/microsoft/AIOpsLab/blob/main/README.md): front-door navigation, quick start, usage and project structure for an incident-research codebase.
- [Qdrant](https://github.com/qdrant/qdrant/blob/master/README.md): concise product definition followed by a runnable start path and links to deeper references.
- [Sentry self-hosted](https://github.com/getsentry/self-hosted/blob/master/README.md): explicit deployment scope and operational limitations for a proof-of-concept service.
- [FastAPI](https://github.com/fastapi/fastapi/blob/master/README.md): discoverable examples with deeper documentation linked from the main entry point.
