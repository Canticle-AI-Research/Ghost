# Rebuild Ghost from the documentation

This is the top-level reconstruction contract. A competent engineer with
repository access should be able to rebuild Ghost's current behavior without
private conversation history or undocumented machine state.

## Inputs

- this Git repository at a named commit;
- an authorized SEAM service implementing the documented opaque v1 routes;
- Python 3.11–3.14 and `uv`;
- an OpenAI API key only for model-backed execution or live tests;
- optional Chrome/fontconfig/ffmpeg for brand outputs;
- optional Linux X11/GTK/Blender dependencies for the local avatar lane.

This is the public rebuild contract. It requires service access at runtime but
never private SEAM source. A hosted service and a licensed local SEAM Node may
implement the same additive HTTP boundary.

## Build graph

```text
source checkout
   │
   ├─ pyproject.toml + uv.lock ──► resolved Python environment
   │                                  │
   │                                  ├─ deepagents / langchain / langgraph
   │                                  └─ httpx → authenticated SEAM v1 service
   │
   ├─ src/ghost/ ─────────────────► canticle-ghost wheel
   │                                  │
   │                                  └─ `ghost` console command
   │
   ├─ branding/ + tools/branding/ ─► reproducible static identity assets
   │
   ├─ tests/ ──────────────────────► provider-free + live qualification
   │
   └─ docs/ + HISTORY.md ──────────► operational blueprint + chronology
```

License and artifact inputs are independently required: `LICENSE`, `NOTICE`,
package metadata, excluded brand assets, dependency notices, and private-source
dependency scans must agree before distribution.

## Reconstruction sequence

1. Follow [installation](../operations/INSTALLATION.md) through `uv sync --frozen`.
2. Verify `pyproject.toml` and `uv.lock` contain only public package sources.
3. Run `uv run ghost --help` to prove the import/entry-point chain.
4. Run the provider-free qualification in
   [testing and qualification](../evaluation/TESTING_AND_QUALIFICATION.md).
5. Configure a throwaway SEAM namespace and an isolated checkpoint database.
6. Run one one-shot turn and one restarted-thread turn using
   [operator how-tos](../operations/HOW_TO.md).
7. Inspect the memory lifecycle against
   [complete system blueprint](../architecture/COMPLETE_SYSTEM_BLUEPRINT.md).
8. Regenerate one brand asset and compare its dimensions/format through the
   brand tests.
9. Rebuild and verify the repository history index.
10. Run a package build and inspect the wheel entry point.

## Behavioral components to recreate

| Component | Source authority | Required proof |
|---|---|---|
| Settings | `src/ghost/config.py` | bounds/default tests |
| SEAM adapter | `src/ghost/seam_memory.py` | opaque HTTP contract tests + authorized live round trip |
| Turn contract | `src/ghost/lifecycle.py` | completion/failure/action tests |
| Agent adapter | `src/ghost/application.py` | real graph construction and live lane |
| Recall middleware | `src/ghost/middleware.py` | real ModelRequest tests and injection bounds |
| Tools | `src/ghost/tools.py` | path, output, approval, timeout, write-set tests |
| CLI | `src/ghost/cli.py` | help, one-shot, interactive exit/error tests |
| Checkpoints | `application.py` + SQLite saver | restart persistence test |
| Branding | `branding/` + `tools/branding/` | font/render/ICO tests |
| Continuity | `HISTORY.md` + `tools/history/` | index/handoff/snapshot verification |
| Avatar | `src/ghost/avatar/` local WIP | local tests and actual rendered review; not mainline |

## No hidden source rule

The following may remain machine-specific but must be named:

- provider and SEAM service credentials;
- ignored `.env.local` values;
- service-owned canonical operator data;
- provider billing authorization;
- desktop display/compositor and GTK packages;
- local avatar generation sources or paid provider outputs not approved for
  repository inclusion.

None of these may be silently assumed to be part of the codebase. If a build
depends on one, the relevant installation/how-to page must say so and provide a
safe detection command.

## Fidelity gate

The rebuild is successful only when:

- the frozen public dependency graph installs without re-resolution;
- provider-free tests and Ruff pass;
- the wheel/sdist clean install and console-entry smoke pass;
- one isolated live model/memory turn passes when explicitly authorized;
- history, handoffs, docs, and local links verify;
- no operator data, credential, private session link, or generated local state
  enters the candidate commit; and
- all skipped external/live work is named rather than implied complete.
