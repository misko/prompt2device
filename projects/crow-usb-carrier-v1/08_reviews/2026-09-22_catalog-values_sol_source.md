# Independent passive-ledger review

Date: 2026-09-22

Candidate: `7c928683ffa3389d34643ae65f5f6f83abc5f570`

Verdict: **ACCEPT**.

The five added `lcsc_passives_ledger.yaml` rows match singleton retained JLC exact-MPN catalog records. For every row, `componentCode`, `componentModelEn`, manufacturer, `erpComponentName`, and the catalog resistance/capacitance attribute support the committed code/MPN/value identity. The ledger text correctly limits these facts to offline catalog identity; it does not treat stock as an assembly allocation.

## Exact retained evidence

- `C2171626` / `CKG57KX7R1E476M335JH` / `47uF`: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/source-value-identity-c/evidence/CKG57KX7R1E476M335JH-jlc-exact.json`; SHA-256 `27bf6f53f324c54c72b4cee669a6a032adf66e457e6a3535c4e8b055f4491dec`. The singleton row identifies TDK, `47uF ±20% 25V`, catalog capacitance `47uF`, stock 0, queried `2026-09-22T15:21:11.333487+00:00`.
- `C3778009` / `R82DC4100CK60J` / `1uF`: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/jlc_fresh_85_a9bdd97d/evidence/uncoded-exact-search/14-R82DC4100CK60J.json`; SHA-256 `5723fa6739d98a3b57c6fde07e4634d64d198ab20a513f9844ae62b91e944220`. The singleton row identifies KEMET, `1uF ±5% 63V`, PET film, 5 mm pitch, stock 6, queried `2026-09-22T11:34:28.816292+00:00`.
- `C852472` / `RT0402BRD07100KL` / `100k`: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/jlc_fresh_85_a9bdd97d/evidence/uncoded-exact-search/19-RT0402BRD07100KL.json`; SHA-256 `c7605a36fa0745c526f29c6b32f94a6628bf4d49126d037768b354455e223496`. The singleton row identifies YAGEO, `100kΩ ±0.1% 62.5mW`, catalog resistance `100kΩ`, stock 778609, queried `2026-09-22T11:34:36.521258+00:00`.
- `C728556` / `RT0402BRD07200KL` / `200k`: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/jlc_fresh_85_a9bdd97d/evidence/uncoded-exact-search/20-RT0402BRD07200KL.json`; SHA-256 `eac669a8a738a5c0eeb3172878021796cc883907513f3c7cd0c5434fe66be824`. The singleton row identifies YAGEO, `200kΩ ±0.1% 62.5mW`, catalog resistance `200kΩ`, stock 145984, queried `2026-09-22T11:34:38.057418+00:00`.
- `C106253` / `CC0402KRX5R5BB105` / `1uF`: `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/jlc_fresh_85_a9bdd97d/evidence/uncoded-exact-search/07-CC0402KRX5R5BB105.json`; SHA-256 `54b9da984ba23547e300905ea44d544459738af61e6f0ef41ce95fd3138c4790`. The singleton row identifies YAGEO, `1uF ±10% 6.3V`, catalog capacitance `1uF`, stock 1012789, queried `2026-09-22T11:34:17.757498+00:00`.

## Retention note

The requested `/home/mouse9911/gits/circuits-trials/crow-usb-design-20260922/source_quotes_c/evidence` directory did not exist during review. The C2171626 capture above was untracked in the isolated candidate worktree, so it must be copied into the durable review/build archive. The other four raw captures were already retained under `jlc_fresh_85_a9bdd97d/evidence/uncoded-exact-search`.
