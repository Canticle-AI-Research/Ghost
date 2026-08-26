# ADR-0005: Ghost uses an opaque SEAM service boundary

- Status: Accepted
- Date: 2026-08-25
- Amends: ADR-0001 transport only

## Context

ADR-0001 correctly assigns canonical memory to SEAM and product policy to
Ghost, but its original in-process transport forced public Ghost installs to
resolve a private Git dependency. The released Apache-2.0 `seam-client` 2.x
offers remember/recall/context operations but does not carry Ghost's reasoned
retrieval, tool verification, accepted outcome, and rejected-turn non-ingest
contract. Replacing the SDK with those lower-level calls would install cleanly
while silently weakening provenance.

## Decision

1. Ghost contains no private SEAM imports or Git source dependencies.
2. `SeamMemory` is an independently authored `httpx` adapter.
3. SEAM exposes four additive opaque routes: `begin`, `actions`, `complete`,
   and `fail`, plus the existing read-only recall route.
4. The server retains canonical run, record, evidence, and verification
   identities. Ghost receives bounded public text and opaque capabilities.
5. The server derives selected evidence and passed verification IDs from its
   own reasoning record. A client cannot nominate support for an outcome.
6. Tool output crosses the authenticated request boundary only for immediate
   hashing. The reasoning graph stores its length and SHA-256, not raw output.
7. Failure sends only an exception class, creates a rejected outcome, and never
   compiles the failed exchange into memory.
8. Principal-derived tenancy and namespace/scope checks remain server-owned;
   a foreign or mismatched opaque handle returns content-free `404`.
9. Public Ghost CI installs and tests on disposable GitHub-hosted runners. Paid
   live-provider tests remain manual and require explicit service credentials.

## Consequences

Positive:

- anyone permitted by Ghost's license can install the package without private
  repository access;
- private MIRL/runtime implementation does not enter Ghost artifacts;
- exact reasoning and verification behavior stays in the canonical engine;
- hosted CI can test the complete provider-free suite and clean wheel; and
- the transport boundary is independently replaceable and testable.

Costs:

- an authorized, compatible SEAM service is required at runtime;
- client and server route changes require coordinated additive releases;
- network errors become explicit turn failures; and
- public HTTP tests prove adapter behavior, while private SEAM tests must prove
  graph/storage enforcement behind the boundary.

## Rejected alternatives

### Keep the private Git SDK dependency

Rejected because it makes public installation and hosted CI depend on private
source authorization and couples Ghost distribution to internal packaging.

### Reimplement MIRL or reasoning enforcement in Ghost

Rejected because it copies protected internals, creates a second memory engine,
and lets client-controlled data assert its own provenance.

### Use only `seam-client` 2.x remember/recall/context

Rejected because that surface cannot represent verified tool actions, accepted
outcomes supported by server-derived checks, or rejected-turn non-ingest.

### Expose private graph records over HTTP

Rejected because canonical IDs, candidate ledgers, storage shapes, and graph
internals are implementation details and information-leakage surfaces. Opaque
capabilities are sufficient for Ghost's lifecycle.
