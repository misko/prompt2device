review_stage: pre-route
review_kind: topology
reviewer_identity: /root/carrier_topology_fresh
context: FRESH
date: 2026-09-16T23:04:00+00:00
source_commit: 97e8f35d371d3f473766a92e56922b83566bc62c
design_verdict: SOUND
order_verdict: BLOCKED-SOURCING
netlist_sha256: d3e2f0f15ab1c291856d81db26842a88a15944f36135f469934dba9b00d49ebe
parts_sha256: 91e41e19f2994dd82cad30bbfe97f51b13130567117c609a04fa9450d3478b60
design_rules_sha256: fdf0eca26f43bdeb286ffdfe91266de9a8d8362a59005db103db4421a9e2d0bf
schematic_pdf_sha256: 19e772f3a18015e52c558e6ffcff6757e4302863b5c76cb84f829c6154dd0ae0
exact_netlist_sha256: 61ebfafbd7196d43c3cfdb670a8896cb41854b5dcc68c45379f78fddd73b21db
circuit_json_sha256: d524421f517ca6876ded176145cfb48ebbfa43e37f34864c6da5988f33505c36
kicad_schematic_sha256: a83d90aa2d84bd59356f4ed0d99470cbf9cd0e8a0a664c57f872d15591bec9c0

Fresh independent topology verdict: SOUND for the exact current carrier bytes.
This review was performed from the source, normalized native netlist, all 89
part dossiers, adopted rules, current circuit model, native schematic and
rendered schematic. It does not inherit the prior verdict without checking the
new source and generated artifacts.

The material delta assigns supplier catalog identities to six existing SMD
references: F_IN is exact 2920L260/33DR / C22870534; C_HOLD1, C_HOLD2,
C_FILT1_470U and C_FILT2_470U are exact EEEFK1A471P / C178530; and U_ADC is
authored as exact CS5308P-DN with candidate JLC identity C42457798. The TSX
delta changes only those six `jlc` values. Reference, value, manufacturer part
number, footprint, polarity, pad numbering, net assignment, and schematic
coordinates are unchanged. The regenerated netlist differs from the accepted
pre-delta netlist only in the corresponding Supplier Part Numbers fields plus
ordinary export metadata. No net or node line changed.

Independent checks against the exact current netlist passed: 178/178 net labels
survive; 241/241 pin-map assertions hold; 205/205 electrical invariants hold;
7/7 protection/topology ADRs retain executable invariant coverage; and circuit
JSON, native schematic and netlist each contain the same 333/333 manifest
references. The power battery passes 10/10 declared rail checks, 9/9 delivery
margin checks, and the externally powered off-control classification. The
current circuit model contains 333 source, PCB and schematic components, 985
source ports and 1,475 source traces. The six affected references retain their
previous exact MPNs and connections.

The dossier delta preserves the manufacturer electrical, package, land-pattern
and polarity authorities. It changes only sourcing disposition for
2920L260/33DR and CS5308P-DN, and removes the obsolete manual-assembly assertion
from EEEFK1A471P. Assembly policy now excludes exactly 27 unique through-hole
references and none of the six affected SMD references. It requires JLC to
place all 306 fitted top-side SMD references with exact MPNs and no automatic
substitutions. This is coherent with the authored supplier-code delta and does
not alter electrical topology.

Order acceptance remains blocked independently of topology. The public catalog
observation reports C178530 at 668 pieces, C22870534 at 28 pieces, and
C42457798 at zero against the five-board quantity plus configured 150-piece
surplus. C42457798 publicly echoes `CS5308P`, not the full `CS5308P-DN`
orderable suffix. The logged-in JLC uploader must confirm the exact DN device,
allocation, rotation, polarity and exposed-pad process; if exact allocation is
unavailable, exact CS5308P-DN must be consigned for JLC placement. These are
assembly and order gates and do not refute the unchanged electrical topology.

No unresolved topology finding was found within the reviewed state. This
witness grants no placement, routing, fabrication, sourcing, uploader-preview,
first-article or order acceptance.
