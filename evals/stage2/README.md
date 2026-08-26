# Stage 2 memory-governance fixtures

`memory_governance.json` freezes provider-free cases for admission relevance,
contradiction/correction, retry identity, stale-history handling, forgetting,
and thread/project isolation. `tests/test_memory_evaluation.py` executes the
cases against Ghost's real classifier and opaque HTTP adapter with the
stateful contract fake.

This suite proves mechanisms and zero leakage in the fixed fake boundary. It
does not run a model, measure answer quality, compare against a no-memory arm,
or authorize a G2 improvement claim. A future sealed Q3 bundle must name and
diff a baseline before G2 can satisfy its exit gate.
