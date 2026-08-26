# Continuity template and workflow candidate integrated

handoff_id: `ghost-continuity-template-integrated-20260825`
supersedes: `ghost-public-runner-next-20260825`
handoff_status: `superseded`
history: `HISTORY#025`
created_at: `2026-08-25T14:30:00-05:00`

## Completed local boundary

- Ghost retains an append-only `HISTORY.md`, exact generated index, bounded
  context packs, ignored snapshots, and one verified handoff chain.
- `verify_append_only` compares the current history to an exact Git base.
- `templates/temporal-chain/` installs the core and handoff layers into
  a fresh Git repository without Ghost/SEAM names or runtime dependencies.
- Automatic public continuity uses `ubuntu-latest` without resolving private
  packages; private `seam-box` CI is manual-only.
- Paid live tests require the explicit `run_live` workflow input.

## Verification

- focused docs/history/CI contract: 29 passed before final closeout;
- scoped Ruff over continuity/template/tests: passed;
- template proof: fresh temporary Git repository installed, four
  standard-library tests passed, closeout wrote a snapshot, and required
  continuity passed;
- Ghost closeout: 12 docs/history tests passed and required snapshot continuity
  verified 25 entries with `HISTORY#025` current;
- template plus CI-contract slice: 18 passed;
- full provider-free suite: 184 passed, eight live tests deselected;
- wheel and source distribution: built successfully;
- scoped continuity/template Ruff: passed;
- full Ruff: retained the five known local avatar/image-tool findings; and
- `git diff --check`: passed.

The final closeout snapshot and any broader qualification results are reflected
by the current ignored snapshot and working tree, not by a merged commit.

## Unresolved remote boundary

- The workflow and template candidate is not committed, pushed, reviewed, or
  merged; GitHub's default branch still has the old workflow topology.
- Repository visibility, runner-group scope, and outside-collaborator approval
  settings need live verification.
- Hosted continuity and manual private CI need controlled exact-head runs after
  safe publication.

## Next work

1. Review the candidate diff and publish it through a path that does not expose
   `seam-box` to untrusted workflow code.
2. Verify external GitHub Actions and runner-group controls.
3. Record merged/exact-head workflow evidence as a successor event.
4. Resume the preserved U1 avatar implementation after the continuity
   foundation is protected-main fact.

## Preserve

- Do not reset or delete the local avatar source, assets, tests, or art tools.
- Do not stage ignored snapshots, local databases, `.env.local`, or Blender
  working files.
- Keep the reusable template repository-neutral; optional SEAM routing and
  streams must arrive with their complete verification layer.
