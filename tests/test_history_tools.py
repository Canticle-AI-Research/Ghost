"""Credential-free gates for Ghost's canonical history and rebuild blueprint."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tools.history.build_context_pack import select_entries
from tools.history.handoffs import load_handoffs
from tools.history.model import HISTORY_PATH, INDEX_PATH, load_history
from tools.history.rebuild_index import render_index
from tools.history.verify_append_only import verify_append_only
from tools.history.verify_handoffs import verify as verify_handoffs

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
BLUEPRINT = DOCS / "architecture" / "COMPLETE_SYSTEM_BLUEPRINT.md"
AVATAR_BLUEPRINT = DOCS / "architecture" / "AVATAR_SYSTEM.md"
COMMANDS = DOCS / "operations" / "COMMAND_REFERENCE.md"
CONFIGURATION = DOCS / "operations" / "CONFIGURATION.md"


def test_history_is_contiguous_and_latest_entry_is_current_slice() -> None:
    entries = load_history()
    assert [entry.id for entry in entries] == list(range(1, len(entries) + 1))
    assert entries[-1].id >= 23
    assert entries[-1].date >= entries[-2].date


def test_history_index_is_exact_generated_output() -> None:
    assert INDEX_PATH.read_text(encoding="utf-8") == render_index()


def test_append_only_check_accepts_a_successor_and_rejects_a_rewrite() -> None:
    base = HISTORY_PATH.read_text(encoding="utf-8")
    # Unchanged history is valid; changing any byte in the established prefix is not.
    verify_append_only(base, base)
    with pytest.raises(ValueError, match="not append-only"):
        verify_append_only(base.replace("Ghost", "Changed", 1), base)
    with pytest.raises(ValueError, match="changed an existing entry"):
        verify_append_only(base, base + "Appended prose without a new history entry.\n")


def test_handoff_registry_is_one_verified_temporal_chain() -> None:
    verify_handoffs()


def test_handoff_index_and_documents_must_agree(tmp_path: Path) -> None:
    source = ROOT / "docs" / "handoffs"
    target = tmp_path / "docs" / "handoffs"
    target.mkdir(parents=True)
    for document in source.glob("*.md"):
        (target / document.name).write_text(document.read_text(encoding="utf-8"), encoding="utf-8")

    index = target / "INDEX.md"
    index.write_text(
        index.read_text(encoding="utf-8").replace(
            "ghost-public-runner-closed-20260825",
            "wrong-index-id",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="invalid handoff metadata"):
        load_handoffs(root=tmp_path)

    index.write_text((source / "INDEX.md").read_text(encoding="utf-8"), encoding="utf-8")
    (target / "unregistered.md").write_text("not registered\n", encoding="utf-8")
    with pytest.raises(ValueError, match="registry mismatch"):
        load_handoffs(root=tmp_path)


def test_handoff_created_at_values_are_strictly_newest_first(tmp_path: Path) -> None:
    source = ROOT / "docs" / "handoffs"
    target = tmp_path / "docs" / "handoffs"
    target.mkdir(parents=True)
    for document in source.glob("*.md"):
        text = document.read_text(encoding="utf-8")
        if document.name == "2026-08-25-public-runner-closed.md":
            text = text.replace(
                "2026-08-25T20:04:30-05:00",
                "2026-08-25T16:10:00-05:00",
            )
        (target / document.name).write_text(text, encoding="utf-8")
    (tmp_path / "HISTORY.md").write_text(HISTORY_PATH.read_text(encoding="utf-8"), encoding="utf-8")

    with pytest.raises(ValueError, match="created_at values"):
        verify_handoffs(root=tmp_path)


def test_context_pack_selection_is_bounded_and_topic_aware() -> None:
    entries = load_history()
    selected = select_entries(entries, latest=2, topics=("docs",), ids=())
    assert 1 <= len(selected) <= 2
    assert all("docs" in entry.topics for entry in selected)
    assert selected == sorted(selected, key=lambda entry: entry.id)


def test_every_runtime_module_is_named_by_the_architecture_blueprint() -> None:
    text = "\n".join(
        [
            BLUEPRINT.read_text(encoding="utf-8"),
            AVATAR_BLUEPRINT.read_text(encoding="utf-8"),
        ]
    )
    missing = []
    for path in sorted((ROOT / "src" / "ghost").rglob("*.py")):
        if path.name == "__init__.py":
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative not in text and path.name not in text:
            missing.append(relative)
    assert not missing, f"runtime modules absent from architecture blueprint: {missing}"


def test_every_ghost_environment_variable_in_source_is_documented() -> None:
    names: set[str] = set()
    pattern = re.compile(r'["\'](GHOST_[A-Z0-9_]+)["\']')
    for path in sorted((ROOT / "src" / "ghost").rglob("*.py")):
        names.update(pattern.findall(path.read_text(encoding="utf-8")))
    text = CONFIGURATION.read_text(encoding="utf-8")
    missing = sorted(name for name in names if f"`{name}`" not in text)
    assert not missing, f"environment variables absent from configuration docs: {missing}"


def test_command_reference_covers_all_repository_entrypoints() -> None:
    text = COMMANDS.read_text(encoding="utf-8")
    required = {
        "uv run ghost",
        "uv run ghost-avatar",
        "tools.branding.assets fonts",
        "tools.branding.assets css",
        "tools.branding.assets png",
        "tools.branding.assets pdf",
        "tools.branding.assets ico",
        "tools.branding.assets video",
        "tools.history.rebuild_index",
        "tools.history.build_context_pack",
        "tools.history.verify_handoffs",
        "tools.history.verify_append_only",
        "tools.history.write_snapshot",
        "tools.history.verify_continuity",
        "tools.history.closeout",
        "tools/make_galaxy_sprite.py",
        "tools/export_ghost_glb.py",
        "src/ghost/avatar/desktop_pet.py",
        "templates/temporal-chain/install.py",
        "tools/launchers/install.py",
        "tools.history.recorded_fact_audit",
        "tools/git-hooks/install.sh",
    }
    missing = sorted(command for command in required if command not in text)
    assert not missing, f"entrypoints absent from command reference: {missing}"


def test_history_commands_in_active_docs_use_uv_python() -> None:
    failures = []
    pattern = re.compile(r"(?<!uv run )python -m tools\.history")
    for path in [ROOT / "AGENTS.md", *sorted(DOCS.rglob("*.md"))]:
        if pattern.search(path.read_text(encoding="utf-8")):
            failures.append(path.relative_to(ROOT).as_posix())
    assert not failures, f"bare python history commands are not portable here: {failures}"


def test_history_does_not_contain_private_session_or_secret_shapes() -> None:
    text = HISTORY_PATH.read_text(encoding="utf-8")
    forbidden = ("chatgpt.com/share/", "claude.ai/share/", "BEGIN PRIVATE KEY")
    assert not [value for value in forbidden if value in text]


def test_path_move_ledger_rows_resolve_and_name_a_real_entry() -> None:
    """The ledger is what lets an append-only chain survive reorganization.

    A row that points at a still-missing path, or cites an entry that does not
    exist, would let a dangling historical reference pass verification.
    """
    from tools.history.model import load_path_moves, resolve_ref

    moves = load_path_moves()
    entries = {entry.id for entry in load_history()}
    ledger = (DOCS / "history" / "PATH_MOVES.md").read_text(encoding="utf-8")

    for cited in re.findall(r"HISTORY#(\d{3})", ledger):
        assert int(cited) in entries, f"path-move ledger cites missing HISTORY#{cited}"

    for old, new in moves.items():
        assert not (ROOT / old).exists(), f"{old} is recorded as moved but still exists"
        if new is None:
            continue
        target = resolve_ref(old, moves)
        assert target is not None
        assert (ROOT / target).exists(), f"{old} moves to missing path {target}"


def test_history_topics_use_the_controlled_vocabulary() -> None:
    """An uncontrolled topic silently drops an entry out of topic-scoped packs."""
    protocol = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    block = protocol.split("Controlled topics:", 1)[1].split("##", 1)[0]
    vocabulary = set(re.findall(r"`([a-z]+)`", block))
    assert vocabulary, "controlled topic vocabulary is missing from AGENTS.md"
    unknown = sorted(
        {topic for entry in load_history() for topic in entry.topics} - vocabulary
    )
    assert not unknown, f"history topics outside the AGENTS.md vocabulary: {unknown}"
