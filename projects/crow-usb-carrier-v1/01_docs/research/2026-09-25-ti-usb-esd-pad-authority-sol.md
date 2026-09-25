# TI USB ESD pad-shape authority trace, 2026-09-25

**Disposition: research rebaseline only.** No canonical footprint, dossier,
TSX, netlist, PCB, or D13 decision was changed for this audit. It does not
accept a board, ESD coordination, P1, or an order. A shape-sensitive placement
study should use a fresh board generated from the governed TI source and
record that native copper uses rounded rectangles. The retained TI primary
does not itself require replacing the existing KiCad footprint with square
corners; any choice to change footprint or source identity requires the
independent D13 exact-part review before promotion.

## Source and primary authority

- Governed `03_tscircuit/src/usb_device_frontend.tsx` (SHA-256
  `62611f919a9e41d3a13a7f9df91e000761026f6d55719d1c3bccb8623980f477`)
  selects `U_USB_ESD = TPD2EUSB30ADRTR / C94934`, with TSX `rect` pads 1/2/3
  of 0.30 × 0.30 mm at local `(-0.35,+0.425)`, `(+0.35,+0.425)`,
  `(0,-0.425)` mm. This is a schematic-source footprint declaration; the
  project's `tsci build --disable-pcb` does not emit KiCad copper pads.
- `02_parts/TPD2EUSB30ADRTR/part.yaml` binds FPID
  `Package_TO_SOT_SMD:Texas_DRT-3`, pin 1 = DP, 2 = DM, 3 = GND. Retained TI
  primary `SLVSAC2G.pdf` SHA-256
  `a2c0dd845043a5bbfe610f673879c29e38649544385dea51dbe0a4c49df39136`
  has a DRT land-pattern drawing on PDF page 27: three 0.30 × 0.30 mm lands,
  0.70 mm data-pad center spacing, 0.85 mm between pad rows. It draws square
  corners but supplies no corner-radius dimension, tolerance, or explicit
  instruction that the copper corners must be square. Square corners alone
  are therefore a drawing convention, not a demonstrated manufacturer
  acceptance condition for these otherwise matching lands.
- Installed KiCad `Texas_DRT-3.kicad_mod` SHA-256
  `15cde3ee13da0e0426038a0a17ee16c50edc6d100b64582166b4263d4e7cae17`
  has the same three pad centers and 0.30 × 0.30 mm extents, using
  `roundrect` with radius ratio 0.25 (0.075 mm corner radius). This changes
  the copper at corners while preserving the dimensional envelope.

## Fresh isolated native witness

An isolated copy of the current governed TSX was built with the pinned
node modules, then converted with current `02_parts`, 18 explicit net aliases,
KiCad native netlist export, the generic board generator, rule generator,
and the eight-site TMUX POFV generator. Nothing was copied into canonical
generated paths. The isolated circuit, netlist, and final board SHA-256 are
respectively `580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
`6b989727eab0b2fbdadd5d8a26f5a2f175e0380d6273e86b9b9ee4693741d1c4`,
and `a3ffbcb46588fa35152718ffeb8eb90c05aee9cb1b2fadaefa248c14e2ee5bad`.
The netlist has 569 components, 1,787 pad/net tuples, and 428 nets. It names
`U_USB_ESD` as TI `TPD2EUSB30ADRTR` with the DRT FPID and exact
1=`USB_DP`, 2=`USB_DN`, 3=`GND` map. The native board places it at
`(217,36,0°)` mm and has:

| Pad | Net | Native center (mm) | Copper |
| --- | --- | --- | --- |
| 1 | `USB_DP` | `(216.65,36.425)` | 0.30 × 0.30 mm roundrect, ratio 0.25 |
| 2 | `USB_DN` | `(217.35,36.425)` | 0.30 × 0.30 mm roundrect, ratio 0.25 |
| 3 | `GND` | `(217,35.575)` | 0.30 × 0.30 mm roundrect, ratio 0.25 |

`P-PINMAP` passes 79 multi-pin refs and 799 physical identities, and
`S-COUNT` matches 569 references across the fresh circuit, schematic,
netlist, and board. Neither result proves this three-pin pad *shape*:
`P-PINMAP` skips dossiers with three or fewer pins and checks numbered pin
identity rather than copper geometry. The isolated project omitted the
manifest, so its `S-COUNT` result is only the three generated-artifact pairs.

The frozen TI diagnostic source packet binds circuit SHA-256
`580ac31b0de8d376d888caa1a342ae43c0636fbd13c74048392173acf718cb6d`,
floorplan SHA-256
`0032b1202f5742b6575198d27ea50629826d49cf81cf12a31fead8a2929d9868`,
netlist SHA-256
`a40b45c27b2169ed4f3dd43d72a1f4f7112d829985f98918a8855ed76735e9bd`,
and board SHA-256
`8e620def0b403fda7635135672afec923c2c23bc9844b3f96102e96d4d5eca10`.
Its circuit bytes equal this isolated fresh circuit; its native netlist has
the same 569 component (FPID,value) tuples, 1,787 pad/net tuples, and 428
net names, despite different export bytes. Its native `U_USB_ESD` has the
same TI identity, pose, pad centers, nets, dimensions, and roundrect ratio.
Between its board and this newly generated board, all 569 reference sets,
FPID/value tuples, and pad number/net/shape/size signatures match; only
`Q_PRE` has a different footprint pose. The frozen floorplan has
`Q_PRE=(46,106.85,0°)` and the current floorplan SHA-256
`c2a6562c1a012e692109b852158af2ef73a432f712a62ae87cbd8e49c4c4ecd6`
has `Q_PRE=(46,107.15,0°)`. Both boards have nine areas after the TMUX
conditional rule generator. This is a source-parity comparison, not DRC or
route acceptance.

At audit time the shared canonical netlist SHA-256
`457763489019b299491c38d303b618561b45be2dc43e6298fe89b25effd8e0cd`
still named `U_USB_ESD = PESD2USB5UX-TR` with Nexperia FPID. That artifact
cannot be used as authority for the governed TI source or a shape-sensitive
TI placement promotion. The minimal next action is a fresh, explicitly
hash-bound TI native **research** rebaseline. This audit does not reopen D13;
the existing prototype-only boundary remains. If a later independent D13
review demands literal rectangular copper, create a
project-local TI DRT footprint changing only the three pad shapes, then
update the dossier FPID, TSX/native shape contract, IC applicability binding,
and dependent reviews before promoting any board. There is no basis here
for a silent generator or global KiCad library change.
