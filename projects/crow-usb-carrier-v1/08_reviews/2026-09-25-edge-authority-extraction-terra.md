# Independent review — extracted physical-cell edge authority

Reviewed `5e4090c5` and trust-boundary follow-up `1dfd1c54`.

**PASS for the stated P1 physical-cell containment scope.** The project-owned
authority record is SHA-256
`0b60dece42aca3e84b085fd0c30847dd358a5f96dd2e26773a6b75eb22b494b4`.
It binds exact d0 and e07 board subjects, their outline, the two independent
review records, each J_PWR/J1–J8 fixed pose, footprint and retained drawing.
Live checking still enforces the actual F.CrtYd projection, F.Fab shape, pads,
drills/slots, cell shape and normal foreign occupancy. J_USB is absent from the
record and remains ineligible.

The reusable reader refuses a missing or mismatched expected digest. A source
attachment is only a request and cannot supply the `edge_authority` argument.
The Crow test uses the literal reviewed digest and rejects an edited manifest
even when source fields contain that edited file's computed hash. This preserves
the caller-supplied trust boundary and prevents source self-approval.

The digest establishes exact byte identity; it is not a cryptographic proof of
reviewer identity. The caller must obtain the expected digest from the
independent reviewed project authority, rather than calculate it from mutable
source during a run. The synthetic non-Crow test intentionally derives a digest
only as a parser/geometry fixture and makes no approval claim.

Validation: edge tests 6/6; complete `test_p1*.py` suite 174/174;
`schema_reader_audit.py projects/crow-usb-carrier-v1` passes 1090/1090 declared
keys. This extraction changes no route, capacity, P1/P2/P3, connector FULL,
release, order or physical qualification gate.
