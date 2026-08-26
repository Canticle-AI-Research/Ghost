# Stage 1 clean-source BIL-0 baseline frozen

handoff_id: `ghost-stage1-baseline-frozen-20260825`
supersedes: `ghost-stage1-frozen-evals-qualified-20260825`
handoff_status: `superseded`
history: `HISTORY#040`
created_at: `2026-08-25T22:10:35-05:00`

## Frozen evidence

Infrastructure commit `bc18555d364a9ed49ce9be2e6c35378bbad29467`
was clean before the tracked baseline was generated. The sealed artifact is
`evals/runs/stage1/ghost-stage1-frozen-v1-bil0-baseline.json`.

- suite: `ghost-stage1-frozen-v1`;
- cases: 20 in each of two arms;
- fixture hash: `4f10f3d8022beeb3ac7adbf3b01bd1b727c81d9db48b8388f8e129b84e3ed61d`;
- bundle hash: `6b16ad744b1dc585fc197150d0e0aee4254c985b1e0810619f0ed64f44fb03ad`;
- verifier and safety gate: pass;
- candidate contract failures: zero;
- isolation violations: zero;
- forbidden effects: zero; and
- claimable: false.

The no-memory arm is present and differs under the scripted contract, but that
difference is not a model-quality measurement.

## Next

Run the complete provider-free suite and build against this successor tree,
push the branch, open the focused PR, require the hosted `stage1-evals` context,
and merge only after exact-head CI. Provider/live and release-candidate proof
remain separately gated and were not run.
