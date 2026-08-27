# Operator and developer how-tos

These recipes describe outcomes and evidence boundaries. Start from the
repository root unless stated otherwise.

## Run a one-shot question

```bash
uv run ghost "What do you remember about the current research objective?"
```

Ghost recalls before answering. A successful turn is ingested only when the
configured admission policy returns `admit`.

## Resume a named conversation

```bash
uv run ghost --thread-id architecture-review
```

Reuse the same ID after restarting the process. The checkpoint resumes message
execution state; SEAM provides cross-session semantic memory.

## Use an isolated test brain

```bash
tmp_dir=$(mktemp -d)
GHOST_CHECKPOINT_DB="$tmp_dir/checkpoints.db" \
GHOST_SEAM_NAMESPACE="ghost.isolated.$(date +%s)-$$" \
uv run ghost --thread-id isolated "Remember that this is an isolated run."
```

Remove the temporary checkpoint directory only after confirming it contains no
needed execution history. The unique service namespace isolates semantic
memory; use a dedicated principal as well when testing tenancy.

## Connect to a SEAM service intentionally

```bash
export SEAM_BASE_URL="https://seam.example"
export SEAM_API_TOKEN="<set without committing>"
export GHOST_SEAM_NAMESPACE="ghost.default"
uv run ghost --thread-id shared-agent
```

This changes the durable memory boundary. Verify the service, principal,
namespace, and scope before sending any content.

## Remember something explicitly

Either ask Ghost directly:

```bash
uv run ghost --thread-id architecture-review \
  "Remember that the chosen release policy is exact-head verification."
```

or bypass the model and use the operator command:

```bash
uv run ghost memory remember \
  "The chosen release policy is exact-head verification." \
  --thread-id architecture-review
```

The first path admits only because the operator used explicit remember intent.
The second is the clearest deterministic write path and prints the SEAM receipt
as JSON.

## Inspect current and historical memory

```bash
uv run ghost memory recall "release policy" --thread-id architecture-review
uv run ghost memory recall "release policy" --view history \
  --thread-id architecture-review
```

Copy the opaque `mem_...` ID from the current result before correcting or
forgetting. Current view is answer-facing. History is an audit view and may
contain `status: deleted_soft`; historical handles are not republished for
mutation.

## Correct a memory without rewriting history

```bash
uv run ghost memory correct mem_0123456789abcdef01234567 \
  "The release policy requires exact-head CI and protected merge." \
  --thread-id architecture-review
```

SEAM adds the replacement and `supersedes` relation before retiring the old
record. Repeating the exact command is idempotent. Use `--idempotency-key KEY`
when an external workflow already owns a durable operation key.

## Forget a memory deliberately

```bash
uv run ghost memory forget mem_89abcdef0123456789abcdef \
  --confirm mem_89abcdef0123456789abcdef \
  --thread-id architecture-review
```

The exact repeated ID is a local confirmation gate. SEAM then performs
auditable canonical soft-delete and recoverable derived cleanup. Use current
recall to verify absence and history recall to verify lifecycle status.

## Prove thread isolation locally

```bash
uv run ghost memory remember "Thread A marker." --thread-id thread-a
uv run ghost memory recall "Thread A marker" --thread-id thread-a
uv run ghost memory recall "Thread A marker" --thread-id thread-b
```

The second recall should be empty. This proves the configured session boundary,
not hosted multi-user tenancy; that additionally requires authenticated SEAM
principal mode.

## Back up and recover conversation checkpoints

Create a consistent backup and retain the printed SHA-256 separately:

```bash
uv run ghost checkpoint backup /secure/backups/ghost-checkpoints-20260826.db
uv run ghost checkpoint verify /secure/backups/ghost-checkpoints-20260826.db \
  --sha256 EXPECTED_64_HEX_DIGEST
```

Restore only while the owning Ghost process is stopped or drained, and restore
to a new path:

```bash
uv run ghost checkpoint restore \
  /secure/backups/ghost-checkpoints-20260826.db \
  /srv/ghost/recovery/checkpoints.db \
  --sha256 EXPECTED_64_HEX_DIGEST
GHOST_CHECKPOINT_DB=/srv/ghost/recovery/checkpoints.db \
  uv run ghost --thread-id recovery-smoke "Report the current thread boundary."
```

The restored file contains execution state only. Validate SEAM memory and
principal/namespace isolation separately; see
[recovery and observability](RECOVERY_AND_OBSERVABILITY.md).

## Build a future specialist adapter safely

Construct one `DelegationEnvelope` per attempt. Name the parent turn, role,
objective, ceilings, complete tool allowlist, absolute readable roots, and SEAM
namespace/workspace/project. Feed only those capabilities to the adapter, raise
`TimeoutError` on deadline, translate root cancellation to
`SpecialistCancelled`, and return opaque `SpecialistEvidence` references.

Verify the provider-free boundary first:

```bash
uv run pytest tests/test_specialists.py -q
uv run ruff check src/ghost/specialists.py tests/test_specialists.py
```

Do not register a live specialist or claim improvement until the equal-budget
Q3 comparison and G1/G2 prerequisites pass. See the
[specialist contract](../architecture/SPECIALIST_CONTRACT.md).

## Grant read-only repository access

```bash
export GHOST_TOOL_ROOTS="/path/to/repository:/path/to/research-notes"
uv run ghost "Find the roadmap's current Stage 1 exit condition and cite the file."
```

Ghost cannot read outside the resolved roots through these tools.
Repository-search globs must be relative and traversal-free, such as
`**/*.py`. Absolute globs and patterns containing `..` are refused. Each match
is resolved and checked against the root that enumerated it before Ghost opens
or reports the file.

## Enable shell access with approval

```bash
export GHOST_ENABLE_SHELL=1
export GHOST_SHELL_WORKDIR="/path/to/repository"
export GHOST_SHELL_TIMEOUT=120
uv run ghost "Run the CLI test file and explain any failure."
```

The CLI asks on `/dev/tty` before each command. Declining returns a normal tool
result to the model.

## Run unattended only inside a deliberate boundary

```bash
export GHOST_ENABLE_SHELL=1
export GHOST_SHELL_APPROVAL=0
export GHOST_SHELL_WORKDIR="/isolated/worktree"
uv run ghost "Run the pre-approved provider-free verification plan."
```

This disables consent prompts; it does not sandbox the process. Use a separate
OS/container/VM boundary and restricted credentials if authority must be
limited.

## Inspect remembered evidence mid-turn

Ask Ghost to use `seam_recall` and cite `record_id` values:

```bash
uv run ghost "Use seam_recall to find the exact source of the last release decision. Cite record IDs."
```

An empty result is evidence of no retrieved match, not proof that the fact was
never stored.

## Verify the agent without provider spend

```bash
uv run ruff check .
uv run pytest
uv build
git diff --check
```

Report live tests as deselected unless separately run.

## Reproduce the frozen Stage 1 contract baseline

From a clean committed checkout:

```bash
uv run python -m tools.evaluation validate-fixtures
uv run python -m tools.evaluation smoke --output /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation verify /tmp/ghost-stage1-smoke.json
uv run python -m tools.evaluation gate /tmp/ghost-stage1-smoke.json
```

Record the printed bundle hash and exact Git SHA. Do not call the resulting
BIL-0 stub score a capability result. For corpus schema, failure attribution,
provider-backed successor requirements, and immutable-version rules, follow
[the Stage 1 frozen suite](../evaluation/STAGE1_FROZEN_SUITE.md).

## Run approved live tests

After confirming model, key source, expected call count, and spend boundary:

```bash
uv run pytest -m live tests/test_live_agent.py -q
```

Do not place the key on the command line or in history output.

## Add a tool safely

1. Classify it read-only or write-capable.
2. Add narrow typed inputs and explicit bounds.
3. Resolve paths/authority before action.
4. Bound result bytes/chars and time.
5. Add it to `WRITE_TOOLS` if it can change anything.
6. Wire it in `_build_tools` only behind the correct operator gate.
7. Add success, refusal, traversal, timeout, output, and verification tests.
8. Update trust boundaries, complete blueprint, command reference, and roadmap.
9. Append history and run closeout.

## Add or change an environment variable

1. Parse it in `GhostSettings` or the clearly owned optional subsystem.
2. Define a conservative default and numeric/path bounds.
3. Add it to `.env.example` without a real value.
4. Add config tests for default, valid, invalid, and boundary cases.
5. Update [configuration](CONFIGURATION.md) and this how-to if operator behavior
   changes.

## Add a documentation page

1. Put it under the correct `docs/` domain.
2. Link it from `docs/INDEX.md` and the relevant `docs/README.md` route.
3. Use relative repository links and label landed/local/planned state.
4. Run `uv run pytest tests/test_docs.py -q`.
5. Append history if the page changes a governing/current/build boundary.

## Record a material build change

1. Append one new `HISTORY#NNN` entry.
2. Update status/ledger/ADR as required.
3. Register a successor handoff when the resume boundary changes.
4. Run:

```bash
uv run python -m tools.history.closeout --agent codex
```

5. Then run code/package verification appropriate to the change.

## Recover from a handoff

```bash
sed -n '1,180p' docs/handoffs/INDEX.md
latest=$(sed -n 's/^latest: `\(.*\)`/\1/p' docs/handoffs/INDEX.md)
sed -n '1,260p' "$latest"
git status --short --branch
git fetch --prune origin
```

Reconcile the handoff with live state. A handoff records what was true at its
timestamp; it does not override later remote facts.

## Regenerate Ghost branding

```bash
uv run python -m tools.branding.assets fonts
uv run python -m tools.branding.assets png branding/ghost.svg /tmp/ghost.png --width 1024
uv run python -m tools.branding.assets ico branding/ghost-mark.svg /tmp/ghost.ico
uv run pytest tests/test_brand_assets.py -q
```

Use `/tmp` or another external review directory until outputs are intentionally
approved for the repository.

## Start the local avatar lane

Browser/bridge experiment:

```bash
uv run ghost-avatar
GHOST_AVATAR=1 uv run ghost "Open the requested research task."
```

Direct desktop experiment:

```bash
DISPLAY=<x11-display> /usr/bin/python3 src/ghost/avatar/desktop_pet.py
```

These commands operate unmerged code. Follow the avatar handoff and do not call
the result shipped.

## Diagnose “docs say one thing, code says another”

1. Identify the exact source line and reproducible command.
2. Check `REPO_LEDGER.md` and relevant ADR for the intended invariant.
3. Check `HISTORY_INDEX.md` and dated update/audit for temporal context.
4. Treat code plus reproduced behavior as implemented state.
5. Correct current docs/status and append history; do not rewrite older history.
