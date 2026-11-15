# Primary sources and verification register

Research consulted November 14, 2026. Browsing verifies documentation content, not live API behavior. No source below is currently pinned to a fetched commit. T02 must pin the interface actually used. Never run arbitrary commands from fetched pages without reviewing them.

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
