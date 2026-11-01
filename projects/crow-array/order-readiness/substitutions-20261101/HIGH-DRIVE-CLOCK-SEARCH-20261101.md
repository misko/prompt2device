# High-drive oscillator substitution review — 2026-11-01

## Follow-up: concrete new supply lead (17:35 UTC)

User requested a deeper search for alternatives that fit, work and have supply.
**TI LMK6CE012288CDLFR / C36974742 is a new, credible redesign candidate.**
It clears the frequency/nominal-voltage/drive/temperature screen and JLC exposes
an orderable overseas-stock pool of 10. It is NOT a drop-in, a fully qualified
replacement, or confirmed immediate factory inventory. Earlier negative search
results below are historical, not a claim that this new candidate is absent.

Completed [live exact-part browser run](https://agent.tinyfish.ai/runs/5efb43d2-8cb1-4679-886d-d8ba2f2a40d8)
on November 1 (176 seconds, 16 steps):

| Candidate | Exact JLC offer | Fit / remaining issue |
| --- | --- | --- |
| **TI LMK6CE012288CDLFR** | [C36974742](https://jlcpcb.com/partdetail/38699451-LMK6CE012288CDLFR/C36974742): browser reports 10, MOQ 1, $4.9424 each; $9.8848 for two installed parts before fees/attrition. Raw public fields identify **overseasStockCount=10, canPresaleNumber=10, isBuyComponent=1**. Do not add these overlapping counts. | 12.288 MHz, LVCMOS, 30 pF below 50 MHz, -40 to +105 C. 2.5 x 2 mm DLF pads replace 7 x 5 mm CTS footprint; no direct fit. Local PCB/power/waveform qualification required. |
| TXC AU-12.288MBE-T | [C2451070](https://jlcpcb.com/partdetail/TXCCorp-AU_12_288MBET/C2451070): browser reports zero/pre-order, MOQ 6, $1.6404 each. DigiKey page lists 5,195 (web response crawl age one month). | 3.2 x 2.5 mm, not drop-in. Manufacturer family sheet says **15 pF or 30 pF** without resolving the exact stocked option; supplier 30 pF field alone is insufficient for admission. |
| CTS CB3LV-3C-12M288000 | [C1851379](https://jlcpcb.com/partdetail/1942192-CB3LV_3C12M288000/C1851379): browser reports zero/pre-order, MOQ 3, $4.0288 each. Previously retained DigiKey offer lists 1,772. | Same-footprint 30 pF candidate, narrower -20 to +70 C rating. Existing prototype review cites -20 to +60 C envelope; confirm it covers actual component ambient before admission. |

The browser's concluding phrase that "all three" have zero stock contradicts
its TI table. Do not use that summary. The raw public exact-identity extraction
resolves TI's ten units as overseas/presale, not factory stock. Neither a usable
warehouse date nor job-specific attrition is established. JLC's exact page lists
SMT assembly, Economic/Standard and MSL1; this is catalog eligibility, not exact-job
placement or process approval. CDLFT was not found; absence is not zero stock.

The retained [structured lookup](LMK6C-STOCK-20261101.json) includes URL, retrieval
time and hashes. jlcsearch returned no exact match, including a separate exact
C-code query; this does not negate the direct JLC offer.

### LMK6C technical screen and bounded next task

[TI exact lifecycle/package page](https://www.ti.com/product/LMK6C/part-details/LMK6CE012288CDLFR)
identifies ACTIVE, DLF four pins, -40 to +105 C, MSL1/260 C.
[TI datasheet rev G](https://www.ti.com/lit/ds/symlink/lmk6c.pdf), sections 6.4,
6.7 and 9.3, establishes:

- 30 pF maximum capacitive load below 50 MHz: passes the retained 27.32305 pF
  load-rating screen with 2.67695 pF margin. This is not a waveform pass.
- Rated operating supply 2.37–3.5 V; 0.1–100 ms ramp. The old model swept to
  3.6 V, so it cannot be transferred. Establish actual rail limits from the
  power source/tolerances and transients; do not silently narrow the old sweep.
- LVCMOS output impedance 40–60 ohm, 45–55% duty. Existing 68/56/56-ohm
  damping needs reanalysis for changed source behavior and native geometry.
- Current tables are substantially higher than the old CTS and specified at
  other frequencies (62 mA maximum at 100 MHz with the stated load). This is
  neither a verified 12.288 MHz maximum nor permission to reuse the CTS budget.
- TI recommends 1 uF local bypass. Check existing bypass and startup interaction;
  update the local source/PCB if necessary.
- Phase-jitter headline is at 100 MHz, not 12.288 MHz. Check the appropriate
  audio clock requirement/frequency evidence rather than claiming the headline
  maximum applies unchanged.

Recommended next engineering subject: qualify this exact TI part and its local
clock block, including power budget/ramp, supply maximum, bypass, pad replacement,
two-ADC timing/overshoot/jitter and affected ERC/DRC/fabrication exports. Preserve
the pod and unrelated carrier design. Separately obtain JLC's usable-stock date;
**overseas inventory does not establish a lead-time saving**. Do not create an r8
quote package until engineering acceptance passes. No purchasing or procurement
flow was entered.

Additional same-body lead: [SiTime SIT8008AI-82-33E-12.288000](https://www.digikey.com/en/products/detail/sitime/SIT8008AI-82-33E-12-288000/11273566)
lists 9,052 **factory** units, MOQ 1, $2.51, NCNR (web response crawl age three
days). Not distributor shelf/JLC stock; no order started. Not qualified: exact
A-family pad/drive/jitter evidence must be checked, not inherited from the newer
SiT8008B family load tables. ECS-7050MV was also screened and excluded under the
[manufacturer's 15 pF limit](https://ecsxtal.com/store/pdf/ECS-7050MV.pdf).

No board, BOM, CPL, Gerber, JLC draft or release acceptance changed in this search.
No purchases, reservations, vendor messages or commitments. Findings local only.

## Decision boundary

User authorized finding a stocked oscillator with enough drive for the existing
clock load, preferring the same footprint, and updating the quote package only
if qualification passes. No purchases. Scope remains 5 fabricated/2 assembled
carriers and 10 fabricated/8 assembled pods. X1 is one per carrier: **2 installed
oscillators**, excluding any supplier-confirmed attrition, spares or MOQ.

No replacement is admitted in this review. r7 remains unchanged. Public stock
and an electrical headline rating are not complete circuit/assembly acceptance.

## Retained circuit boundary

Original: CTS CB3LV-3I-12M288000, 12.288 MHz, 3.3 V, 7 x 5 mm, pin 1 OE,
2 ground, 3 output, 4 supply. Output feeds R3 68 ohm, then two R4/R5 56 ohm
branches to the two PCM1864 SCKI inputs. Existing clock routing/pads were
previously compared against retained geometry; no edits since that comparison.

The retained sensitivity model reaches **27.32305 pF**, including an upper
receiver allocation of 16.80774 pF. These are model allocations, not measured
capacitance or guaranteed TI receiver maxima. A 30 pF driver clears the
capacitive-load screen with 2.67695 pF margin; it does not by itself establish
waveform, timing, jitter, startup or assembly compatibility.

The earlier Taitien OVETDLJANF-12.288MHZ / C5382655 remains rejected for direct
substitution under this model: 15 pF drive rating, plus a changed footprint.

## Screened alternatives

| Exact candidate | Classification | Drive / footprint screen | Availability evidence | Disposition |
| --- | --- | --- | --- | --- |
| CTS CB3LV-3C-12M288000 | Same-footprint candidate | Same CB3LV family and 7 x 5 x 1.8 mm package; 30 pF drive at this frequency. Commercial -20 to +70 C instead of original -40 to +85 C. | DigiKey US exact page retrieved November 1 shows 1,772, cut tape MOQ 1, $1.35/unit; web response identifies crawl age as last month. No confirmed JLC code/ready assembly pool. | Promising technical fallback, NOT adopted. Resolve narrower temperature rating against board component temperatures and exact JLC route. No demonstrated lead-time improvement over sourcing the original. |
| Crystek C3392-12.288 | Rejected for this sourcing pass | Supplier lists 7.2 x 5.2 mm and 0 to +70 C; not an established drop-in. Full manufacturer qualification not pursued after stock failure. | DigiKey exact page says not normally stocked, available to order; 9-week manufacturer lead and 1,000-piece price tier. Response crawl age two months. | Does not meet immediate-stock objective. Do not mistake the 'available to order' label for stock. |
| TI CDC6CE012288ADLYR | Redesign candidate | Manufacturer confirms 30 pF maximum below 50 MHz; 12.288 MHz, 3.3 V supported, active-high OE on pin 1. DLY 1.6 x 1.2 mm requires a new footprint and routing. | DigiKey indexed exact offer shows 3,000 and $1.02 at quantity 1, crawl age last month. Not a fresh JLC allocation or verified warehouse-arrival date. | Clears load-rating screen only. NOT qualified/adopted. Need exact JLC sourcing, changed-layout waveform/timing review, power-ramp and current checks, assembly validation and regenerated outputs. |

### Manufacturer evidence

- [CTS CB3/CB3LV datasheet, rev K](https://www.ctscorp.com/Files/DataSheets/Passives/FCP/Clock-Oscillators/clock-ocillators-CB3_CB3LV-datasheet.pdf): family electrical and mechanical specifications. Do not use Avnet's 50 pF headline in place of the manufacturer 30 pF limit. CB3LV rise/fall specification is at 15 pF; retained CTS analysis was conditional, not a manufacturer 30 pF edge guarantee.
- [TI CDC6C datasheet, rev D](https://www.ti.com/lit/ds/snas843/snas843.pdf): section 6.6 gives 30 pF maximum below 50 MHz and rise/fall specifications through 15 pF; section 6.4 requires a monotonic 0.1–100 ms supply ramp. Normal-mode A suffix, much smaller pads and different driver behavior require reanalysis, not transfer of the CTS acceptance.

### Supplier evidence

- [DigiKey CTS commercial variant](https://www.digikey.com/en/products/detail/cts-frequency-controls/CB3LV-3C-12M288000/280299).
- [DigiKey Crystek](https://www.digikey.com/en/products/detail/crystek-corporation/C3392-12-288/1936791).
- [DigiKey TI candidate](https://www.digikey.com/en/products/detail/texas-instruments/CDC6CE012288ADLYR/27785500).

These observations are indicative and unreserved. Cached/indexed distributor
counts cannot establish immediate JLC assembly availability. Do not combine
public, overseas, presale or account pools.

## Search quality and stopping rule

### Completed live JLC catalog check

[TinyFish read-only run](https://agent.tinyfish.ai/runs/5e29613b-d112-4444-ab71-342566fe2756)
completed on November 1 (10 steps, 316 seconds; requested 180-second bound was
exceeded by the service). It discovered these specific new leads, which justified
a final manufacturer-family drive check beyond the earlier shortlist:

| Exact YXC candidate | JLC code / browser observation | Manufacturer drive screen |
| --- | --- | --- |
| O9705012288MEDA4SI | [C496456](https://jlcpcb.com/partdetail/508162-O9705012288MEDA4SI/C496456), 24 shown, MOQ 1, $1.1155/unit; 7050 | YSO690PR family specifies 15 pF. No evidence of a higher-drive exact option. Not qualified for retained load. |
| O9322512288MEDA4SI | [C496676](https://jlcpcb.com/partdetail/508232-O9322512288MEDA4SI/C496676), 12 shown, MOQ 1, $0.566/unit; 3225 | YSO690PR family specifies 15 pF; also different footprint. Not qualified. |
| OT705012.288MJBA4SL | [C669092](https://jlcpcb.com/partdetail/699192-OT705012288MJBA4SL/C669092), browser reports 1000+ stock, MOQ 1; 7050 | YSO110TR family lists 15 pF or a specified option; no exact 30 pF custom-option evidence. Not qualified. |

Primary references: [YXC YSO690PR](https://yxcxtal.com/product/yso690pr.html)
and [YXC YSO110TR](https://yxcxtal.com/product/yso110tr.html). These reject
admission under published family limits, not a claim that a physical sample
could never oscillate at a greater load. Custom options cannot be assumed.
No new footprint or waveform work is warranted for these failed drive screens.

The browser did not show drive ratings, usable warehouse dates or identify stock
pools sufficiently to establish job allocation. Its `Extended` classification
is not an overseas-stock label. Treat counts as browser observations, not a
complete assembly quote. In particular the reported 1000+ count is not separately
confirmed against a full-reel quantity. Exact C496456 jlcsearch recovery returned
the right MPN but `stock:null`; that does not negate the browser count or prove
zero stock. No inference that the catalog search was exhaustive is made.

The public jlcsearch MPN/broad-frequency queries returned unrelated components
in this pass. Those results do not establish zero stock. Exact C-code lookup
worked for the previously reviewed Taitien, but that candidate fails drive.
Do not keep repeating equivalent searches or create speculative MPNs from
configurable-family ordering codes. Microchip VCC1/VCC4 50 pF family options
were discovery leads only: no exact stocked 12.288 MHz offer was established.

## Next action ranking

1. Preserve the original CTS and resolve its exact JLC assembly eligibility /
   consignment route. It already has retained circuit qualification and an
   earlier distributor-stock lead. The earlier disabled-Add assembly tooltip
   means sourcing stock alone is insufficient. The user's non-binding inquiry
   authorization exists; the historical request for permission is superseded,
   but no message was sent in this substitution review.
2. If that route is unavailable, establish a usable JLC offer for the TI part
   before doing the local clock redesign. Alternatively, the commercial CTS
   could avoid layout work if its temperature envelope and JLC route pass.

Do not silently move X1 to home installation, omit it, relax the load model,
or label a BOM-only replacement production-ready. Other open manufacturing
and placement holds remain independent of this component search.

## Verification

`python3 projects/crow-array/order-readiness/r7_quote.py verify`:
**PASS, 97 files, production_ready=false** on November 1. No r8 created,
no CAD/BOM/CPL/Gerber changes, no JLC draft changes, purchases, reservations,
vendor messages or manufacturing commitments. This report is local, not pushed.
