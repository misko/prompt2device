# Reviewed P1 edge-cell authority

`physical_cell_edge_authority.json` migrates the independently reviewed
J_PWR/J1–J8 nominal north-edge courtyard evidence out of the reusable P1
checker. It pins the d0 and e07 boards separately, their native outline, exact
fixed poses, footprint and supplier-drawing bytes, and the two retained
independent review notes. The checker still inspects live F.CrtYd, F.Fab,
material, pads and drills. J_USB is absent and cannot use this authority.

The trusted caller must supply this **reviewed expected digest** separately
from the source request and file path:

```text
--edge-authority projects/crow-usb-carrier-v1/03_src/rules/physical_cell_edge_authority.json
--expected-edge-authority-sha256 0b60dece42aca3e84b085fd0c30847dd358a5f96dd2e26773a6b75eb22b494b4
```

Do not compute that expected value from the authority file or
`p1_corridor_requirements.yaml` during a run; doing so would let an edited
manifest approve itself. The digest binds reviewed bytes but is not a
cryptographic reviewer signature. A changed manifest needs fresh independent
review and a new expected digest at the caller's trust boundary. The
source-owned `physical_cell_edge_attachments` rows are requests, never
independent approval. Without the file and expected digest, any such request
fails closed.

The synthetic non-Crow unit fixture computes a disposable manifest digest to
exercise parsing and geometry only. The Crow acceptance tests instead use the
literal reviewed digest above and reject an edited manifest even if source
fields contain its newly computed hash.

This grant concerns physical-cell containment only. It does not qualify an
assembled edge, connector FULL, return continuity, routing, capacity, P2/P3,
P1 acceptance, fabrication or release.
