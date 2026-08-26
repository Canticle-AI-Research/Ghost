# Complete Ghost system blueprint

This page maps every active subsystem, its owner, inputs, outputs, trust
boundary, and source location. It is descriptive of the current source tree;
`PROJECT_STATUS.md` and the latest handoff identify whether that tree is local,
under review, protected-main, or released.

## Whole system

```text
                                     GHOST

  ┌──────────────┐    argv/env     ┌───────────────────────────────┐
  │ operator     │ ──────────────► │ CLI                           │
  │ terminal     │ ◄────────────── │ ghost.cli                     │
  └──────────────┘    answer/error └──────────────┬────────────────┘
                                                   │ settings + prompt
                                                   ▼
  ┌──────────────┐   provider API  ┌───────────────────────────────┐
  │ model        │ ◄─────────────► │ agent adapter                 │
  │ OpenAI/etc.  │                 │ ghost.application             │
  └──────────────┘                 │ DeepAgents + LangChain        │
                                   │ LangGraph + SqliteSaver       │
                                   └───────┬──────────┬────────────┘
                                           │          │
                             transient     │          │ tool calls
                             middleware    │          ▼
                                           │   ┌────────────────────┐
                                           │   │ ghost.tools        │
                                           │   │ recall/read/search │
                                           │   │ optional shell     │
                                           │   └─────────┬──────────┘
                                           ▼             │ real result
                                   ┌───────────────────────────────┐
                                   │ framework-free lifecycle      │
                                   │ ghost.lifecycle               │
                                   │ begin/run/verify/complete/fail│
                                   └──────────────┬────────────────┘
                                                  │ narrow MemoryLayer
                                                  ▼
                                   ┌───────────────────────────────┐
                                   │ Ghost SEAM adapter            │
                                   │ ghost.seam_memory             │
                                   └──────────────┬────────────────┘
                                                  │ authenticated opaque HTTP
                                                  ▼
  ┌─────────────────────┐              ┌────────────────────────────┐
  │ checkpoint SQLite   │              │ SEAM                       │
  │ execution state     │              │ RAW + MIRL + retrieval     │
  │ NOT semantic truth  │              │ knowledge/reasoning graphs │
  └─────────────────────┘              └────────────────────────────┘
```

The diagram above is the public product path. The SEAM box is a separately
deployed service; none of its private implementation ships in Ghost.

## Company distribution architecture

```text
PUBLIC / SOURCE-AVAILABLE PRODUCT PLANES

  Ghost (PolyForm Shield)           Canticle Core (PolyForm Shield, planned)
          │                                      │
          └──────────────┬───────────────────────┘
                         ▼
             thin API clients/protocols
                    (Apache-2.0)
                         │
                         ▼
              auth + metering + policy edge
                         │
       ┌─────────────────┼───────────────────┐
       ▼                 ▼                   ▼
 hosted SEAM        licensed SEAM Node   SEAM-U inference
 runtime/MIRL       (Shield/commercial)  (planned proprietary model)
       │                 │                   │
       └─────────────────┴───────────────────┘
                         │
                         ▼
              proprietary cloud/control plane
```

Implemented in this candidate: Ghost's complete reasoning-preserving HTTP path
and corresponding authenticated routes in the private SEAM service. Planned: hosted operations,
Canticle Core runtime, SEAM Node delivery, and SEAM-U. The licensing decision
does not turn planned services into released or deployed software.

## Repository topology

```text
Ghost/
├── AGENTS.md                  cross-agent work protocol
├── PROJECT_STATUS.md          current-state router
├── REPO_LEDGER.md             stable decisions
├── HISTORY.md                 append-only build event stream
├── HISTORY_INDEX.md           generated bounded history map
├── README.md                  repository overview and quick start
├── pyproject.toml             package, dependencies, entry points, test/lint config
├── uv.lock                    exact resolved dependency graph
├── src/ghost/
│   ├── application.py         framework/model/checkpoint adapter
│   ├── lifecycle.py           framework-free turn contract
│   ├── memory_policy.py       deterministic admission classifier
│   ├── seam_memory.py         opaque public HTTP boundary
│   ├── middleware.py          transient recall injection
│   ├── tools.py               memory/filesystem/shell tools
│   ├── config.py              environment parsing and bounds
│   ├── context.py             per-invocation transient context
│   ├── cli.py                 console operator interface
│   └── avatar/                local unmerged avatar lane
├── tests/                     provider-free and live verification
├── tools/
│   ├── branding/              deterministic asset tooling
│   └── history/               canonical continuity tooling
├── branding/                  identity sources and tokens
└── docs/                      rebuildable wiki and evidence records
```

## One successful turn

```text
1  CLI parses argv and environment
2  GhostSettings validates bounds and authority switches
3  GhostAgent constructs model, tools, recall middleware, and checkpoint saver
4  lifecycle.run_turn trims input and asks SEAM to open a reasoning-backed turn
5  SeamMemory receives bounded public evidence through HTTP
6  middleware adds escaped JSONL evidence to the system message transiently
7  DeepAgent invokes the model and executes permitted tools
8  adapter translates provider ToolMessages into plain ToolAttempt records
9  SeamMemory sends one bounded attempt per tool for server-side verification
10 memory_policy classifies the completed exchange as admit/reject/review
11 SeamMemory submits the pair and admission decision through the public API
12 SEAM records the decision; only admit compiles durable memory
13 CLI prints the answer and closes HTTP/checkpoint connections on exit
```

Detailed sequence:

```text
Operator     CLI       Lifecycle      SEAM       Middleware/Model      Tool
   │          │            │            │                │              │
   │ prompt   │            │            │                │              │
   ├─────────►│ invoke     │            │                │              │
   │          ├───────────►│ begin_turn │                │              │
   │          │            ├───────────►│ begin+retrieve │              │
   │          │            │◄───────────┤ public evidence│              │
   │          │            ├────────────────────────────►│ inject+run   │
   │          │            │            │                ├─────────────►│
   │          │            │            │                │◄─────────────┤
   │          │            │◄────────────────────────────┤ answer/calls │
   │          │            ├───────────►│ actions        │              │
   │          │            ├───────────►│ complete +     │              │
   │          │            │            │ admission      │              │
   │          │            │◄───────────┤ opaque receipt │              │
   │          │◄───────────┤ answer     │                │              │
   │◄─────────┤ print      │            │                │              │
```

## Failure and cancellation

```text
begin SEAM run
      │
      ▼
model/tool/checkpoint exception or KeyboardInterrupt
      │
      ├─ DO NOT ingest the incomplete turn
      ├─ add an outcome node describing bounded failure type
      ├─ transition outcome to rejected
      └─ re-raise so CLI/supervisor receives the real failure
```

`BaseException` is intentionally caught around the open-run window so
cancellation and Ctrl-C do not strand reasoning state.

## Memory planes

```text
canonical evidence                         execution state
┌────────────────────────────┐             ┌──────────────────────────┐
│ SEAM service-owned store   │             │ LangGraph checkpoint DB  │
│ RAW + MIRL                 │             │ messages / graph cursor  │
│ lifecycle/provenance       │             │ thread resume state      │
└────────────┬───────────────┘             └──────────────────────────┘
             │
             ├─ derived knowledge graph
             ├─ derived retrieval indexes
             ├─ bounded prompt evidence
             └─ reasoning/action verification graph
```

The checkpoint database may be discarded without deleting semantic memory.
Ghost has no filesystem path to the service's canonical store; memory deletion
and recovery are explicit authenticated SEAM lifecycle operations.

## Deliberate memory state machine

```text
completed turn
     │
     ▼
deterministic classifier ── explicit remember ──► admit ──► SEAM compile/persist
     │
     ├── durable but unconfirmed ───────────────► review ─► reasoning only
     └── transient/no intent/mutation request ──► reject ─► reasoning only

operator mutation plane (never a model tool)
  remember TEXT ────────────────────────────────► new current memory
  correct MEM_ID TEXT ─► replacement + supersedes + old deleted_soft
  forget MEM_ID --confirm MEM_ID ───────────────► old deleted_soft
  recall --view current|history ────────────────► bounded public records
```

Every arrow carries `namespace`, `scope`, `workspace`, `project`, and, for
thread scope, the LangGraph thread ID as `session_id`. The bearer credential is
resolved to a principal only inside SEAM.

## Tool authority ladder

```text
default
  └─ seam_recall                    read Ghost memory

GHOST_TOOL_ROOTS set
  ├─ seam_recall
  ├─ read_file                      bounded UTF-8 file read
  └─ search_repo                    bounded literal search

GHOST_ENABLE_SHELL=1
  ├─ all above
  └─ run_command                    full account authority; unsandboxed
         ├─ approval default ON
         ├─ timeout bounded
         └─ result verified/fingerprinted
```

There is no denylist. A shell denylist would not create a security boundary.

## Configuration path

```text
process environment
       ▲
       │ wins
.env.local (loaded without override)
       ▲
       │ copied selectively from
.env.example
       │
       ▼
GhostSettings.from_env()
       │
       ├─ parse model/provider
       ├─ expand paths
       ├─ resolve readable roots
       ├─ enforce recall/hop/timeout bounds
       └─ preserve shell-off default
```

## Package path

```text
pyproject.toml + uv.lock
       │
       ├─ uv sync --frozen ─► runnable development environment
       │
       └─ uv build ─────────► dist/canticle_ghost-0.1.0.whl
                               dist/canticle_ghost-0.1.0.tar.gz
```

The wheel clean-installs using public dependencies only. Artifact publication
still requires owner approval, version/release evidence, license review, and a
compatible SEAM service; buildability alone grants none of those.

## Continuity path

```text
material change
   ├─ update blueprint/how-to/commands
   ├─ update status or ledger if authority changed
   ├─ append HISTORY#NNN
   ├─ register successor handoff when resume state changed
   ├─ regenerate HISTORY_INDEX.md
   ├─ write ignored snapshot
   └─ run docs/history/code/package verification
```

On a public pull request, `public-ci.yml` adds an exact-base prefix check:

```text
base HISTORY.md ──must be exact prefix──► candidate HISTORY.md
       │                                      │
       └─ immutable prior bytes               └─ zero or more new entries
```

The repository-neutral Temporal Chain starter under
`templates/temporal-chain/` reproduces this core path for other repositories. SEAM's routing and stream
split is an optional scale layer, not a prerequisite for the append-only core.

## Local avatar lane

The current working tree contains an additional unmerged path:

```text
Ghost CLI ──WebSocket──► AvatarBridge ──► browser overlay / desktop sensor
    │
    └─ start/end notifications ─────────► director actions/faces

separate GTK path:
system python + GTK ──► desktop_pet.py ──► real desktop override-redirect pet
```

This is documented in [avatar system](AVATAR_SYSTEM.md) but remains local. It
must not be required to rebuild
`main@dbd421babf0703c8c339e7b8db8d51fc51b58282`.

## Specialist and operations foundation

The merged runtime remains single-agent. The provider-free foundation adds
contracts around future extensions. `src/ghost/specialists.py` owns delegation
types and terminal normalization; `src/ghost/operations.py` owns checkpoint
recovery and health types:

```text
root turn ─► DelegationEnvelope ─► future specialist adapter
   ▲          budget + scope              │
   └──── SpecialistOutcome + evidence ◄───┘

checkpoint.db ─► online backup ─► SHA-256 + quick_check
                                     │
                                     └─► verified non-overwriting restore

component probes ─► redacted readiness snapshot
specialist run ───► content-free start/finish events
```

See [bounded specialist contract](SPECIALIST_CONTRACT.md) and
[recovery and observability](../operations/RECOVERY_AND_OBSERVABILITY.md).
No adapter, hosted endpoint, dashboard, deployment, or G3 comparison is implied.

## Planned extensions

- selective memory admission and user-directed correction/forgetting;
- frozen task/memory evaluation fixtures;
- true principal/workspace/project partitioning;
- model-backed bounded specialist adapters after single-agent qualification;
- authenticated service and operator UI;
- sandboxed or separately isolated execution boundary;
- SEAM recovery, hosted observability, release, and incident operations.

Planned arrows do not change current ownership boundaries.
