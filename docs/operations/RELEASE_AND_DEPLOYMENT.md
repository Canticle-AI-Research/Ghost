# Release and deployment boundaries

Ghost has a buildable package, not a qualified public release or hosted
deployment. This page prevents those states from collapsing into one claim.

## State machine

```text
working tree
   → committed branch
   → pushed branch
   → reviewed PR
   → merged main
   → built candidate artifact
   → qualified release artifact
   → published release
   → deployed environment
   → live operational verification
```

Each arrow requires distinct evidence and a history event when material.

## Current package boundary

- project name: `canticle-ghost`;
- current version: `0.1.0`;
- build backend: Hatchling;
- wheel package: `src/ghost`;
- console entry: `ghost = ghost.cli:main`;
- local WIP adds `ghost-avatar = ghost.avatar.runner:main`;
- runtime dependencies resolve from public package indexes only.

The wheel clean-installs publicly, but no PyPI/GitHub release or hosted Ghost
deployment is implied or authorized by installability.

## Candidate build

```bash
uv lock --check
uv build
```

The normal build can run without clearing `dist/`. If old artifacts need to be
removed, inspect `dist/` and delete only the named files you intend to replace.
Package smoke currently expects one wheel, so CI starts from a clean checkout.

Qualification should inspect:

- wheel and sdist member paths;
- METADATA dependencies and exact version;
- entry points;
- absence of `.env`, databases, keys, local paths, caches, source candidates,
  and unapproved avatar assets;
- clean install on a credential-free disposable environment; and
- real `ghost --help` plus isolated agent smoke.

## License and ownership gate

Before any public artifact:

1. confirm the copyright/licensor name matches the actual owner;
2. include `LICENSE` and every required `NOTICE` in wheel and sdist;
3. verify package metadata uses the declared license reference;
4. prove excluded branding/assets and private runtime material are absent unless
   intentionally delivered under separate terms;
5. preserve third-party notices and dependency provenance;
6. confirm inbound contributions can be distributed and commercially
   relicensed as planned; and
7. reconcile consumer/API/commercial/privacy terms with deployed behavior.

The current local candidate has not received counsel review or
founder-to-company assignment and is not approved for publication.

## Public distribution decision

The selected architecture is a public Ghost wheel plus an independently
authored opaque HTTP adapter. It calls an authenticated hosted SEAM service or a
compatible licensed local node. Private MIRL/runtime implementation is neither
packaged nor imported. The agent-turn contract preserves reasoning/action
parity that `seam-client` 2.x alone does not provide. Publication still awaits
owner approval, release qualification, and company/legal reconciliation.

## Deployment prerequisites

Before any production claim:

- authenticated principal and workspace boundary;
- secret management outside repo/env examples;
- sandbox or explicit process/container authority model;
- network/provider allowlists and egress policy;
- service supervision, cancellation, time/step budgets;
- shared or topology-appropriate rate limiting;
- durable database backup/restore and tested recovery;
- schema/projection migration contract inherited from exact SEAM version;
- tracing, latency, cost, tool, and memory-quality observability;
- rollback and incident procedures;
- exact release artifact identity; and
- live smoke against the deployed artifact.

Ghost's local checkpoint backup/verify/restore primitives satisfy only the
mechanical beginning of the checkpoint recovery bullet. They do not establish
a schedule, retention, encryption, off-host copy, SEAM recovery, migration,
RPO/RTO, or deployed restore drill. The redacted health and specialist event
types similarly define a safe data contract but expose no endpoint or hosted
telemetry backend. See
[recovery and observability](RECOVERY_AND_OBSERVABILITY.md).

## Runner boundary

Every workflow job targets `ubuntu-latest`; Ghost has no assigned self-hosted
runner. Paid live work is manual-only and requires service/provider secrets.
Repository/fork settings remain external evidence. Resolve
[public repository and runner](../security/PUBLIC_REPOSITORY_AND_RUNNER.md)
before describing CI as operational.

## Release evidence record

A release history entry names:

- exact tag and commit;
- artifact names, bytes, and SHA-256 hashes;
- build and clean-install commands;
- test/live-test scopes and deselections;
- dependency source boundary;
- publication destination and visibility;
- rollback artifact; and
- whether deployment was performed or explicitly not performed.
