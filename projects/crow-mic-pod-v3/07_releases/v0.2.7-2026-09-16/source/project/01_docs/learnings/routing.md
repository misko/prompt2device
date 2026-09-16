# Routing-stage learnings

## Physical adjacency is not realized copper adjacency
- what happened: centroid-distance checks passed while the first routed board sent the negative audio leg about 13 mm through two vias before its ESD clamp and sent the LDO output through a long, via-bearing path before the required bulk capacitor.
- root cause: the placement gate measured endpoint proximity, not the saved copper graph, route order or layer changes.
- avoid next time: grade exact pad-to-pad route length, layer changes and connector-first dominance on the realized board; require the safety/stability prefix to be unavoidable before downstream branches.
- candidate-canon: no — this project now implements the required realized-route checks and hostile cases; the shared lesson is already represented by the route-acceptance and exact-copper review gates.

## A clean generic route report is not a safety-topology proof
- what happened: generic routing and native DRC were green on copper that still branched to loads before the TVS and allowed a long pre-clamp audio exposure.
- root cause: connectivity and clearance answer whether copper is legal and connected, not whether current or transients traverse components in the intended order.
- avoid next time: encode protection order as graph-cut/dominance assertions and replay them against the final board, independently of DRC and shortest-path summaries.
- candidate-canon: yes — retain a reusable connector-to-protection dominance check with a hostile parallel-bypass fixture.

## Datasheet operating limits must be distinguished from absolute maximums
- what happened: the first source facts used the TPS7A49 36 V absolute maximum as its recommended operating ceiling and omitted signed feedback-pin current from the regulator corner calculation.
- root cause: headline ratings were copied without retaining the table role, sign convention and equation that consume them.
- avoid next time: store recommended and absolute limits separately, encode signed bias current, and require the executable corner calculation to reproduce the declared rail window.
- candidate-canon: no — E-TOPO now checks the signed feedback window and the corrected dossier separately records 35 V recommended and 36 V absolute limits.

## Final reviews must precede the layout seal
- what happened: an early seal became stale as soon as final review files were added, because the governed source census correctly includes every `08_reviews` judgment.
- root cause: the tentative sequence treated reviews as outputs of the seal even though they are inputs to its trust claim.
- avoid next time: commit all exact-board reviews first, then issue one reviewed-commit layout seal and copy that post-review seal into release evidence; reviews must not bind the downstream seal hash.
- candidate-canon: no — the layout-seal flow now enforces reviewed-commit provenance and includes review bytes in its source snapshot.

## Public catalog evidence is not authenticated assembly allocation
- what happened: all exact public catalog rows were resolvable and the public twin mounted 31/31 bodies, but no logged-in JLCPCB BOM resolution or placement preview existed.
- root cause: public part identity, stock visibility and geometry are different authorities from the assembler's order-time allocation and orientation acceptance.
- avoid next time: keep design and sourcing verdicts separate; permit a design release with `BLOCKED-SOURCING`, but never turn public catalog evidence into an order authorization.
- candidate-canon: no — the release and PCBA receipt schemas already enforce this separation.


## A zone DRC endpoint does not identify its disconnected fill component
- what happened: an unrouted GND row naming C10.2 was carried forward as a possible local capacitor-return problem. Fresh independent native polygon/graph review found C10 already on broad ground through two0.499 mm spokes; the disconnected component actually held R7.2/C9.2. Exact review evidence: `01_docs/journal/0af80497152923b20263b051e83421b4b067582b0004b723e69c664aa5cfef38.tar.gz`.
- root cause: one KiCad zone UUID covers multiple disconnected fill polygons, and its reported nearest opposite endpoint is not the isolated component's identity. Pad/UUID lookup alone cannot assign the root cause.
- avoid next time: when a DRC endpoint is a zone, enumerate its filled polygon components and each component's pads, vias and graph connections before selecting the source correction. Preserve the raw row and distinguish the reported endpoint from the disconnected network.
- candidate-canon: yes — extend the existing all-unconnected classification guidance with component-aware zone diagnosis; do not invent a new pass or infer RF performance from DC connectivity.
