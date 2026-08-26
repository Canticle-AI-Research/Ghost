# Canonical Ghost foundation

**State:** merged and exact-head hosted checks green.

PR #6 established Ghost's rebuildable wiki, complete system blueprint,
installation and command references, how-tos, roadmap, canonical history,
Temporal Chain tooling/template, licensing/company foundation, and launcher
tooling, closing roadmap items T0, T1, and R0. Implementation commits
`dcbad97b9583de403438241384e5dffb9776c810` and
`fc0ebbb31966cf35fd36d442d603ac81e14a90ee` merged as
`a5997c616e946496875a3ba4772ab9759b46f2d7`.

Public CI passed `repo-hygiene`, `brand-assets`, and `package-smoke` on exact PR
head `fc0ebbb31966cf35fd36d442d603ac81e14a90ee` in run
[`32918686149`](https://github.com/Canticle-AI-Research/Ghost/actions/runs/32918686149)
and on the exact merge head in run
[`32918733013`](https://github.com/Canticle-AI-Research/Ghost/actions/runs/32918733013).
The full provider-free local suite, Ruff, build, closeout, diff hygiene, and
gitleaks also passed before publication. The final complete committed-diff
review reported zero findings.

Private SDK integration and provider-live tests were not run. The avatar
runtime/assets remain preserved local WIP and were not part of PR #6.
