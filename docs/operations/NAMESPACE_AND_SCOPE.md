# Namespace and scope policy

## Why this matters

A second brain is unsafe if a correct memory is returned to the wrong user,
workspace, or task. Attribution metadata is not authorization. Isolation must
be designed into writes, retrieval, graph traversal, corrections, and deletion.

## Current behavior

Ghost currently receives one namespace and one scope from environment-backed
settings:

```text
GHOST_SEAM_NAMESPACE=ghost.default
GHOST_SEAM_SCOPE=thread
```

Every reasoning run, retrieval, and ingest uses that same pair. The SEAM
service may additionally derive a principal/tenant boundary from the bearer
credential; Ghost never supplies that identity as JSON. Token-only trusted
mode remains suitable only for single-operator use and is not tenancy. In both
modes, the `thread` label does not itself partition by LangGraph thread ID.

## Planned logical dimensions

| Dimension | Purpose | Example policy |
|---|---|---|
| tenant | top-level authorization boundary | one Canticle organization or deployment |
| user | personal preferences and private history | stable opaque user partition |
| workspace | shared team or product context | project or research workspace partition |
| project | narrower body of durable project knowledge | Ghost repository or initiative |
| thread | current conversational execution | LangGraph checkpoint identifier |
| agent | contribution attribution | `ghost`, future researcher, coder, verifier |

The exact encoded namespace format remains planned. It should use stable opaque
identifiers rather than raw emails, usernames, or secrets.

## Proposed retrieval policy

Ghost should make scope composition explicit rather than searching everything:

1. current thread context from the checkpoint;
2. project memory when the active project is known;
3. workspace memory when policy permits sharing;
4. user preferences when relevant;
5. organization knowledge only through an authorized shared scope.

Results from different scopes should retain their original boundary and should
not be copied into a broader scope merely because they were retrieved.

## Required isolation tests

| Test | Required result |
|---|---|
| User A writes; User B asks exact query | zero User A records |
| Project A writes; Project B searches | zero Project A records unless explicitly shared |
| Current query excludes superseded memory | superseded record absent from asserted context |
| Historical query requests earlier state | older record returned with historical label |
| Graph traversal reaches cross-boundary node | traversal refuses or clips the path |
| Delete plan names foreign record | authorization or boundary failure before mutation |
| Subagent receives delegated task | it inherits no broader boundary than the root run |

## Migration requirement

Before a deployment changes principal or namespace structure, existing
`ghost.default` memory must be inventoried and migrated deliberately. Changing
the default without migration strands old memories; searching old and new
boundaries together by default defeats isolation.
