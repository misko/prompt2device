# Current operated connector census — 2026-09-22

Current source contains eleven board connectors: J1–J8 are Wurth 615008160221 Crow spoke jacks; J_USB is GCT USB4105-GF-A-120; J_PWR is Molex43650-0200; J_JTAG is Samtec FTSH-105-01-L-DV-K. The source expansion contains all eleven, and their exact native footprints load. This is a source census, not a native-board geometry or mechanical acceptance claim.

The retained spoke mate is Weidmuller8909650150 from the previous Crow spoke interface. Its prior board placement and service approval are not inherited. The selected USB cable is ASSMANN A-USB31C-20A-100, with its manufacturer drawing retained in the local dossier. Exact power harness and JTAG probe/mating cable selection remain owed.

Normal service assumes all eight spoke cables plus power and USB can coexist. Bench service adds the JTAG cable without removing those functional connections. These are requirements for the service envelope, not verified access. Receptacle axes in the initial contract are planning candidates only; no board outline, edge registration or placement is admitted by this record.

The contract now contains one profile for each actual connector family, preserving unknown geometry, tool/grip, cable bend, reaction and tolerance facts as unknown. Required source facts and allowed physical deferrals still need individual classification before source admission. No null value or unknown grade is a pass.

Compiler observation: the current connector assembly parser rejects J_USB because its _REF pattern requires a digit. J_USB, J_PWR and J_JTAG are actual source references, not unannotated placeholders. Consequently this census has not compiled and owns no acceptance receipt. A targeted parser regression/fix is required before unknown mechanical rows can be classified; do not disguise this failure by inventing references in the contract.
