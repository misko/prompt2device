# Independent r6 working-package integration review

Verdict: **PASS for the bounded local quote/working-source derivative. No blocking integration defects found.** This does not admit a new sealed release, accept factory placement/process, reserve inventory or authorize an order. Reviewed read-only on 2026-11-01 UTC / 2026-10-31 PDT; no repository files changed by this reviewer.

Subject: `/home/mouse9911/gits/circuits-crow-stock-substitutions-20261101/projects/crow-array/order-readiness/quote-draft/r6-2c8p-substitutions`.

Final reviewed package manifest SHA256: `c01cb5e90b31738b6afd0102aca1b22ae3322c1e82f17fbe5492c8f198f19099`.

I read the actual handoff, adopted-change map, independent capacitor and ADC review scopes, generated tables, manifest, generator and tests. I compared actual outputs against r5 and the frozen release rather than accepting manifest assertions alone. This is integration review of the four locally qualified identities, not a fresh independent requalification of the capacitors or whole board.

## Replayed and independently checked

- `python3 projects/crow-array/order-readiness/substitute_quote.py verify projects/crow-array/order-readiness/substitutions-20261101/adopted-changes.json projects/crow-array/order-readiness/quote-draft/r6-2c8p-substitutions`: **PASS**. This checks hash-bound r5/release/evidence inputs and deterministic replay of all package files.
- Nine generator unit tests: **PASS**, rerun against the final rebuilt package. Tests include property-only rewriting, maker/reference mismatch rejection, escaped strings, library plus instance fields, unchanged footprint/quantity fields, and real-package replay/tamper detection.
- Independently expanded BOM designators: carrier30 rows/137 placed references =127 SMT +10 THT per board; pod21 rows/29 placed references =28 SMT +1 THT. No duplicate BOM references; every row quantity equals its designator count. Each BOM reference set exactly equals its paired CPL reference set. Scope and current exported netlist identities/footprints reconcile to those BOMs.
- Current build arithmetic: `127×2 +28×8 =478` SMT; `10×2 +1×8 =28` factory THT; `1×2 +2×8 =18` home parts. Total524 installed. The38-row procurement plan independently reconciles manufacturer/MPN, individual references, per-board counts and every `2×per_carrier +8×per_pod` installed total. Mechanical-only references have zero installed-parts demand. BOM/CPL files remain per-one-board; fabrication stays5carriers/10pods while assembly is2carriers/8pods.
- The four replacement totals are correct: PCM1864DBTR4, CL21B105KBFNNNE12, CL21B225KBYVPNE8 and CL31B106KBHNNNE4. Correct exact codes C544855/C28323/C5362585/C89632 occur in the intended BOM rows. No scope shift hides a shortage.

## Native and fabrication boundary

Independent line-aligned and property-value-masked byte comparisons against the frozen release found **only MPN/Manufacturer/Value property changes** in six owning native files. Carrier changes affect only C1/C2/C11/C21/U1/U2; pod only C1/C3. Changed-property line counts: carrierPCB16, schematic32, library16; podPCB6, schematic12, library6. The double schematic counts are embedded library plus actual instance fields. All other native source bytes, including nets, pin definitions, footprint identifiers, coordinates, copper and zones, remain identical. Generator replay separately verifies the exact intended metadata strings.

Carrier/pod before-versus-after exported net membership is identical:132 and20 nets respectively, including node pin/function/type attributes. No new electrical or firmware interface is implied. The frozen release's manifest-listed files all pass their original publication hashes through replay; r5's manifest-listed files also pass. The final generator additionally checks the exact frozen-release file census, preventing unlisted runtime artifacts from being copied. The coordinator moved the two KiCad-generated `.kicad_prl` preference files into `substitutions-20261101/validation/tool-side-effects`; I independently confirmed the final native package contains no `.kicad_prl` files. No sealed manufacturing artifact or acceptance receipt changed.

Independently compared r6 versus r5 byte-for-byte: both GerberZIPs, both CPLs, home-install table, JLC-THT table and THT-placement-verification table are unchanged. Existing native-versus-CPL rotation conventions are intentionally retained. No assumption of JLC library rotation equivalence is made; actual preview pin1 remains open.

## Validation scope and remaining holds

Inspected saved current validation JSON: carrier and pod ERC contain zero violations with **four ignored check classes each**; both DRC reports contain zero violations and zero unconnected items, with no ignored checks. Final `validation/native-validation.json` reports PASS and binds the final manifest above; I independently verified all14 bound source/XML/ERC/DRC/PDF input hashes against actual files. This is properly scoped as KiCad checks for the derivative, not proof of every possible electrical rule, measured performance, manufacturing process or renewed historical acceptance. I did not rerun ERC/DRC or edit PCB sources; current exported identity/net parity and metadata-only comparison support use of the saved reports for this bounded review.

The three retained exact identities are intact everywhere: Littelfuse1206L010/30WR need24, CTS CB3LV-3I-12M288000 need2, RECOM R-78E5.0-0.5 need2. Their procurement rows now carry correct exact distributor URLs and Global-Sourcing/consignment-candidate routes; installed quantities remain separate from blank purchase quantities. Fuse/clock public catalog locators are retained in the plan while BOM code cells are blank for private-source matching. Blank code is not DNP, and all references remain placed. No YLPTEC regulator,5Vclock or60VPTC has entered the package.

Handoff and README explicitly retain factory allocation/eligibility, gross demand/attrition, fees/date, process, full-preview/pin1, capacitor paste/joint/part mapping, ENIG/stackup, outline/rails/depanel/mechanical, and automatic-confirmation holds. They retain no-purchase/no-reservation/no-vendor-contact/no-production-approval instructions. The historic exact-RECOM two-for$9.69 lead is identified as unrefreshed and not allocation. Public stock and supplier/lifecycle conflicts are not promoted to factory guarantees.

Manifest flags are all false: production_ready, purchase_authorized, submitted, vendor_preview_approved and inherited_release_acceptance. Consequently the derivative does not silently promote inherited receipts. Next safe step is the handoff's read-only exact-job matching/quote information review; stop if the portal requires acquisition, reservation or a noncancelable workflow. No redesign or whole-board restart is indicated by this integration pass.
