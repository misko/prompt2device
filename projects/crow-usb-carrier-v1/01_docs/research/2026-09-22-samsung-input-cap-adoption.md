# Samsung input capacitor adoption — 2026-09-22

Replaced six GRM21BR61C106KE15L input capacitors with CL21A106KOCLRNC / C318695: same10uF16V±10%X5R0805 rating and unchanged circuit/footprint. Samsung primary HTML contains the exact family/packaging identity and typical DC/AC characteristic arrays; retained bytes and SHA are in the new dossier notes. An exact project-contract allowance and deviations register preserve this genuine primary web export without calling it a PDF.

Independent review rejected the initial30% combined retention assumption. The5.11605V DC sample retains35.959775%, and low-amplitude AC data retains75.4752%. Their product screens to27.14%; use the more adverse25% combined factor. With10% tolerance,15% temperature and10% lifecycle allowances, each two-capacitor bank is2×10×.9×.25×.85×.9=3.4425uF,14.75% above the3uF requirement. Separate typical curves and selected reserves do not guarantee joint PVT or aging; first-article input ripple/startup/load-step verification remains owed.

Root applied the reviewed correction to all three input banks (`dc_bias_derating_pct:75`) and reran early_design_check:4/4gatefamilies pass. All other bank bounds are unchanged. Expanded-source comparison changes only six MPN/supplier records:489components/85MPNs/1619ports/1493traces,zero errors,26critical endpoint checks. Modular489/489refs and54/54crossings pass.

Exact dated supplier observations report DigiKey37521 and JLC45399 for demand30. Root owning full sourcing composition is72/85two-pool,13one-pool,zero unparseable. Evidence:06_build/verification/samsung-cap-adoption and jlc-stock-samsung-composed.json. These dated observations do not imply assembly allocation. Native schematic, escape/process feasibility, routing and physical checks remain open.
