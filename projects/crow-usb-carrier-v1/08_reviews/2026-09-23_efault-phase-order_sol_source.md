# Independent review — E-FAULT phase-order repair

- Candidate: `6e8cc9368786fc60cdbd99f63c8b6a54f7d68933`
- Base: `63a2e437`
- Verdict: **ACCEPT** for adoption as a phase-order repair. This does not admit the board or its physical fault behavior.

The former [0d] invocation required `03_tscircuit/build/circuit.json` before the tscircuit producer ran. The candidate changes [0d] to `--prebuild`, retaining authored architecture, conditional-status, digest syntax, exact `bound_refs`, active spoke rails, part-value assertions, source limits, fuse/PFET calculations, and protection-path consistency. Its successful note explicitly says `PREBUILD CONTRACT ONLY; CIRCUIT OWED`. It omits only assertions that depend on generated circuit contents: digest equality, source component identities/count, pin/net topology, and fitted numeric values.

The Crow driver then invokes `early_design_check.py . --fault-envelope` without `--prebuild` immediately after the fresh tscircuit artifact is copied and diagnostics run. A mismatch stops [1d] before schematic rendering, conversion, review, or placement. The existing full `early_design_check.py .` at [1b] remains. The generic template adopts prebuild at [0d] and retains its full [1b] invocation before schematic review and placement; no external-source exception is added to its full gate. The generic template's extra blank line has no effect.

The full checker still reads `circuit.json`, compares its SHA-256 with the reviewed authored digest, and checks exact source component identities, eight TPS26625 branches, required pin/net connections, and fitted values. The candidate's cold-start test proves prebuild passes without circuit bytes while full checking fails; its stale-byte test proves prebuild labels binding owed while full checking rejects a changed digest. A contradictory authored protection envelope still fails prebuild.

Verification repeated on the candidate tree: `python3 tests/test_external_source_fault.py` **20/20**, `python3 tests/t1_early_design.py` **52/52**, `python3 tests/t1_rebuild_templates.py` **67/67**. `git diff --check 63a2e437..6e8cc9368786fc60cdbd99f63c8b6a54f7d68933` passed. I reviewed the exact four-file diff and made no source edits. No canonical rebuild or schematic generation was performed for this review.
