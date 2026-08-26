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
- runtime dependency includes a private exact Git-over-SSH SDK.

Consequently, `uv build` may succeed while a public installer cannot resolve
runtime dependencies. Do not upload this metadata to public PyPI.

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
- clean install in an environment with the intended private registry/Git
  authorization; and
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

A public Ghost package needs one of these deliberate architectures:

1. depend only on a public opaque Canticle/SEAM client and call a service; or
2. distribute through an authenticated private package channel that can resolve
   the private SDK/runtime.

Changing to the public `seam-client` is not a metadata edit; it changes Ghost
from in-process MIRL/SEAM behavior to an opaque API product and requires an
architecture/reliability/security evaluation.

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

## Runner boundary

The local candidate routes automatic public continuity to `ubuntu-latest` and
makes `seam-box` CI manual-only. It is not a remote control until merged, and
runner-group/fork settings remain external evidence. Resolve
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
