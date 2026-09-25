# Independent review — e07 power-board edge attachment binding

Reviewed `fae7198d` relative to the accepted containment-only scope in
`90604d58`. **PASS for that scope only.**

The allowlist contains exactly two reviewed board hashes: the original d0
board and the Q_PRE-repair power board
`e07ed8bc663fdfd4ce39477165b656b0dcf2bfbae54d84ec501bfccf326d22ef`.
Each source attachment must equal the hash of the board currently being
checked; therefore a d0 attachment row fails on e07 rather than inheriting
approval. The native outline digest remains pinned.

The new focused test independently confirms the same 569-reference census and
identical `_physical_envelope` geometry for every eligible J_PWR/J1–J8
connector on d0 and e07. It accepts an e07 row only after changing its bound
board hash, and rejects the stale d0 row. No references, directions,
projection limit, footprint/drawing hashes, poses, cell shape, material/pad/
drill checks, or downstream route/capacity/FULL paths broadened.

Validation run:

- focused edge attachment tests: 4/4 pass;
- full `test_p1*.py` suite: 172/172 pass.

This keeps the prior no-credit disposition: physical-cell containment only;
no P1/P2/P3, routing, return, capacity, connector FULL, P-OUT or release
acceptance.
