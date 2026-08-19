# Ghost updates

Dated reports on what changed in Ghost, why, and what the evidence was.

This directory is the provenance track. A report is written when work lands,
not when it is planned, and it records what was actually verified rather than
what was intended. Reports are append-only: a later report may supersede an
earlier one, but an earlier report is not edited to agree with it. If a report
turns out to be wrong, the correction is a new report that says so and names
the one it corrects.

## Convention

- one file per landed piece of work, named `YYYY-MM-DD-short-slug.md`;
- state what was verified and how, not what was believed;
- name the commits, so a claim can be walked back to a diff;
- record what was found and NOT fixed as explicitly as what was;
- every file here must be linked from [`../INDEX.md`](../INDEX.md), which
  `tests/test_docs.py` enforces.

## Relationship to the roadmap

[`../roadmap/SECOND_BRAIN_ROADMAP.md`](../roadmap/SECOND_BRAIN_ROADMAP.md)
says what is intended and gates each stage on an exit condition. A report here
says what actually happened. When a report closes a roadmap item, it names the
item; the roadmap's status language (Current / Governing / Planned /
Exploratory) is only allowed to move on the evidence of a report.

## Index

| Date | Report | Covers |
|---|---|---|
| 2026-08-19 | [CI, three defects, and the memory boundary](2026-08-19-ci-and-test-coverage.md) | Roadmap slice item 6; tests 18 → 81 |
