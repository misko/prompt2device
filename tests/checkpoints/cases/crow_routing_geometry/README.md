# Maintainer controls

`reference/geometry.json` is the valid outside-snapshot repair used to prove
the checkpoint is solvable. `bypass/geometry.json` connects with two vias and
B.Cu, proving that a connectivity-only shortcut cannot pass the protected
zero-via/F.Cu gate. Neither is included in the solver snapshot.
