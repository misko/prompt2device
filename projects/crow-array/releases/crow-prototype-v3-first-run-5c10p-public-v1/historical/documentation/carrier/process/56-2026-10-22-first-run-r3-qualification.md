# Independent carrier R3 replacement qualification

2026-10-22, FR1. Reviewer: independent SOL reviewer, separate from the SOL
engineering author and Astra source/integration author. Subject: Panasonic
Industry **ERJ-3EKF68R0V**, carrier R3 only, five carriers/ten pods, installed
need **1×5 + 0×10 = 5**. No spare/attrition quantity is authorized or inferred.

**Verdict: PASS for this bounded prototype replacement engineering qualification.**
I recommend adoption of this exact part with unchanged 68-ohm clock damping,
native 0603 copper and placement, and the proposed R3-only larger occupied
model. No demonstrated electrical, contact-overlap or local-body contradiction
remains within the explicitly retained prototype design basis. This is NOT an
architecture, sourcing, schematic, placement/mating, routing, layout,
fabrication, assembly or release admission certificate. It does not make a
successor order-ready or accept an unmodified old Vishay model under a new name.

## Scope, authority and independent work

Read the local PCB skill, complete part-recheck, sourcing/schematic/architecture
contracts, schematic-review and upstream-admission procedures; project contract,
brief/raw decisions and first-run authority; frozen schematic-v1 skill,
sourcing/schematic, imported-tooling and upstream-admission instructions. The
first-run authority controls the new 5/10 build quantity; the architecture still
has eight-pod capacity per carrier. No requirement reduces capacity to two pods.
The old brief's 5/40 is retained history, not the new installed procurement need.

The root project contract explicitly retains schematic-v1 for affected upstream
and schematic receipts. Root/frozen `admission.py` are byte-identical
(`4d1f2f05e4ba06107baea3c0876b149aa5190b7d654263a3cf7176053c79c3fa`), but
their admission instruction hashes differ. Part-recheck instructions are
identical (`340d45af651bef1c035b5ca2bea4998262fb25b2e83a7db3db88b768376ce937`).
Do not run the root instruction fingerprint over old approvals and call them
renewed. The frozen skill's historical unsupported-placement wording is not a
new override of separately adopted downstream adapters; this review executes
none of those adapters and issues no receipt.

I independently reopened manufacturer PDFs and HTML, rendered maker page 4,
opened the exact supplier page, loaded the accepted LS44 carrier read-only with
pcbnew, compared source and native netlist semantics directly, inspected the
candidate carrier PDF and exact native-output clock region, audited the author
calculation code and underlying MNA routines, independently recalculated local
body clearances, and reran finer worst fast/slow model cases. No board was saved,
source modified, vendor contacted or purchase initiated. pcbnew emitted three
inherited property-enum assertions but returned the inspected geometry; this is
not a new DRC result. Inspection images are in
`06_build/recovery/first-run-r3-review/`.

## Reviewed dispositions

| Affected subject | Disposition | Basis |
|---|---|---|
| Exact identity and five-piece design availability | PASS | Exact Panasonic identity, maker facts and opened DigiKey offer; no JLC allocation claim |
| Electrical role, ratings and clock sensitivity | PASS, prototype design basis | Same topology/value; wider R3 sensitivity stays coherent with current LS20/LS44 model |
| Unchanged copper and solder-contact feasibility | PASS, design qualification | Actual roundrect-pad overlap, symmetric lands and retained process/inspection controls |
| Larger occupied body at current LS44 pose | PASS for proposed 1.80×1.00×0.65-mm model | Positive finite separation; old 1.70-mm model is not accepted for Panasonic |
| Candidate source regeneration delta | PASS for inspected candidate | Only R3 maker/MPN semantic delta; all pins/nets/values/footprints and pod preserved |
| Owning stage and successor-release acceptance | OPEN / not performed here | Exact live adoption, dossier/model/population integration and affected-chain admission still required |

### Maker facts and application judgment

The [exact Panasonic model](https://industrial.panasonic.com/ww/products/pt/general-purpose-chip-resistors/models/ERJ3EKF68R0V)
and retained AOA0000C304 (29-May-2025), pages 3–4, establish 68 ohms, ±1%,
0.1 W at 70 C, ±100 ppm/K, 75-V limiting element voltage and −55..155 C
category range. Page 4's drawing/table gives L=1.60±0.15,
W=0.80(+0.15/−0.05), H=0.45±0.10 and bottom termination b=0.30±0.15 mm.
The supplier hyphenated identity links the same Panasonic ERJ3EK family; it is
not an assumed alternate maker or substituted suffix. The retained filtered
maker list includes the exact row, with 571 Active and zero NRFND results;
other series' NRFND annotations must not be applied to ERJ3EK.

R3 remains `X1.3 → MCLK_SRC → 68Ω R3 → MCLK_FAN → 56Ω R4/R5 → U1/U2.15`.
It is not a pod divider or audio resistor. Its lack of a DC shunt, nominal
resistance, initial tolerance, power class, TCR and package technology support
unchanged source damping. At the declared −20..60 C prototype envelope, the
45-K/100-ppm sensitivity plus initial tolerance is about 1.455% high. This is
an engineering application sensitivity, not an extension of a maker test into
a guaranteed complete low-temperature/lifetime specification.

Panasonic's separate 1000-hour endurance allowance is ±2%; solder heat is a
separate ±1% test. Initial×temperature×endurance gives approximately 3.484%,
and adding the separate solder-heat factor gives approximately 4.518%.
Neither product is a guaranteed combined-stress drift or mission lifetime.
The old ±4% Vishay sensitivity does not transfer as a Panasonic life guarantee.
No mission duration was specified by the user, and I neither invent one nor
shorten it to 1000 hours. For the requested unprogrammed prototype build,
retaining the explicit prototype-model posture plus wider sensitivity is a
defensible design qualification; physical waveform/life qualification remains
at its established later boundary, not a precondition to obtaining prototypes.

I audited the author's **v2** 128-fast/48-slow sweep using R3 independently
±6% and R4/R5 independently ±4%. It binds the actual LS44 clock graph and current
7628A spacing sensitivities, not the superseded LS12 thinner-stack hold. Maximum
sampled physical SCKI overshoot is 26.254 mV; finer time/line mesh gives
26.226 mV. Adding the existing SINGLE 100-mV combined residual allowance is
below the 300-mV physical-pin excursion allowance in these cases. Minimum
modeled high/low dwell is 24.803/33.120 ns and sampled skew is at most 0.36622 ns.
My independent finer-point rerun reproduced 26.226048 mV and minimum
24.802948/33.119650 ns. Dwell is not a newly invented TI minimum-pulse rating.
The associated high-load case remains 27.32305 pF against the 30-pF screen.

These are sampled reduced-model sensitivities, not all-space guarantees,
measured edges or a Panasonic parasitic specification. Retain current LS20/LS44
3.0..3.6-V local rails, single combined 100-mV residual allocation, exact
construction/no-substitution controls and rail/clock/startup/capture falsifiers.
The slow model extrapolates the CTS 8-ns/15-pF row; it is not an 8-ns/30-pF
guarantee. Resistor ESL remains an explicit 0.5-nH model allocation. The
ideal-source X1-pad peaks are disclosed model uncertainty, not observed faults.

The independent capacitive-energy screen C×V²×f = 4.777574 mW for
30 pF/3.6 V/12.288 MHz supports the low-average-energy damping application even
if wholly assigned to R3. It is not a repetitive-pulse certification or source
current maximum. RCWV=min(sqrt(0.1×68),75)=2.607681 V for steady DC across
the part. The retained schematic `25V` is a selection class, not permission for
25 V continuous across 68 ohms; no steady clock high creates that voltage drop
into the capacitive receiver. Nanosecond instantaneous power may exceed the
continuous rating without this being a demonstrated continuous-rating fault.

### Unchanged land and finite assembly fit

Independent native read confirms R3=(88.4,80.15) mm, 90 degrees, with pad 1
`/MCLK_SRC`, pad 2 `/MCLK_FAN`, local pad dimensions 0.80×0.95 mm and centers
±0.825 mm. Inner gap=0.85 mm; outer span=2.45 mm. Actual copper is roundrect
with radius 0.20 mm. The library courtyard remains 2.96×1.46 mm.

Panasonic DMM0000COL17's page-1 example gives gap 0.7..0.9, span 2.0..2.2 and
width 0.8..1.0 mm. The extra 0.25-mm span beyond that example is a disclosed
guidance deviation, not an absolute limit. Existing pads still underlie the
minimum bottom terminations and retain symmetric toe/paste geometry. There is
no full-width reserve at the 0.95-mm maximum body width; do not promise side
fillets. Matching a land example is not a reason to edit accepted clock copper
when actual overlap, clearance and solder-process feasibility are supported.

I independently checked the corrected v2 contact argument: with radial
translation ≤0.10 mm and total rigid 3D rotation ≤1 degree, maximum maker-box
point motion is ≤0.119852 mm. A central 0.15×0.25-mm strip of each minimum
bottom termination stays within the pad's actual straight-sided central copper
region, halfwidth 0.475−0.20=0.275 mm. Both axial and lateral conservative
reserves are ≥0.030148 mm. This addresses rounded copper, not merely its
bounding rectangle. Author v1 used a wider strip without the rounded-corner
check and is explicitly superseded; it is not review evidence for contact.

The old 1.70×1.00×0.65-mm occupied model cannot cover new maximum length
1.75 mm. I accept the **proposed R3-only 1.80×1.00×0.65-mm** envelope and
maker-derived nominal contact witnesses ±0.65 mm, with the stated 0.27-mm
registration screen only. That screen does not replace the finite overlap or
actual contact/seating requirements. My independent conservative neighbor-box
calculation using the exact LS44 pose and BOTH parts' radial/3D-rotation margins
finds R5 nearest at ≥0.358136 mm, C28 ≥0.590323 mm and X1 ≥1.543747 mm. Author
v2's complete accepted-scene comparison agrees. No local collision is hidden
by keeping the smaller old model.

Preserve symmetric pads/paste and exact Panasonic process identity. Carry the
maker's maximum two reflows and compatible terminal-temperature/profile limits
into assembly instructions. Existing seating, wetting, no bridge/tombstone,
retention and lot/label traceability obligations remain. All custom mechanical
controls remain conjunctive: general pose caps cannot authorize lost contact,
board penetration, altered Pico pools/reliefs, relaxed finished holes/annuli,
reduced RJ/DC service zones or a changed stack. No process capability or actual
solder result is claimed by this calculation.

### Source/export and sourcing observations

Direct intent comparison against frozen LS13 finds only carrier R3's MPN and
Manufacturer fields changed; pod intent is identical. Direct native XML
comparison finds carrier 142 components/132 nets and pod 34 components/20 nets:
all net memberships and all component keys/values/footprints are identical;
only carrier R3's two ordering fields differ. `drawing.py` and the retained
0603 library are unchanged. The source's R3-specific note is split from R4/R5,
so the remaining Vishay branches are not mislabelled. The exact native-output
PDF clock region visibly preserves source/common/branch paths and values.
Producer receipts report zero ERC violations but retain four inherited ignored
checks; this is not a claim that every KiCad check is enabled. This bounded
delta review does not accept the whole schematic/harness on behalf of its owner.

Before finalizing I also reopened the frozen `first-run-r3-physical2` candidate,
P040 dossier and new `first-run-r3-parity2` results. A direct textual native
comparison against LS44 confirms exactly two changed carrier property strings,
R3 Manufacturer/MPN; every other native byte is identical, and the pod native
is byte-identical. Thus the inspected LS44 geometry is the candidate geometry,
not merely an assumed equivalent. The new parity records execute all-severity
DRC, refill and schematic parity against regenerated successor schematics:
both exit zero, with zero violations, unconnected items and parity findings,
no ignored DRC checks and no changed inputs. These are useful producer checks,
not independent physical-stage admission. The copied native directories also
contain historical DRC files; only the explicitly new parity2 records above
are used as this run's results. The P040 candidate dossier correctly names R3
only, quantity five and the exact retained Panasonic PDF. Its supply/lifecycle
references and engineering caveat are consistent with this scoped judgment.

The retained 14:59:53 UTC JLC exact lookup returned no exact match, not zero
inventory. I independently opened the [exact DigiKey 1746805 page](https://www.digikey.com/en/products/detail/panasonic-industry/ERJ-3EKF68R0V/1746805)
during this review on 2026-10-22: Panasonic ERJ-3EKF68R0V, 0603, **64,642
present stock**, cut-tape quantity-one tier $0.10. One adequate exact offer
satisfies design availability for need five. Stock is unreserved; underlying
update time is unknown. Five installed parts at that tier total $0.50 before
shipping/tax/reeling or supplier process quantities. Full-reel 5000 MOQ is not
the cut-tape MOQ. This does not establish JLC private-library arrival, feeder
minimum/attrition sufficiency, allocation or consignment/process acceptance.

## Open adoption work, not replacement contradictions

1. Integrator must select the reviewed successor source and candidate P040
   dossier/five-piece subject explicitly, and update R3-only BOM,
   population, assembly/model/evidence membership. Preserve P038 and old scenes.
2. Instantiate the proposed larger model and replay registered mechanical
   evidence; carry the exact part's reflow and traceability requirements.
3. Reaccept the affected upstream/schematic and transitive downstream chain
   with owning exact-subject reviews and issue/check. Quantity changes also
   require the complete first-run sourcing/BOM review, not just this R3 offer.
4. Retain original prototype physical/firmware/environmental qualification and
   every custom manufacturing control. No new blanket physical-validation gate
   before an unprogrammed prototype order is imposed here.

There are no open R3 engineering FAIL findings in this bounded qualification.
The integration/admission actions above remain mandatory before a successor
release or order-readiness claim. The historical sealed release is untouched.

## Exact reviewed identities

Project-relative paths below use SHA-256. A changed relevant subject requires
affected re-review; this list is not an admission-schema subject map.

```text
22bdb51e4a45997b133dbedff32737312ee389486d63898a2ed69974649cfeab  01_docs/first-run-authority.md
78825b819853a63f57cc18214f321d2f1da9dc205a7e58af7db18ae73563e378  02_parts/first-run-r3-evidence/AOA0000C304.pdf
fc707b230cce91d464bc3aaf1ed614fa5b412f40cbe7df7cab1541d2c164a882  02_parts/first-run-r3-evidence/DMM0000COL17.pdf
e45fce2af6de6c7145f0fc725e979ccbb69d586e004956b209d9f49d3a99490f  02_parts/first-run-r3-evidence/DMM0000COL14.pdf
0224c881ffd0ab9a01945954c73fb8565d4f8c371ee2504f8e4e30db28880d5b  02_parts/first-run-r3-evidence/ERJ3EKF68R0V-maker.html
7654a791717497e26bda0a07f8e814ba9d4776990911e15a7e82a402cfd0c328  02_parts/first-run-r3-evidence/ERJ3EKF-maker-list.html
75128547241fe624bb309b53383c9ac156e00834450934c41d792f7f74ad789a  02_parts/first-run-r3-evidence/prior-JLC-exact.json
7962958213c453aec970d092abc4039311d4382d653d2033e2544355a7d871ed  02_parts/first-run-r3-evidence/observations.json
8159a20715f35186d8e014dbbd7cf7382c79a43e4d8d9820f4bf7aa3f3747987  03_src/recovery/first-run-r3-source/author.py
c2f1372dbc01f7d18767f2b457e46de922b59f6cb42f9af4d6478ab2963b901d  03_src/recovery/first-run-r3-source/ordering.json
b4be36423511cf39c6e5dfa7046d8520a4c14d09c19d49927ebc28a54b2edd56  03_src/recovery/first-run-r3-source/drawing.py
7a3910f8dc8423047cce821750882c8f76d4ccfcee29d858b6b0509470f8c767  03_src/recovery/first-run-r3-source/crow-carrier-intent.json
f687195ca7b2a2aa2f380c863381b1f48f5930ea8e4854cd398d8768ade965eb  03_src/recovery/first-run-r3-source/crow-pod-intent.json
d40d964423d4a02fe02c0e856e7e64e65e115f4b215f5c78f6f1333b9d32b414  03_src/recovery/first-run-r3-source/crow-carrier.kicad_sch
da2857f3f806582406b4ebac83a1217584508861ce2c6cd26edde3037b879fbe  03_src/recovery/first-run-r3-source/crow-pod.kicad_sch
c52f46828a2d0a4a7265c32af333a7044b7fbfc697599f4acd36168f9744dec3  03_src/recovery/first-run-r3-source/crow-carrier-bom.csv
2bf108d606fc6287126bc083d2d4fb9b39f0f6b2ced50cbec2f3eddf32130650  03_src/recovery/first-run-r3-source/crow-pod-bom.csv
ad781d217e520a2094973d35da4e5b6496f2224fb03ca080aede7012771c382d  03_src/recovery/first-run-r3-engineering/REPORT.md
f2c1ba0a4054418c69233704ca1084e025dd6aa15c44a078e3af1e29749e6fe4  03_src/recovery/first-run-r3-engineering/check.py
269f22118bf5e738176f1b73f0e0adc88ece3fb990b5d90baaaae7473e0cb9c9  03_src/recovery/first-run-r3-engineering/v2-calculations.json
39a3b60246075751e8f5367036e9468e7825009084a2060d445fbf444b8cc4f1  03_src/recovery/first-run-r3-engineering/v2-native-clock-geometry.json
d958a3c69eaea669fa06d74a12db04d092a9a36b67e1a22ee891f1150d500209  03_src/recovery/first-run-r3-engineering/v2-clock-sensitivity.json
644c47d216a546a59f9f900f50d05f5b521c0a1d3468e7519d90dfa4663ea398  03_src/recovery/first-run-r3-engineering/model-proposal.json
56a79ca17f25fd2e8f3eebd07e9ccc617dd69b1ea6fc83b50bb222a2b0016907  06_build/recovery/first-run-r3-native/carrier/native.xml
e4bf549fbb87671295eb5ac2ad7c6c55f59c427bd86ee4d9dd626f48077254b6  06_build/recovery/first-run-r3-native/carrier/native.pdf
dae99a3c024a814be59f6de445e84b47359742aa41bd6880fda2e77478d9e3d4  06_build/recovery/first-run-r3-native/carrier/receipt.json
45542053ada3c533cd4f081df0cdedcd6111658e6943797f3969ac4b7d8f303b  06_build/recovery/first-run-r3-native/pod/native.xml
d4bf5b71ee03e901252027136b146d934b606da20102e11e4747c866e5abae65  06_build/recovery/first-run-r3-native/pod/receipt.json
bbb12bcd67bf42567a30900708d26a1cae0b979d3c319874c4cd82e7b913a0c4  06_build/recovery/ls44-layout/build1/carrier/native/carrier.kicad_pcb
054b35dd7c9e4076db9f92120838f246fd3afd01f2ba7bf278b63f263cc22075  06_build/recovery/ls47-release/archive1/mechanical/scene.json
ae9204cd09811bee62e9c91eb0a3346dea65a6642a9544b4729fc6ad05e066f8  03_src/recovery/ls46-assembly/assembly.json
275e474cd6d9299e2b9791ba002f12e9ab1acba53e0eb7b048b4c6257dc529c4  03_src/recovery/ls43-mating/controls.md
f16eebca233ae0ff599b3f2a0a452f3988d781d8211e94d8f3530b1b41ae8a4f  01_docs/reports/2026-10-08-ls20-engineering.md
46e02ce495e61ab6abcce2167d6afdc698b5bece9bb11c7c87b54f01d864bdff  08_reviews/2026-10-10-ls44-layout.md
0c5a9bb65ada6250964e2670e92a5bc1824ccd7c2e35bbcb7a2f4667d0342414  03_src/adopted/ls13/author.py
0e7e1f502e92cadd2a5fd748f0d53fa79c3d57c0a006961a15c21758b7412754  03_src/adopted/ls13/ordering.json
064504d5472515b0e25018b7f7e9ed251913b244b41137df99f785a22849ce46  06_build/recovery/ls13-source/carrier/native.xml
9367e91002912ef12df6131250d45ec1c943678d70eb41de7254db91ffccc90d  06_build/recovery/ls13-source/pod/native.xml
c54aabf76b20df2aa54ba89f0793ddbd0d1786db0317c6126c015b00c9d12b37  02_parts/P040/part.yaml
78825b819853a63f57cc18214f321d2f1da9dc205a7e58af7db18ae73563e378  02_parts/P040/manufacturer.pdf
788de03787008f20e9d5af57386baa0d0dca12c537f5b0836d4e6d5ed8f407b5  03_src/recovery/first-run-r3-physical2/identity.json
a306cc51bcbf5c874a9c86848df6c35015134dd45ebf91c1ec865895bcecf16e  03_src/recovery/first-run-r3-physical2/carrier/carrier.kicad_pcb
791814ab6baf3ff10da15ebcd2be4e424d2b6682987557886b7763292e89855e  03_src/recovery/first-run-r3-physical2/pod/pod.kicad_pcb
4e24dfbaf27e99719f6d6890c38bcceaf0746741704e891ee2b2c75748304d65  06_build/recovery/first-run-r3-parity2/carrier/parity.json
040e57d43cb6e98dfd65283abd0b16c072cad4ce32b3b59d081cd5c8db49413d  06_build/recovery/first-run-r3-parity2/carrier/drc.json
c22a768f19d9deb60c129c9df655aeb4ce576e443c60dccb06b3edb040ff085f  06_build/recovery/first-run-r3-parity2/pod/parity.json
b2d6402b56a53839a404835ca398d0a93c7583a332c76dbb0ffdde609fa04a4c  06_build/recovery/first-run-r3-parity2/pod/drc.json
```
