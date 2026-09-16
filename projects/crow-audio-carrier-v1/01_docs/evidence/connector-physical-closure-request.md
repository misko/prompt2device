# Carrier connector closure: document facts and physical request

Updated: 2026-09-07
State: `DO-NOT-ORDER`; this is a request for missing evidence, not a test result.

The unchanged canonical connector compiler currently reports 22/42 evidence
items known and 20 explicitly unknown across 3 assemblies / 11 operated
connector instances. Base receipt:
`06_build/verification/connector_assembly_contract.json`, SHA-256
`f8d941dda0d73bb9e41862c9b9e76b9eda430f0b51b73c96eac114e0e173f7c2`.
The additive source receipt is
`06_build/verification/connector_assembly_source_gate.json`, SHA-256
`f44dbb3f23bcebd327e9f22eb72f5688c8c6c2466c5d89b83e3d70a393837c23`.
It passes while admitting all 20 unknowns only as stable-ID physical
qualification work. The full-phase receipt remains `INCOMPLETE` with exactly
those 20 findings; its SHA-256 is
`6b0e587eb3d5bedc6d32d769ef02e89039e4929ab1ef13fa2e5bb73a73d31714`.
Neither wrapper relabels the base receipt.

Under user-accepted ADR-0007, SOURCE plus independent geometry/electrical/review
gates can admit this unqualified prototype's layout. FULL still requires base
`PASS` and zero unknowns for physical qualification, but it no longer blocks
the prototype needed to make those measurements. A connector coupon is optional;
the first assembled carrier may supply the same evidence. Neither route
changes the qualification bar or authorizes a purchase.

The current regenerated carrier placement is
`04_kicad/crow_audio_carrier_v1.kicad_pcb`, SHA-256
`0f6e2e608e72c986e2fc5d559e63df4ed23de8728e6428698eb3eba9ad7d15d1`.
Its south-bank pad-1 anchors compensate the exact 43650-0400 right-angle
footprint's 9.0 mm body-center offset, so J5-J8 align laterally with J1-J4 and
the former J5/H3/FID3 courtyard and NPTH conflicts are absent. Any coupon must
derive from these exact corrected bytes and geometry, not the superseded
placement.

## Governed coupon prepared

The exact physical-test handoff is now
`06_build/connector_qualification_coupon/current/`. The source-bound generator
copied J1-J11, H1-H4, FID1-FID3 and the complete 150 x 100 mm outline into a
non-functional four-layer, 1.600 mm connector-only coupon, cleared all pad nets,
and proved normalized source/coupon footprint, pad, courtyard, model, outline
and pairwise-anchor geometry equal. It is a bare-board fabrication request for
hand population of exact connector lots, not a carrier PCB, PCBA request,
release, or product order.

Current exact bindings:

- coupon board SHA-256: `93e01e71556659112f3c40c45328cdc266b235d5d394ff1247485a61f45f71a2`;
- normalized source/coupon geometry SHA-256:
  `ea83a5c7e0b5fab54323b6984c0dff13e1e3963e5f39084b8dc116d254523d24`;
- fabrication ZIP SHA-256:
  `82dbfeaad54f07ac89207ab437aa15a6480da575c29e761692fe9e6956200d20`;
- typed request SHA-256:
  `c840f3cc2d6025fae9f4a7069954d180a782cf5926ec41bced3fdb0b28d4f10d`;
- blank response SHA-256:
  `53fd0cd5885c34ff8d11e7f34d57beda380537e2ca7f33c6351b44d616c462f9`;
- current regraded receipt SHA-256:
  `21ccbe6bfe1c4646145a8d07c94c51e740b5687e800f7e4db95e9778a1fdb49f`.

Coupon DRC is zero errors, zero mechanical findings and zero unconnected items;
its four warnings are only accepted connector-silkscreen clipping at the board
edge. The request covers all 3 assemblies, 11 operated connector refs, 7 board
datums and all 20 source-phase physical targets. The deliberately blank
response regrades `INCOMPLETE` with 0/20 observed targets, 0/11 samples and 25
findings. If this optional coupon is chosen, revalidate its bindings against
the current candidate, fabricate/populate and measure it, then fill the
response rather than editing the receipt. It is not an action the user must
perform before carrier design can continue.

The public manufacturer option screen in
`jlcpcb-connector-coupon-public-capability-record.md` finds the coupon's exact
4-layer FR-4, 150 x 100 mm, 1.600 mm, green/white and lead-free-HASL choices
compatible with JLCPCB's published rigid-PCB capabilities. No file was
uploaded, so that record is not CAM acceptance, a quote, an authenticated
allocation, or order authority and closes none of the physical observations.

## A. Facts closed by documents

| Assembly fact | Ordinary project record and SHA-256 | What it closes |
|---|---|---|
| J1-J8 header | `02_parts/43650-0400/primary-source-record.md` — `5e889afa96fcca7b77c42a8490e00da8ed9d7ebffd21975d46b02c87228cac2d` | Exact 43650-0400 identity; 3.00 mm pitch; 1.02 mm holes; four-position dimensions; locator relationships; 43645 mating family; 17.56 mm mated length; drawing tolerances. |
| J1-J8 cable housing | `02_parts/43645-0400/primary-source-record.md` — `efad1929ec14d6a0d58be8bb477bd415737a8af860a0d873d6899777e592795f` | Exact 43645-0400 housing, 43030 contact family, keyed positive latch, 14.00 x 12.85 x 8.28 mm planning body and mating-face numbering obligation. |
| Micro-Fit contact/process | `02_parts/43030-0007/primary-source-record.md` — `3beb43044f7ea1a7f997e414c58ea3523a20786905e45eb4082dc274649b44f2` | Exact 43030-0007; 20/22/24 AWG; 1.85 mm maximum insulation; 2.54-2.92 mm strip; 22 AWG crimp/pull numbers; hand and extraction tool identities. |
| Spoke cable | `02_parts/6541PA/primary-source-record.md` — `34a2219e32c9356f30355b73567023b7c242603d24cdb4251e341fbef688cf9c` | Exact Belden 6541PA; two shielded 22 AWG pairs; 1.2 mm conductor insulation; 5.44 mm OD; 53 mm bend radius; electrical/temperature facts. |
| J10/J11 carrier header | `02_parts/TMM-106-01-L-D/primary-source-record.md` — `f1a49081c9141e86c88b81f7e729c0a1f31e4a1ea00464cc38b8daba38225d13` | Exact TMM-106-01-L-D order code, 2x6 numbering, 2.00 mm pitch, 0.50 mm square posts, body/post envelope, unshrouded friction interface. |
| J10/J11 selected cable | `02_parts/TCSD-06-D-04.50-01/primary-source-record.md` — `8559057eab2852914ae62bd3b1111fa8d8f5f21c99bf8dc11f82479e477682c5` | Exact double-ended 2x6 socket assembly, 114.30 +/-3.175 mm length, base-socket envelope, 28 AWG construction, first-position indicator, TMM family compatibility. |
| MCH electrical/pin interface | `01_docs/evidence/mchstreamer-user-manual-record.md` — `fe4435e945b2536bdcac2864663c7f8d55a3ecd412fa85e2e58b46fa5ac189c8` | J1/J3 numbering and used pins, 3.3 V logic, J3 supply rating, clock-master behavior, TDM8 pinout/rates and 24-bit input treatment. It explicitly records that miniDSP publishes no board-header MPN. |

These records also close that all three interfaces are non-threaded, need no
installed service tool, and have no torque operation. For J1-J8 harness
manufacture, the exact tools are Molex `63819-0000` (`ATS-638190000`) and, only
for rework, Molex `11-03-0043` (`HT60923A`). J9 instead uses factory-precrimped
leads and authorizes no field crimp operation. None of these document facts
proves a built J1-J8 crimp, installed seating, enclosure access, or simultaneous
service.

## B. Minimum physical evidence still required

Supply original-resolution JPEG/PNG files (not screenshots of thumbnails) and
a CSV or Markdown measurement sheet. Every image must include a visible sample
ID/date card; dimensional images must include a ruler or scale in the same
plane. Record instrument maker/model/serial, resolution, and calibration date.

### J1-J8 spoke bank

Required samples: one carrier connector-bank coupon or first PCB populated with
all eight exact 43650-0400 headers, plus eight complete harness ends built from
43645-0400, 43030-0007 and 6541PA.

1. Provide orthogonal top and edge photos of the north and south banks with all
   eight cables simultaneously latched, plus mating-face and wire-side macro
   photos showing cavity 1 and every wire color.
2. Measure each header's mouth position relative to the PCB edge, housing
   seating height, nearest-neighbor body gap, minimum latch/finger clearance,
   first unobstructed straight cable run, achieved bend radius, and minimum
   cable-to-enclosure clearance. Record all eight values, not only the best one.
3. Provide one continuous photo sequence or short video showing mate,
   latch/tug-check, continuity check and unmate for the worst-access J1-J8
   position while the other seven remain populated. Support the PCB/enclosure;
   do not react the load through cable conductors or solder joints alone.
4. For the 22 AWG setup samples record strip length (required documented range
   2.54-2.92 mm), conductor crimp height (0.83-0.93 mm), reference insulation
   crimp height/width (1.58/1.72 mm), and destructive pull force (minimum
   documented value 35.6 N). Include crimp cross-section/macros showing
   bellmouth, brush and insulation support.
5. Photograph the `63819-0000` tool marking and its `ATS-638190000` identity.
   If any contact is removed, also photograph `11-03-0043` / `HT60923A`; reject
   the removed contact. Identify the crimp-height micrometer and calibrated pull
   tester used.
6. Supply a signed cavity-to-cavity result for every harness: 1-1, 2-2, 3-3,
   4-4 and no cross-short. Also record carrier polarity: pin 1 `+12V_PODn`, pin
   2 GND, pin 3 `AUDIO_Pn`, pin 4 `AUDIO_Nn`.

### J9 isolated 12 V input

The cable-side design is selected: exact 43645-0200 housing, factory-precrimped
150 mm red 214761-2122 and black 214761-1122 18 AWG leads with 43030-0038
contacts, and internal screw-mount restraint 113-00022 after a 12.70 mm free
run. Supply those exact samples and identify the downstream appliance-side
pigtail termination. Record the installed two-lead cross-section, achieved bend
radius, restraint screw/hardware, conductor temperature exposure and final
route; the public part records do not qualify those installed facts.

Provide mating-face/wire-side/pin-1 photos and bag/lot labels establishing the
two exact factory-precrimped lead identities. Show both contacts fully seated
without splice or recrimp, and continuity-prove pin 1 `+12V_IN` and pin 2 GND.
With J1-J8 populated, measure J9 mouth-to-edge position, installed housing
envelope, finger/latch clearance, straight run, bend radius, enclosure/strain-
relief clearance and supported mate/unmate reaction. Supply one supply-off
mate/polarity-check/unmate video. Do not hot-plug.

### J10/J11 to MCHStreamer J1/J3

Required samples: the exact intended MCHStreamer Kit/Lite hardware revision,
two bag-labeled `TCSD-06-D-04.50-01` assemblies, and a carrier coupon/first PCB
with J10/J11 exact TMM-106-01-L-D headers.

1. Photograph the module revision/serial, top side of MCH J1/J3 with the manual
   pin-1 orientation visible, both TCSD first-position indicators, and both
   carrier headers. Provide top/side photos with both cables simultaneously
   seated and labels visible: `J10 <-> MCH J1 TDM` and
   `J11 <-> MCH J3 SENSE`.
2. Measure MCH J1 and J3 row/column pitch, post width in both axes, exposed post
   contact length, and any shroud/obstruction. The manual's 2x6/2.00 mm statement
   is insufficient: compare the sample directly with the 0.50 mm-square TMM/
   TCSD mating system and photograph a fully seated socket on each module header.
3. Before connecting boards, record end-to-end resistance for pins 1-12 of each
   cable and the off-diagonal no-short check. The reviewed drawing indicates the
   base straight configuration, but this project will not infer 1-1 wiring from
   suffix absence or socket appearance.
4. Measure socket seated gap/insertion depth, minimum clearance between both
   populated carrier sockets, total cable height above each PCB, installed
   straight run, smallest bend radius and enclosure clearance. Samtec publishes
   no minimum bend radius for this configured ribbon assembly; obtain a Samtec
   application limit or provide a documented flex/retention qualification before
   the cable section can be closed.
5. Provide one continuous sequence showing J10 mate, J11 mate, pin-1/label
   inspection, J11 unmate and J10 unmate, always supporting both boards and
   leaving the neighbor in the required populated state.

After these files exist, bind them as ordinary project evidence, rerun the base
compiler plus `--phase full`, and review both receipts. First fill
`06_build/connector_qualification_coupon/current/physical-response.yaml` and
run the grade command in `request.json`; only a fresh 20/20 `PASS` receipt may
be cited by the base contract. A complete photo set is still not an electrical
back-power or TDM performance pass; the four-state current and logic-analyzer
tests in ADR-0005/`first_article.yaml` remain independent.
