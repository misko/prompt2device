# Unapplied island reservation source proposal

Original patch SHA256: `085a0f47dea38f0305d643238e8e7bba1a174379e0ee01c88e4701b98f40a543`. Extract only the fenced patch for application. USB anchor reassessment remains owed.

```diff
--- a/projects/crow-usb-carrier-v1/03_src/floorplan.yaml
+++ b/projects/crow-usb-carrier-v1/03_src/floorplan.yaml
@@ -95,8 +95,81 @@
 
 placement:
   require_anchor: true
-  anchors: {}
-  seeds: {}
+  anchors:
+    C_HOLD1: [30.85, 120.45, 0]
+    C_HOLD2: [42.95, 120.45, 0]
+    C_HOLD3: [55.05, 120.45, 0]
+    C_HOLD4: [67.15, 120.45, 0]
+    C_HOLD5: [30.85, 129.55, 0]
+    C_HOLD6: [42.95, 129.55, 0]
+    C_HOLD7: [55.05, 129.55, 0]
+    C_HOLD8: [67.15, 129.55, 0]
+    C_HOLD9: [82.85, 120.45, 0]
+    C_HOLD10: [94.95, 120.45, 0]
+    C_HOLD11: [107.05, 120.45, 0]
+    C_HOLD12: [119.15, 120.45, 0]
+    C_HOLD13: [82.85, 129.55, 0]
+    C_HOLD14: [94.95, 129.55, 0]
+    C_HOLD15: [107.05, 129.55, 0]
+    C_HOLD16: [119.15, 129.55, 0]
+    J1: [50, 26.86, 0]
+    J2: [72, 26.86, 0]
+    J3: [94, 26.86, 0]
+    J4: [116, 26.86, 0]
+    J5: [138, 26.86, 0]
+    J6: [160, 26.86, 0]
+    J7: [182, 26.86, 0]
+    J8: [204, 26.86, 0]
+    J_PWR: [30, 29.42, 0]
+    J_USB: [230, 23.675, 180]
+    J_JTAG: [228, 50, 90]
+  seeds:
+    D_HOLD: [28, 108]
+    R_PRE: [39, 108]
+    R_PRE_G: [43, 108]
+    Q_PRE: [43, 104]
+    Q_PRE_EN: [48, 106]
+    U_LDO: [133, 118]
+    C_LDO_IN: [128, 119]
+    C_LDO_OUT_1: [138, 116]
+    C_LDO_OUT_2: [138, 120]
+    R_LDO_SET: [135, 123]
+    C_LDO_NR4: [136, 126]
+    C_LDO_NR5: [140, 126]
+    U_ADC_A: [137, 96]
+    U_ADC_B: [137, 108]
+    C_VMID1_EXT_10U: [127, 89]
+    C_VMID1_EXT_1U: [130, 89]
+    C_VMID2_EXT_10U: [127, 102]
+    C_VMID2_EXT_1U: [130, 102]
+    C_ADC_A_AREG_100N: [128.0, 90]
+    C_ADC_A_AREG_1U: [131.2, 90]
+    C_ADC_A_AVDD_100N: [134.4, 90]
+    C_ADC_A_AVDD_10U: [137.6, 90]
+    C_ADC_A_DREG_100N: [140.8, 90]
+    C_ADC_A_DREG_1U: [128.0, 103]
+    C_ADC_A_IOVDD_100N: [131.2, 103]
+    C_ADC_A_IOVDD_10U: [134.4, 103]
+    C_ADC_A_VREF_100N: [137.6, 103]
+    C_ADC_A_VREF_10U: [140.8, 103]
+    C_ADC_B_AREG_100N: [128.0, 102]
+    C_ADC_B_AREG_1U: [131.2, 102]
+    C_ADC_B_AVDD_100N: [134.4, 102]
+    C_ADC_B_AVDD_10U: [137.6, 102]
+    C_ADC_B_DREG_100N: [140.8, 102]
+    C_ADC_B_DREG_1U: [128.0, 115]
+    C_ADC_B_IOVDD_100N: [131.2, 115]
+    C_ADC_B_IOVDD_10U: [134.4, 115]
+    C_ADC_B_VREF_100N: [137.6, 115]
+    C_ADC_B_VREF_10U: [140.8, 115]
+    U_ISO1: [23.3, 67.6]
+    U_ISO2: [60.4, 49.2]
+    U_ISO3: [82.4, 49.2]
+    U_ISO4: [104.4, 49.2]
+    U_ISO5: [126.4, 49.2]
+    U_ISO6: [148.4, 49.2]
+    U_ISO7: [170.4, 49.2]
+    U_ISO8: [202.7, 58.4]
   regions:
     adc_reference:
     - 75
@@ -113,6 +186,8 @@
     - 105
     - 75
     - 134
+    hold_bank_left: [24, 113, 74, 137]
+    hold_bank_right: [76, 113, 126, 137]
     digital_power:
     - 145
     - 85
@@ -700,6 +775,26 @@
     - U_BUCK
     region: input_buck
   - match:
+    - C_HOLD1
+    - C_HOLD2
+    - C_HOLD3
+    - C_HOLD4
+    - C_HOLD5
+    - C_HOLD6
+    - C_HOLD7
+    - C_HOLD8
+    region: hold_bank_left
+  - match:
+    - C_HOLD9
+    - C_HOLD10
+    - C_HOLD11
+    - C_HOLD12
+    - C_HOLD13
+    - C_HOLD14
+    - C_HOLD15
+    - C_HOLD16
+    region: hold_bank_right
+  - match:
     - C_AUDIO
     - C_AUDIO_CT1
     - C_AUDIO_CT2
@@ -712,22 +807,6 @@
     - C_DUMP_TIME6
     - C_DUMP_TIME7
     - C_DUMP_TIME8
-    - C_HOLD1
-    - C_HOLD10
-    - C_HOLD11
-    - C_HOLD12
-    - C_HOLD13
-    - C_HOLD14
-    - C_HOLD15
-    - C_HOLD16
-    - C_HOLD2
-    - C_HOLD3
-    - C_HOLD4
-    - C_HOLD5
-    - C_HOLD6
-    - C_HOLD7
-    - C_HOLD8
-    - C_HOLD9
     - C_LDO_EN
     - C_LDO_IN
     - C_LDO_NR4
@@ -866,12 +945,20 @@
   - match:
     - J_JTAG
     region: debug_connector
+  # Floating footprints may not occupy either pinned capacitor island.
+  forbid:
+  - rect: [24, 113, 74, 137]
+    margin: 0.25
+  - rect: [76, 113, 126, 137]
+    margin: 0.25
+  - rect: [74, 113, 76, 137]
+    margin: 0.25
   legalize:
     enable: true
     clearance: 0.25
     edge_margin: 1.0
     hole_keepout: 2.6
-    ring_max: 40
+    ring_max: 120
 design_rules:
   track_min_width: 0.15
   min_clearance: 0.15
```
