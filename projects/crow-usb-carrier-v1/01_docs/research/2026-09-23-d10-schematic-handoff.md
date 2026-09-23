# Crow D10 schematic handoff — 2026-09-23

The canonical circuit is freshly generated at SHA-256 b323ca64ebeec6e7d3660304a03e6bb8c60e041cf1afcf73d436bd9d3b583c64. It has568 components and39 nonempty schematic pages. Root conductor passed M-FRESH9/9 and exported the KiCad schematic/netlist. After independently verified catalog-ledger additions09050504, the unchanged artifacts pass E-CLOSURE9/9 and manufacturing selection2/2. The ledger-only repair required no new producer. Skill authority,14/14 disclosure and15/15 documentation checks pass; SOL's BOM tests passed31, skipped2.

Manufacturing prelayout is INCOMPLETE2/4: exact code identity568/568 and source values pass; provider availability and procurement exposure lack a JLC receipt. Anonymous BOM upload redirects to sign-in, as recorded in2026-09-23-jlc-prelayout-access.md. This is the next operator boundary. Schematic ERC/readability/topology acceptance, block P1–P5, PCB routing and release remain owed; no PCB or sealed release exists.

## Prepared local files and next action

- `06_build/sourcing/crow-jlc-bom-upload.csv`:88 coded rows,544 refs per board; SHA-2564e47a09057169ebd2e38d6e141807aaf372efb76b3b6b049ef5b82a1e455f746. It is the tracked `01_docs/sourcing/exact-parts.csv` with only the24 D9 manual THT refs excluded. Quantities are per board: set the JLC build quantity to5.
- `06_build/sourcing/prelayout_request.json` and `prelayout_response.csv`:current88-line request and blank schema-v2 response; verify-request passes against the canonical circuit, assembly policy and procurement policy. Old84-line blank pair retained under ignored `historical-pre-d10/`.
- Sign in privately at https://jlcpcb.com/parts/bom-tool and upload the CSV. Save the actual matched codes, availability, recommended quantities/attrition, minimum quantities and costs/fees. Unknown fields remain unknown. Do not place an order or send credentials.
- Fill only observed fields, then use `jlc_pcba_availability.py grade` to produce `prelayout_receipt.json`; reopen it with `manufacturing_readiness.py grade --phase prelayout`. If the BOM tool does not expose all required economics, that evidence remains owed; public catalog counts cannot fill those gaps.
- Once the receipt passes, run the project conductor through its schematic checkpoint and obtain independent schematic review before placement. Do not use `--resume-after-schematic-review` until the new exact checkpoint is accepted.

The user-approved XMOS exception affects only the150-unit public-stock surplus for U_XU/C6362698, not JLC population, actual build demand or assembly attrition. The fresh public-stock audit reports88/88 passing including XMOS41 against5. It does not reserve stock or establish order readiness.
