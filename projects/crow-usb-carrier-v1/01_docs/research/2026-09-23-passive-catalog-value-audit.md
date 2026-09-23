# Crow exact JLC catalog value audit

Scope: the eight code identities cited by `E-CLOSURE`'s `source_value_identity` failure in `06_build/verification/pipeline/electrical_closure.json`. This is read-only evidence for a later ledger adoption; it does not modify source, dossiers, or the ledger.

## Method and result

Each result below was extracted from the retained serialized direct JLC response in `06_build/verification/jlc-stock-xmos-exception-20260923/raw/`. Each response has one exact `componentCode` row. The reported code, MPN, manufacturer, catalog value attribute, tolerance, and package all agree with the selected `exact-parts.csv` identity and the expected electrical value. No network request was made for this audit.

| Code | Exact JLC identity | Catalog value / tolerance | Package | Retained completion UTC / raw SHA-256 |
|---|---|---|---|---|
| C852775 | YAGEO `RT0402BRD0740K2L` | 40.2kΩ / ±0.1%, ±25ppm/℃ | 0402 | 2026-09-23T14:21:57.944156+00:00 / `959bc62c4797bd204493901e23d22109d7c05e1ad7c5d1cd7d9b246c5d88ec9c` |
| C852832 | YAGEO `RT0402BRD0752K3L` | 52.3kΩ / ±0.1%, ±25ppm/℃ | 0402 | 2026-09-23T14:22:02.735014+00:00 / `d21d4ff7e49ef1598a920b0642d301efb6f757fad4542e624cbefe411256dbf8` |
| C852555 | YAGEO `RT0402BRD07169KL` | 169kΩ / ±0.1%, ±25ppm/℃ | 0402 | 2026-09-23T14:21:53.674430+00:00 / `06c80a47f07713326eab7d2cbce79556d15979bb645d9c0e0863b469569b6658` |
| C861412 | YAGEO `RT0603BRD07453KL` | 453kΩ / ±0.1%, ±25ppm/℃ | 0603 | 2026-09-23T14:22:11.426711+00:00 / `a057f170c8e60748e761e6539db046f803906c9ed966fd72c31e874da3d33086` |
| C122538 | YAGEO `RT0603BRD07100KL` | 100kΩ / ±0.1%, ±25ppm/℃ | 0603 | 2026-09-23T14:20:01.871760+00:00 / `7233b6f4e5df7bdc4176759d74af912d872648f0ae6606a4656e05b09a22903e` |
| C106996 | YAGEO `CC0402JRNPO9BN121` | 120pF / ±5%, NP0 | 0402 | 2026-09-23T14:19:58.646917+00:00 / `9b20d94ccb36998012a1f190d61bbfbe90790ecdd6c4c705e5f997d8b93daf15` |
| C852631 | YAGEO `RT0402BRD07210KL` | 210kΩ / ±0.1%, ±25ppm/℃ | 0402 | 2026-09-23T14:21:55.808223+00:00 / `2b1745c7e6449cb143c86733ffac26b8cb07dcc5f88a81c0f7866734d1a15eaf` |
| C852808 | YAGEO `RT0402BRD0749K9L` | 49.9kΩ / ±0.1%, ±25ppm/℃ | 0402 | 2026-09-23T14:22:00.521237+00:00 / `07f368c02fecc9bcd01cdbc00162fb0afc02dbd3e05da0c22387cbc94aa60d8f` |

The seven resistor values and one capacitor value exactly match the expected gate inputs: 40.2k, 52.3k, 169k, 453k, 100k, 120pF, 210k, and 49.9k. All eight code/MPN/value identities are suitable for the vetted passive ledger's code→MPN/value authority.

## Ledger-adoption candidates

The following is an adoption-ready fragment. Its `verified` strings identify the retained exact row and keep stock explicitly outside the authority claim.

```yaml
C852775: {mpn: RT0402BRD0740K2L, value: "40.2k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C852775, YAGEO RT0402BRD0740K2L, catalog Resistance 40.2kΩ, ±0.1%, ±25ppm/℃, 0402; raw SHA-256 959bc62c4797bd204493901e23d22109d7c05e1ad7c5d1cd7d9b246c5d88ec9c; catalog identity only."}
C852832: {mpn: RT0402BRD0752K3L, value: "52.3k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C852832, YAGEO RT0402BRD0752K3L, catalog Resistance 52.3kΩ, ±0.1%, ±25ppm/℃, 0402; raw SHA-256 d21d4ff7e49ef1598a920b0642d301efb6f757fad4542e624cbefe411256dbf8; catalog identity only."}
C852555: {mpn: RT0402BRD07169KL, value: "169k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C852555, YAGEO RT0402BRD07169KL, catalog Resistance 169kΩ, ±0.1%, ±25ppm/℃, 0402; raw SHA-256 06c80a47f07713326eab7d2cbce79556d15979bb645d9c0e0863b469569b6658; catalog identity only."}
C861412: {mpn: RT0603BRD07453KL, value: "453k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C861412, YAGEO RT0603BRD07453KL, catalog Resistance 453kΩ, ±0.1%, ±25ppm/℃, 0603; raw SHA-256 a057f170c8e60748e761e6539db046f803906c9ed966fd72c31e874da3d33086; catalog identity only."}
C122538: {mpn: RT0603BRD07100KL, value: "100k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C122538, YAGEO RT0603BRD07100KL, catalog Resistance 100kΩ, ±0.1%, ±25ppm/℃, 0603; raw SHA-256 7233b6f4e5df7bdc4176759d74af912d872648f0ae6606a4656e05b09a22903e; catalog identity only."}
C106996: {mpn: CC0402JRNPO9BN121, value: "120pF", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C106996, YAGEO CC0402JRNPO9BN121, catalog Capacitance 120pF, ±5%, NP0, 0402; raw SHA-256 9b20d94ccb36998012a1f190d61bbfbe90790ecdd6c4c705e5f997d8b93daf15; catalog identity only."}
C852631: {mpn: RT0402BRD07210KL, value: "210k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C852631, YAGEO RT0402BRD07210KL, catalog Resistance 210kΩ, ±0.1%, ±25ppm/℃, 0402; raw SHA-256 2b1745c7e6449cb143c86733ffac26b8cb07dcc5f88a81c0f7866734d1a15eaf; catalog identity only."}
C852808: {mpn: RT0402BRD0749K9L, value: "49.9k", verified: "2026-09-23 retained serialized JLC exact-code API row: componentCode C852808, YAGEO RT0402BRD0749K9L, catalog Resistance 49.9kΩ, ±0.1%, ±25ppm/℃, 0402; raw SHA-256 07f368c02fecc9bcd01cdbc00162fb0afc02dbd3e05da0c22387cbc94aa60d8f; catalog identity only."}
```

The catalog responses also expose stock counts, voltage, power, and operating-temperature attributes. They were not used to assert procurement, allocation, attrition, or assembly acceptance. The exact source electrical and footprint suitability remains governed by the existing part dossiers and electrical closure receipt.
