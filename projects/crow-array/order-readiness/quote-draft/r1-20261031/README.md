# Crow quote-only upload candidates — revision 1

**For pricing/review only. NOT a manufacturing-approved packet. No purchases.**
User authorized local preparation/validation and Git publication, not a JLC
upload or commitment. Present this manifest for the quote-session permission
described in `../../MACBOOK-QUOTE-HANDOFF.md` before external actions.

## Files and quantities

| Job | Gerbers | Complete JLC-requested BOM | SMT CPL | Portal board/assembly quantity |
|---|---|---|---|---:|
| Carrier | `carrier-gerbers.zip` | `carrier-bom.csv` | `carrier-cpl.csv` | **5** |
| Pod | `pod-gerbers.zip` | `pod-bom.csv` | `pod-cpl.csv` | **10** |

Each BOM/CPL describes **one board**, not the batch or minimum purchase quantity.
Do not multiply the rows or panelize the data. Carrier BOM: 137 installed refs
(127 SMT + ten JLC manual); pod BOM: 29 (28 SMT + one JLC manual).
Full BOMs include the requested THT/manual parts to keep the quote complete;
they intentionally have more references than their SMT-only CPLs.

`carrier-smt-bom.csv` and `pod-smt-bom.csv` are **alternatives**, not additional
BOMs. Use one only if the portal requires a matching SMT-only BOM/CPL pair,
and separately retain/quote every operation in `manual-assembly.csv`. Never
call the resulting SMT-only subtotal a complete assembly quote. If the portal
requires THT coordinates, pause for a reviewed manual-specific format; do not
insert guessed centroids/angles into the SMT CPL. JLC's documentation requests
placement data for SMT and THT, but this package's manual schedule is not a
vendor-approved THT placement file. No successful portal ingestion is claimed.

## Additional scope files — do not upload as a BOM/CPL

- `manual-assembly.csv`: 60 JLC-requested operations across both jobs: 50
  RJHSE-5080, five PJ-102AH and five R-78E5.0-0.5. Includes exact refs, quantities
  and native anchors for locating them, **not** machine centroids or rotations.
- `user-installation.csv`: five SC0915 Picos, ten CMA-4544PF-W microphones and
  ten CPE-203 buzzers; exclude from JLC supply/placement/paste. Protected acoustic
  handling and D1-only Pico instructions still apply. No reassignment of work.
- `scope.csv`: all 177 native references, including eight mechanical mounting
  features. Accounts for 1,000 installed electrical components and makes
  candidate matching/sourcing exceptions explicit.
- `manifest.json`: source and generated-file hashes, quantity/datum conventions
  and outstanding checks. Gerbers and CPLs are byte-identical to the release.
- `native-audit.json`: KiCad 10.0.4 reopened-board checks against all population
  fields, native poses/exclusion flags, retained CPL positions/sides and angles.

## Matching and supply

Exact maker/MPN/footprint/value and installed refs are retained. Proposed public
C-codes are added for regular catalog/replenishment candidates. The two Global
Sourcing parts intentionally have **blank JLCPCB Part #** in the upload BOM:
select exact **PCM1864DBT** and **R-78E5.0-0.5** from the appropriate global/private
offer. Their public locator codes appear only in scope/schedule metadata and
must not be represented as allocated private stock. Do not substitute DBTR.
An unavailable item remains in the job scope; do not mark it DNP to get a price.

Panasonic R3's hyphenated spelling and historical CUI/Same Sky power-jack naming
use the explicit OR7 reconciliation, not generic alias matching. CTS X1 stays
in the SMT scope; its manual catalog label still needs a compatible assembly
route. Portal matching must confirm these candidate choices. No stock refresh,
new part qualification, allocation or fee/attrition approval is implied here.

## Geometry and retained process

CPL uses absolute native datum, millimetres, +X right and +Y up. Negative Y is
intentional. No mirroring, normalization, translation or new panel offset was
applied. Native footprint angle is **not** automatically the vendor placement
angle: 18 carrier and seven pod entries retain explicit angle offsets from the
released CPL. These are listed in the native audit. Check the actual JLC preview
and all relevant pin-1/cathode orientations before any production commitment;
this draft preserves prior mapping, not independently requalifies it against
new catalog selections. All retained SMT centers coincide with native anchors.

Native sources are four-layer, 1.6 mm; retain carrier 7628A and pod 7628 process
requirements from the release. Unchanged ZIPs preserve original plot/drill and
paste bytes. Vendor stencil optimization, rails/fixtures, mechanical limits,
manual handling and exact-job process acceptance remain unresolved. Read the
public release README's holds; do not accept portal defaults as a process waiver.
The discussed prototype Pico-fit risk is already user-accepted; no new redesign.

## Validation and reproduction

From repository root, Python 3.11+:

```sh
python3 -B projects/crow-array/order-readiness/quote_files.py verify
python3 -B -m unittest discover -s projects/crow-array/order-readiness -p 'test_*.py'
python3 -B projects/crow-array/publication.py verify
```

To reproduce into an unused directory, run `quote_files.py build --output PATH`.
It refuses overwrite. `quote_files.py native-audit --output PATH` additionally
requires KiCad 10.0.4's pcbnew Python module and creates a new audit; it never
saves native boards. README is human guidance, not a generated artifact.
Portable verify regenerates expected data in memory and checks the input/output
hashes; it does not rerun pcbnew or manufacture a new independent acceptance.

Checked: 915 SMT placements + 60 JLC manual + 25 user-installed components,
with no manual/user refs in SMT CPL. Tests reject wrong quantity/code/angle,
altered exclusions and stale manifests. Native audit passed; KiCad emitted
nonfatal property-enum/image-handler warnings. No release payload changed.

Format references checked 2026-10-31:
[JLC BOM requirements](https://jlcpcb.com/help/article/bill-of-materials-for-pcb-assembly)
and [JLC placement requirements](https://jlcpcb.com/help/article/pick-place-file-for-pcb-assembly).
CSV headers carry description, designator, footprint, exact identity and quantity;
CPL carries designator, mm position, side and CCW-positive vendor rotation.

Next: after quote-session permission, obtain one itemized 5/10 quote including
both manual schedules, parts/fees, fabrication, setup, assembly, shipping, taxes
and usable-stock timing. Stop at payment/reservation/purchase requirements;
retain partial results as partial. The earlier $227.71 is only the seven-shortage
component estimate, not this packet's complete price.
