# Connector FULL public-record re-audit (Terra)

Read-only audit of the current 19 unknowns in
`06_build/verification/connector_assembly_contract.json`, the phase policy,
and retained public manufacturer records. No broad repeat web search was
needed: retained records already cover selected connector/mate identities and
dimensional planning inputs.

## Result

**Zero of the 19 targets is closable from a public drawing alone.** The open
set is four targets for RJ45, five each for USB and external power, and five
for JTAG. They are realized interface, reaction, operated service,
registration/tolerance, and where applicable installed cable-route targets.
Each predicate requires an exact populated candidate or governed coupon,
selected mate/cable/sample identity, and observed mating, restraint/service,
or installed-route evidence. Public records cannot show the realized board,
populated-neighbor state, enclosure, production seating/process contributors,
or sample response.

## Retained authoritative public records

| Assembly | Exact public record | What it can establish | Why it cannot close the target |
| --- | --- | --- | --- |
| J1–J8 RJ45 | Würth `615008160221` rev `001.003`, [PDF](https://www.we-online.com/components/products/datasheet/615008160221.pdf); Telegärtner `100009141` drawing `L00000A0149DP`, [PDF](https://www.telegaertner.com/fileadmin/pdms_files/L00000A0149DP.pdf) | identity and nominal/toleranced package/cable geometry | exact cross-manufacturer mating, latch/grip access, reactions, installed route and registration remain sample-dependent |
| J_USB | GCT `USB4215-03-A` drawing rev `A`, [public PDF](https://gct.co/files/drawings/usb4215.pdf); ASSMANN `ASS 7348 CA` rev `08`, [drawing](https://www.assmann-wsw.com/uploads/datasheets/ASS_7348_CA.pdf) | receptacle and cable dimensions | full engagement, populated service, PCB reaction, exit/bend/strain relief and registration require the article/coupon |
| J_PWR | Molex `43650` rev `D8`, [drawing](https://www.molex.com/content/dam/molex/molex-dot-com/products/automated/en-us/salesdrawingpdf/436/43650/436501000_sd.pdf); exact `43645-0200` [record](https://www.molex.com/en-us/products/part-detail/436450200) | compatible series and polarized latch family | harness, latch operation, reaction, cable route, service and tolerance stack are not drawing facts |
| J_JTAG | Samtec FTSH/FFSD prints and [FFSD catalog](https://suddendocs.samtec.com/catalog_english/ffsd.pdf) for `FTSH-105-01-L-DV-K` / `FFSD-05-D-06.00-01-N` | keyed pair identity and catalog geometry | cable-end exit, bend, service access, reactions and realized registration require a sample |

The retained USB and JTAG records explicitly leave bend/service or full
toleranced mate extents owed. New public drawings could refine a test fixture
or future bounds; they cannot substitute for the missing observations.

## Release impact

FULL remains `INCOMPLETE` with 19 physical unknowns. It continues to block
P3/routing promotion, integrated placement promotion, release and order. The
next evidence type is governed physical qualification, not catalog research;
no connector target is relaxed or waived by this re-audit.
