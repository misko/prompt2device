review_stage: pre-route
review_kind: topology
reviewer_identity: /root/carrier_topology_refresh
context: FRESH
date: 2026-09-16T23:43:08Z
source_commit: 60ad41827f29fa7327241b12f521617e6fc7d518
design_verdict: SOUND
order_verdict: FIRST-ARTICLE-ONLY
netlist_sha256: d3e2f0f15ab1c291856d81db26842a88a15944f36135f469934dba9b00d49ebe
parts_sha256: 19914c21c35cc6593b6dcc88a26f5b094517c09c3834356f6fc252048ce3b916
design_rules_sha256: 790b9c21efc3a61c742237939eaa94759f3cbb4658e8c418a69781eb1f0d5417
schematic_pdf_sha256: abc0a7a5d4e12c2d0dd3d65adf36291a6a2465ce50520f63084e462e345dbf18
exact_netlist_sha256: 124e8c4f889c44752fd5c7343f9e708556fb56066e6e2a299e937b074afea616
circuit_json_sha256: cffbcd410f2cfe085d990bf4b8ccc31aa5a2cb280f9b11a873376eb3d501bddf
kicad_schematic_sha256: 3160cc4afdd2855c1d8198419e98efeb5c9b0db70d716735b535270078d9096f
promoted_kicad_schematic_sha256: a83d90aa2d84bd59356f4ed0d99470cbf9cd0e8a0a664c57f872d15591bec9c0

2026-09-16 final sourcing rebind: the semantic rules digest changed only by
adding exact dated public-stock plans for F_IN/C22870534 and
U_ADC/C42457798. Electrical topology, schematic, netlist, geometry, assembly
population and every safety floor remain unchanged. Exact public observations
now clear the configured surplus; live uploader identity, rotations and
allocation remain supervised first-article order controls.

Fresh independent topology verdict: SOUND for the exact current carrier
schematic subject. I reviewed the authoritative source delta, all current part
dossiers and adopted rules, the regenerated circuit model, native schematic,
normalized and raw exported netlist, current schematic checkpoint, and the
manufacturer evidence changed in this revision. I did not inherit the earlier
acceptance as the basis for this verdict.

The current design has nonzero and complete measured coverage. The circuit
model contains 333 source components, 985 source ports and 1,475 source traces.
The manifest, circuit model, native KiCad schematic and exported netlist agree
on 333/333 references. The netlist contains 221 nets; 178/178 authored labels
survive and 241/241 physical pin-map assertions hold. The executable design
battery passes 205/205 electrical invariants, 7/7 protection/topology ADR
coverage, 10/10 declared rail-topology checks and 9/9 loaded-delivery margin
checks. The analog checks independently cover eight same-leg channels, 32
independent shunts, two passive VMID dividers and two direct FILT returns. The
clock/default-state screen passes all nine top-level checks and all seven TDM
subchecks. The source-level analog protection model covers 333 components, 985
pins, eight amplifiers, eight channels and sixteen pulldowns. The board is
externally powered, so unplugging the input is the applicable de-energization
mechanism; no stored battery source is present.

The revision changes manufacturing population geometry and evidence, not the
electrical circuit. `floorplan.yaml` removes `exclude_from_pos_files` from
U_ADC, F_IN, C_FILT1_470U, C_FILT2_470U, C_HOLD1 and C_HOLD2. Those attributes
control CPL emission and do not change schematic pins, values or nets. The
remaining position-exclusion set is exactly the 27 references declared for
manual through-hole assembly: eleven connectors and sixteen film capacitors.
All six corrected references remain top-side fitted SMDs required for JLC
placement. The normalized netlist digest is unchanged from the preceding
electrical subject; the new raw netlist bytes differ through ordinary export
date and instance UUID regeneration. I nevertheless re-ran the complete
electrical checks above and inspected the affected nodes directly.

The six affected references retain coherent exact identities and topology.
U_ADC is CS5308P-DN in the exact QFN-48 footprint with supplier candidate
C42457798. F_IN is 2920L260/33DR in the 2920 footprint with C22870534 and still
bridges J9/12V_IN to 12V_FUSED ahead of Q_IN. Each of C_FILT1_470U and
C_FILT2_470U is exact EEEFK1A471P / C178530: pad 1 remains on FILT1P or FILT2P
beside U_ADC pins 43 or 18, while pad 2 remains directly on GND. C_HOLD1 and
C_HOLD2 use the same exact polarized part with pad 1 on 5V_LDO_HOLD and pad 2
on GND. No polarity, value, MPN, footprint, pin number, node membership or
functional series/shunt relationship changed.

The new capacitor dossier and PAD-GEOM adjudication are electrically and
physically coherent. The retained official Panasonic FK PDF has SHA-256
`b36857d089adaddf3042b33bf11d0f7d83bf70734e983f33b7827152e11854e3`.
Its exact EEEFK1A471P row specifies the standard-P, 10 V, 470 uF, size-F part,
and its standard-product land table specifies a=3.1 mm inner gap, b=4.0 mm pad
length and c=2.0 mm pad width. This yields the 7.10 mm pad-center pitch used by
the native footprint, whose SHA-256 is
`63fc06c20177564eb58d1befaf432e427c2cfdb49565a7e8cb1c983a66845294` and
whose pads are exactly at +/-3.55 mm with 4.0 x 2.0 mm lands. The adjudication
is narrowly scoped to the generic supplier PAD-GEOM discrepancy and retains
exact-MPN, CPL, rotation, polarity, model and uploader checks. It does not
waive an electrical or assembly identity requirement.

Order acceptance remains blocked separately from design soundness. The latest
public catalog receipt grades 54/54 coded placement lines against the five-board
quantity plus the configured 150-unit surplus and finds four lines below that
threshold: F_IN/C22870534 at 28, U_ADC/C42457798 at zero, the eight
U_ISO devices/C53283916 at 16, and U_LDO/C7452883 at zero. The assembly source
records independent authorized-distributor stock for the latter two MPNs, but
that does not prove JLC allocation. The logged-in JLC uploader still must
confirm exact identities, allocation, rotations and polarity; C42457798 must
resolve to the exact CS5308P-DN suffix or exact CS5308P-DN must be consigned for
JLC placement. This sourcing hold does not refute the topology verdict.

No unresolved topology defect was found in the reviewed state. This witness
does not grant placement, routing, fabrication, uploader-preview, first-article
or order acceptance.
