# Buffer packaging adoption — 2026-09-22

Selected SN74LVC1G125DCKT / C2675550 for U_MCLK_BUF, U_ADC_CLOCK_OK and U_ADC_READY, replacing SN74LVC1G125DCKR / C7833. Root inspected the retained TI SCES223 package-option and packing tables: both order codes use the same SC70 DCK five-pin device, Active/Production, −40 to 125 °C, with the same listed finish and moisture class. R is 3,000-unit tape/reel; T is 250-unit tape/reel. Package drawing, function and electrical limits are unchanged.

The complete original dossier and primary PDF are retained under the new exact order code. PDF SHA-256 remains 65afa3f9d879b37cb8be507caf84804b24bceeb2e0782ba449fff72160994e4c. Only the MPN, local directory reference and supplier code changed in that dossier. The separate missing escape record remains under repair and is not claimed resolved here.

The dated exact DigiKey observation is Active, stock 7,507, minimum/multiple 1; owning JLC C2675550 evidence reports stock 186. Five-board demand is 15. Root reran the owning shopping gate over the complete current 85-part BOM: 70 rows have two qualifying pools, 15 have one, and zero are unparseable. This is a composition of dated supplier observations, not an order-time allocation or a simultaneous fresh full query.

Expanded-source comparison changes exactly three records, limited to the above references' manufacturer part numbers and supplier codes. All other records are equal. Fresh source render has 489 components, 85 MPNs, 1,619 ports, 1,493 traces, zero errors and 26 critical endpoint checks. Modular coverage passes 489/489 references and 54/54 crossings; TSX preflight passes 92/92 dossiers; contracts pass. Native schematic and routed/physical checks remain owed.

Evidence: 06_build/verification/buffer-packaging-adoption and jlc-stock-buffer-composed.json; original supplier capture/owning candidate results remain in /home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/ti-packaging-next. No other TI packaging candidate was adopted.
