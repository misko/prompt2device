# RJ45 manufacturer model adoption

Retained Würth's exact 615008160221 rev1 STEP from
https://www.we-online.com/components/products/download/Download_STEP_615008160221%20%28rev1%29.stp.
The 961453-byte file has SHA-256
`f69068769f95f99f0c23aeaaafde9d2a9b9f57c2b8238aeacdfd418578510d7b`.

SOL measured the complete model with OpenCascade AddOptimal; root reproduced
the same extents using a separate installed OpenCascade environment:

| Model axis | Minimum mm | Maximum mm | Size mm |
|---|---:|---:|---:|
| X, axial | -0.250000 | 13.200054 | 13.450054 |
| Y, lateral | -3.479018 | 13.797143 | 17.276161 |
| Z, board normal | -3.344712 | 15.748181 | 19.092892 |

This includes modeled spring fingers and terminal tails, unlike the smaller
dimensioned rigid shell. It is nominal manufacturer geometry, not a tolerance
or deflection bound. The contract binds the model directly; it does not turn
these extents into a manufactured maximum envelope or a registered PCB pose.

Root's older reader emitted one unresolved-reference diagnostic but returned
ReadDone, transferred its single root, and produced a valid BRep with identical
extents. Text inspection found no undefined numbered STEP entity references.
The diagnostic remains recorded; it is not proof of missing physical geometry
nor a claim of a warning-free import. Exact native registration and service
clearance review must reopen the model at placement.

The raw model is stored under `03_src/lib/3dmodels/wurth/`. The existing
KiCad-oriented model has a different hash and coordinate system; root also
reopened it and found the same nominal extents with X/Y exchanged. The new
evidence does not silently replace that board-model transform.

Connector compilation is valid INCOMPLETE: 4 assemblies, 11 instances,
17/45 known facts and 28 unknowns. RJ45 receptacle model evidence is now known;
mate/service and other connector facts remain open. No board geometry changed.
