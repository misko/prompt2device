# Native parity bridge source review

Reviewed commit: `7407a42e2add4b30951f486f06be005c6327be86`

Verdict: **PASS — source/code scope only.** No blocking correctness findings in
the reviewed change.

The converter now resolves an exactly identified dossier before symbol
synthesis, translates documented schematic identities to physical pad names,
retains source ports/functions/nets and NC status, and fails closed for
ambiguous, malformed, incomplete, incompatible-footprint, and unsafe
many-to-one identities. The extra USB shell port remains a same-raw-identity
duplicate; distinct aliases collapsing onto one pad require equal non-null
nets. The Q_IN fused-drain fixture confirms that pads 6–8 are not invented.

`part_identity.py` is the shared parser used by the converter, P-PINMAP, and
the board path. Datasheet selection is tied to hidden exact MPN/supplier
identity and overwrites a footprint-library stale URL; it is not based on the
displayed value. Both grid and layout emitters include the same metadata.

Validation performed:

- `python3 tests/t1_native_parity_bridge.py`: 6 passed. It invokes native
  KiCad schematic-parity DRC successfully for both grid and layout output,
  and covers USB contacts/NCs, stale Datasheet replacement, alias conflict,
  missing NC collapse, ambiguous identity, malformed authority, and fused
  Q_IN behavior.
- `python3 tests/t1_pin_map.py`: 8 passed, 0 failed.
- `python3 -m py_compile` for all changed Python modules: passed.
- `git diff --check`: only reports an extra trailing blank line in the new
  `part_identity.py`; this is non-functional.

The sparse implementation worktree cannot run the complete historical
converter/board suites because archived fixture projects and source PDFs are
absent. Those failures are environmental (missing files), not evidence of a
change regression. Full-suite compatibility remains for the complete root
workspace. This review does not approve Crow board regeneration, placement,
routing, DRC closure, or release.
