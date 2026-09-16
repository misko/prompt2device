# Littelfuse 1812L035/60MR primary-source fact record

Accessed: 2026-09-01
Authority status: exact manufacturer document facts pinned in this ordinary
record; upstream PDF bytes were readable through the documentation reader but
the direct download endpoint returned HTTP 403, so no raw-PDF hash is claimed

Primary document:

- [Littelfuse 1812L Series datasheet](https://www.littelfuse.com/assetdocs/resettable-ptcs-1812l-datasheet?assetguid=ca5c80cb-504e-4a8a-8e74-0107520a1717),
  revision GD dated 2024-06-10, eight pages.

Exact `1812L035/60` electrical-table facts used by the carrier:

- 0.35 A hold current and 0.70 A trip current at 20 C;
- 60 V maximum voltage and 10 A maximum fault current;
- 1.00 W typical tripped-state dissipation;
- maximum trip time 0.15 s at the table's 8.00 A test current;
- 0.400 ohm minimum initial resistance and 1.700 ohm maximum resistance one
  hour after trip or the specified reflow exposure.

The ambient-operation table gives 0.20 A hold at 70 C and 0.16 A at 85 C.
The latter is 60 percent above the 0.10 A continuous spoke requirement. The
package table keeps the 1812 body and pad family; the `/60` member has a
1.2-1.8 mm height envelope. The ordering table fixes the exact standard,
halogen-free 1000-piece tape-and-reel ordering number as `1812L035/60MR`.

The carrier voltage-loss calculation uses the published 1.700 ohm `R1max`,
never a typical value. This document-level selection does not prove realized
hot resistance, copper heat sinking, fault-clearing time at the appliance's
prospective current, trip recovery, or one-fault/seven-healthy operation.
