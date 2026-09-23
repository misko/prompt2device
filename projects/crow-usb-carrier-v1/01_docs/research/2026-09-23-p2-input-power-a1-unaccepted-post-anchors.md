# P2 input/quiet-power full-cell A1 unaccepted post-anchor proposal

Status: **research only; not active `03_src/floorplan.yaml`, not a P2 acceptance or route permission**. The accepted source HEAD for this experiment was `8fb310f4878d7ab00bbe5749407285f47d4a5327`; base floorplan SHA-256 `b0049211eaf65ef55f57db06d99da1ccc7b54296a0dd4eafe9ea3955d30bea3c`. This exact patch SHA-256 is `3049b6280af25b32eb4e5afc482c2d7c74e0486fdd5307a90e6b32ffab8311ce`; applying with `patch --batch --forward --fuzz=0 -p1` yields floorplan SHA-256 `9fbdea3e8f19dcba6d2f50426fdf1ee6576df319492d0b2bc22c83a44f04b4a5`.

The patch adds 72 `placement.post_anchors` to the bounded input/quiet-power candidate; it leaves the accepted source and raw Circuit JSON unchanged. One generated board from this patch is SHA-256 `12224f54c1da0bcfb30d0427167db1f0ec24e3f4569d09a19e2be249411312fc`. The exact 47-row power layout census is 38 pass/9 fail. See the dated [A2 assessment](2026-09-23-p2-input-power-a2-assessment.md) and [Terra diagnostic review](../../08_reviews/2026-09-23_p2-input-power-a2_terra_diagnostic.md). This retained proposal is a starting point for source backtrack and new bounded review, never an active or accepted floorplan. The old 3-seed probe was withdrawn without native generation.

```diff
--- a/03_src/floorplan.yaml
+++ b/03_src/floorplan.yaml
@@ -94,6 +94,79 @@
     at: [[0.0, 0.0]]

 placement:
+  post_anchors:
+    C_AUDIO: [24.7, 109.6, 90]
+    C_AUDIO_CT1: [22.7, 107.1, 0]
+    C_AUDIO_CT2: [22.7, 112.6, -90]
+    C_DUMP_LOGIC: [65.0, 96.0, 0]
+    C_DUMP_TIME1: [61.5, 93.5, 90]
+    C_DUMP_TIME2: [68.5, 93.5, 90]
+    C_DUMP_TIME3: [65.0, 90.0, 0]
+    C_DUMP_TIME4: [65.0, 98.0, 0]
+    C_DUMP_TIME5: [61.5, 97.5, -90]
+    C_DUMP_TIME6: [61.0, 90.0, 180]
+    C_DUMP_TIME7: [59.0, 96.5, -90]
+    C_DUMP_TIME8: [69.0, 97.0, 0]
+    C_IN1: [46.5, 92.1, 0]
+    C_IN2: [54.0, 97.5, 0]
+    C_IN3: [41.0, 97.5, 0]
+    C_IN_HF: [48.4, 102.4, 0]
+    C_LDO_EN: [78.2, 106.7, 0]
+    C_LDO_IN: [128.0, 119.2, 90]
+    C_LDO_NR4: [136.0, 126.0, 0]
+    C_LDO_NR5: [140.0, 126.0, 0]
+    C_LDO_OUT_1: [133.0, 122.2, 180]
+    C_LDO_OUT_2: [137.0, 117.2, 90]
+    C_OPA_BULK: [63.4, 108.3, 0]
+    C_OUT1: [53.2, 92.7, 0]
+    C_OUT2: [41.0, 92.0, 0]
+    C_OUT3: [45.9, 88.1, 0]
+    C_PWR: [74.0, 94.0, 90]
+    C_PWR_CT: [76.0, 96.5, 0]
+    C_PWR_CT2: [53.2, 101.3, 0]
+    C_PWR_CT3: [53.3, 138.2, 0]
+    C_VCC: [40.0, 100.2, 0]
+    C_VLDO: [43.3, 101.0, 0]
+    D_HOLD: [43.0, 108.0, 0]
+    D_IN: [34.0, 90.5, 0]
+    D_QIN_GS: [36.0, 102.5, 0]
+    F_IN: [31.5, 97.0, 90]
+    Q_DUMP: [34.3, 106.3, 0]
+    Q_IN: [36.0, 97.5, 0]
+    Q_PRE: [43.0, 104.0, 0]
+    Q_PRE_EN: [49.5, 105.5, 180]
+    R_ADC_BOT: [26.2, 107.6, 0]
+    R_ADC_TOP: [25.7, 111.6, 180]
+    R_AGND_JOIN: [40.9, 95.1, 0]
+    R_AUDIO_PD: [22.7, 105.1, 90]
+    R_AUDIO_PU: [26.2, 109.6, 90]
+    R_BUCK_FB_BOTTOM: [39.8, 103.9, 0]
+    R_BUCK_FB_TOP: [57.4, 93.9, 0]
+    R_DUMP: [33.8, 109.8, 0]
+    R_DUMP_PD: [31.3, 106.3, 90]
+    R_DUMP_TIME1: [68.0, 90.5, 0]
+    R_DUMP_TIME2: [68.0, 89.0, 180]
+    R_DUMP_TIME3: [65.0, 88.0, 180]
+    R_LDO_ILIM: [133.5, 115.2, 0]
+    R_LDO_PG_BOT_A: [30.8, 103.4, 0]
+    R_LDO_PG_BOT_B: [69.9, 102.8, 0]
+    R_LDO_PG_TOP: [137.0, 121.7, 90]
+    R_LDO_SET: [139.5, 121.2, 0]
+    R_OPA_BLEED1: [22.5, 119.5, 0]
+    R_OPA_BLEED2: [28.9, 101.8, 0]
+    R_PRE: [38.0, 107.0, 90]
+    R_PRE_G: [46.5, 104.5, 0]
+    R_PWR_BOT: [72.5, 92.0, 180]
+    R_PWR_PU: [78.5, 94.0, 0]
+    R_PWR_TOP: [76.0, 91.5, 0]
+    R_QIN_G: [36.0, 100.5, 0]
+    R_RT: [41.7, 87.5, 0]
+    U_AUDIO: [22.7, 109.6, 0]
+    U_BUCK: [47.5, 97.5, 0]
+    U_DUMP: [65.0, 93.5, 0]
+    U_LDO: [132.5, 118.2, 0]
+    U_LDO_EN: [78.2, 109.2, 0]
+    U_PWR: [76.0, 94.0, 0]
   require_anchor: true
   anchors:
     C_HOLD1: [30.85, 120.45, 0]
```

## Byte-exact patch payload

The readable diff above normalizes one whitespace-only added line so Markdown has no trailing whitespace. Decode this Base64 block to recover the exact frozen `.patch` bytes named by the SHA-256 above.

```base64
LS0tIGEvMDNfc3JjL2Zsb29ycGxhbi55YW1sCisrKyBiLzAzX3NyYy9mbG9vcnBsYW4ueWFtbApA
QCAtOTQsNiArOTQsNzkgQEAKICAgICBhdDogW1swLjAsIDAuMF1dCiAKIHBsYWNlbWVudDoKKyAg
cG9zdF9hbmNob3JzOgorICAgIENfQVVESU86IFsyNC43LCAxMDkuNiwgOTBdCisgICAgQ19BVURJ
T19DVDE6IFsyMi43LCAxMDcuMSwgMF0KKyAgICBDX0FVRElPX0NUMjogWzIyLjcsIDExMi42LCAt
OTBdCisgICAgQ19EVU1QX0xPR0lDOiBbNjUuMCwgOTYuMCwgMF0KKyAgICBDX0RVTVBfVElNRTE6
IFs2MS41LCA5My41LCA5MF0KKyAgICBDX0RVTVBfVElNRTI6IFs2OC41LCA5My41LCA5MF0KKyAg
ICBDX0RVTVBfVElNRTM6IFs2NS4wLCA5MC4wLCAwXQorICAgIENfRFVNUF9USU1FNDogWzY1LjAs
IDk4LjAsIDBdCisgICAgQ19EVU1QX1RJTUU1OiBbNjEuNSwgOTcuNSwgLTkwXQorICAgIENfRFVN
UF9USU1FNjogWzYxLjAsIDkwLjAsIDE4MF0KKyAgICBDX0RVTVBfVElNRTc6IFs1OS4wLCA5Ni41
LCAtOTBdCisgICAgQ19EVU1QX1RJTUU4OiBbNjkuMCwgOTcuMCwgMF0KKyAgICBDX0lOMTogWzQ2
LjUsIDkyLjEsIDBdCisgICAgQ19JTjI6IFs1NC4wLCA5Ny41LCAwXQorICAgIENfSU4zOiBbNDEu
MCwgOTcuNSwgMF0KKyAgICBDX0lOX0hGOiBbNDguNCwgMTAyLjQsIDBdCisgICAgQ19MRE9fRU46
IFs3OC4yLCAxMDYuNywgMF0KKyAgICBDX0xET19JTjogWzEyOC4wLCAxMTkuMiwgOTBdCisgICAg
Q19MRE9fTlI0OiBbMTM2LjAsIDEyNi4wLCAwXQorICAgIENfTERPX05SNTogWzE0MC4wLCAxMjYu
MCwgMF0KKyAgICBDX0xET19PVVRfMTogWzEzMy4wLCAxMjIuMiwgMTgwXQorICAgIENfTERPX09V
VF8yOiBbMTM3LjAsIDExNy4yLCA5MF0KKyAgICBDX09QQV9CVUxLOiBbNjMuNCwgMTA4LjMsIDBd
CisgICAgQ19PVVQxOiBbNTMuMiwgOTIuNywgMF0KKyAgICBDX09VVDI6IFs0MS4wLCA5Mi4wLCAw
XQorICAgIENfT1VUMzogWzQ1LjksIDg4LjEsIDBdCisgICAgQ19QV1I6IFs3NC4wLCA5NC4wLCA5
MF0KKyAgICBDX1BXUl9DVDogWzc2LjAsIDk2LjUsIDBdCisgICAgQ19QV1JfQ1QyOiBbNTMuMiwg
MTAxLjMsIDBdCisgICAgQ19QV1JfQ1QzOiBbNTMuMywgMTM4LjIsIDBdCisgICAgQ19WQ0M6IFs0
MC4wLCAxMDAuMiwgMF0KKyAgICBDX1ZMRE86IFs0My4zLCAxMDEuMCwgMF0KKyAgICBEX0hPTEQ6
IFs0My4wLCAxMDguMCwgMF0KKyAgICBEX0lOOiBbMzQuMCwgOTAuNSwgMF0KKyAgICBEX1FJTl9H
UzogWzM2LjAsIDEwMi41LCAwXQorICAgIEZfSU46IFszMS41LCA5Ny4wLCA5MF0KKyAgICBRX0RV
TVA6IFszNC4zLCAxMDYuMywgMF0KKyAgICBRX0lOOiBbMzYuMCwgOTcuNSwgMF0KKyAgICBRX1BS
RTogWzQzLjAsIDEwNC4wLCAwXQorICAgIFFfUFJFX0VOOiBbNDkuNSwgMTA1LjUsIDE4MF0KKyAg
ICBSX0FEQ19CT1Q6IFsyNi4yLCAxMDcuNiwgMF0KKyAgICBSX0FEQ19UT1A6IFsyNS43LCAxMTEu
NiwgMTgwXQorICAgIFJfQUdORF9KT0lOOiBbNDAuOSwgOTUuMSwgMF0KKyAgICBSX0FVRElPX1BE
OiBbMjIuNywgMTA1LjEsIDkwXQorICAgIFJfQVVESU9fUFU6IFsyNi4yLCAxMDkuNiwgOTBdCisg
ICAgUl9CVUNLX0ZCX0JPVFRPTTogWzM5LjgsIDEwMy45LCAwXQorICAgIFJfQlVDS19GQl9UT1A6
IFs1Ny40LCA5My45LCAwXQorICAgIFJfRFVNUDogWzMzLjgsIDEwOS44LCAwXQorICAgIFJfRFVN
UF9QRDogWzMxLjMsIDEwNi4zLCA5MF0KKyAgICBSX0RVTVBfVElNRTE6IFs2OC4wLCA5MC41LCAw
XQorICAgIFJfRFVNUF9USU1FMjogWzY4LjAsIDg5LjAsIDE4MF0KKyAgICBSX0RVTVBfVElNRTM6
IFs2NS4wLCA4OC4wLCAxODBdCisgICAgUl9MRE9fSUxJTTogWzEzMy41LCAxMTUuMiwgMF0KKyAg
ICBSX0xET19QR19CT1RfQTogWzMwLjgsIDEwMy40LCAwXQorICAgIFJfTERPX1BHX0JPVF9COiBb
NjkuOSwgMTAyLjgsIDBdCisgICAgUl9MRE9fUEdfVE9QOiBbMTM3LjAsIDEyMS43LCA5MF0KKyAg
ICBSX0xET19TRVQ6IFsxMzkuNSwgMTIxLjIsIDBdCisgICAgUl9PUEFfQkxFRUQxOiBbMjIuNSwg
MTE5LjUsIDBdCisgICAgUl9PUEFfQkxFRUQyOiBbMjguOSwgMTAxLjgsIDBdCisgICAgUl9QUkU6
IFszOC4wLCAxMDcuMCwgOTBdCisgICAgUl9QUkVfRzogWzQ2LjUsIDEwNC41LCAwXQorICAgIFJf
UFdSX0JPVDogWzcyLjUsIDkyLjAsIDE4MF0KKyAgICBSX1BXUl9QVTogWzc4LjUsIDk0LjAsIDBd
CisgICAgUl9QV1JfVE9QOiBbNzYuMCwgOTEuNSwgMF0KKyAgICBSX1FJTl9HOiBbMzYuMCwgMTAw
LjUsIDBdCisgICAgUl9SVDogWzQxLjcsIDg3LjUsIDBdCisgICAgVV9BVURJTzogWzIyLjcsIDEw
OS42LCAwXQorICAgIFVfQlVDSzogWzQ3LjUsIDk3LjUsIDBdCisgICAgVV9EVU1QOiBbNjUuMCwg
OTMuNSwgMF0KKyAgICBVX0xETzogWzEzMi41LCAxMTguMiwgMF0KKyAgICBVX0xET19FTjogWzc4
LjIsIDEwOS4yLCAwXQorICAgIFVfUFdSOiBbNzYuMCwgOTQuMCwgMF0KICAgcmVxdWlyZV9hbmNo
b3I6IHRydWUKICAgYW5jaG9yczoKICAgICBDX0hPTEQxOiBbMzAuODUsIDEyMC40NSwgMF0K
```
