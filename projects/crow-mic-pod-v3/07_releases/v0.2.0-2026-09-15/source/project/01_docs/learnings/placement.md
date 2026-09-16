
## 2026-09-12 23:07 UTC — source-coordinate/pad-identity mismatch

MEASURED: the three authored connector/clamp seeds target NC or opposite-audio pads after the source package is placed on the bottom side. Correct netlist connectivity and standalone placement DRC cannot prove that hard-coded route points target those pins. Project-local prevention: independently bind every seed start/end to actual native pad number, net, side and copper envelope before accepting source paths; preserve this exact rejected source as the negative fixture. No producer gate or clearance exception is warranted.
