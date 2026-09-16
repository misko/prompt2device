# ADR-0001 — one-CS5308P TDM8 topology for eight synchronous channels

Status: accepted for first article
Date: 2026-09-01

Use one CS5308P-DN in hardware secondary ASP, minimum-slot TDM mode. The external MCHStreamer is the only clock master. Multiple stereo ADCs were rejected because they add independent clock/configuration state, inter-device phase uncertainty, and extra serial aggregation without improving the eight-channel requirement. A generic ADC module was rejected because no reviewed module exposes eight active-balanced analog inputs, the mandated spoke pinout, and the MCHStreamer TDM8 electrical boundary.

Consequences: the CS5308P QFN, reference network, buffered VMID, reset sequence, and external input stages are all critical. The bare-IC exception is deliberate and must remain machine-visible in `integration.yaml`.

2026-09-07 source correction: DS1314F1 Table1-2 p6 requires unused SPI_CS
pin38 high at VDD_IO. It now ties3V3_ADC. The other unused control pins
35/36/37 remain GND. The exact source and generated-pin invariant must
retain this distinction; a blanket all-unused-control-pins-to-GND rule is wrong.


## Proposed 2026-09-13 complete support-boundary correction

The integration inventory excludes U_ADC itself. Its252-ref ADC/front-end
boundary is192channel coupling/buffer/filter/isolation supports,52ADC reference,
mode,clock,reset and interface parts, plus8external bias supports. This is a
functional inventory, not a minimal or module-replaceable part count. The
complete fitted carrier has333refs. All80other external dependencies remain:
9local buck supports, U_BUCK and70shared power/spoke/infrastructure parts.
Those shared rails, holds, supervisors and protection remain necessary to the
architecture; they are not made dispensable by this accounting boundary. The
ADC remains above threshold10 and retains its existing evidenced module trade
study and bare-IC decision. No unresearched module is claimed to fail.

- analog_channel_support: C_A1N, C_A1P, C_A2N, C_A2P, C_A3N, C_A3P, C_A4N, C_A4P, C_A5N, C_A5P, C_A6N, C_A6P, C_A7N, C_A7P, C_A8N, C_A8P, C_ADC_CM1N, C_ADC_CM1P, C_ADC_CM2N, C_ADC_CM2P, C_ADC_CM3N, C_ADC_CM3P, C_ADC_CM4N, C_ADC_CM4P, C_ADC_CM5N, C_ADC_CM5P, C_ADC_CM6N, C_ADC_CM6P, C_ADC_CM7N, C_ADC_CM7P, C_ADC_CM8N, C_ADC_CM8P, C_FB1N, C_FB1P, C_FB2N, C_FB2P, C_FB3N, C_FB3P, C_FB4N, C_FB4P, C_FB5N, C_FB5P, C_FB6N, C_FB6P, C_FB7N, C_FB7P, C_FB8N, C_FB8P, C_FILTER1N1, C_FILTER1N2, C_FILTER1P1, C_FILTER1P2, C_FILTER2N1, C_FILTER2N2, C_FILTER2P1, C_FILTER2P2, C_FILTER3N1, C_FILTER3N2, C_FILTER3P1, C_FILTER3P2, C_FILTER4N1, C_FILTER4N2, C_FILTER4P1, C_FILTER4P2, C_FILTER5N1, C_FILTER5N2, C_FILTER5P1, C_FILTER5P2, C_FILTER6N1, C_FILTER6N2, C_FILTER6P1, C_FILTER6P2, C_FILTER7N1, C_FILTER7N2, C_FILTER7P1, C_FILTER7P2, C_FILTER8N1, C_FILTER8N2, C_FILTER8P1, C_FILTER8P2, C_ISO1, C_ISO2, C_ISO3, C_ISO4, C_ISO5, C_ISO6, C_ISO7, C_ISO8, C_OPA1, C_OPA2, C_OPA3, C_OPA4, C_OPA5, C_OPA6, C_OPA7, C_OPA8, R_ADC_PD1N, R_ADC_PD1P, R_ADC_PD2N, R_ADC_PD2P, R_ADC_PD3N, R_ADC_PD3P, R_ADC_PD4N, R_ADC_PD4P, R_ADC_PD5N, R_ADC_PD5P, R_ADC_PD6N, R_ADC_PD6P, R_ADC_PD7N, R_ADC_PD7P, R_ADC_PD8N, R_ADC_PD8P, R_B1N, R_B1P, R_B2N, R_B2P, R_B3N, R_B3P, R_B4N, R_B4P, R_B5N, R_B5P, R_B6N, R_B6P, R_B7N, R_B7P, R_B8N, R_B8P, R_IN1N, R_IN1P, R_IN2N, R_IN2P, R_IN3N, R_IN3P, R_IN4N, R_IN4P, R_IN5N, R_IN5P, R_IN6N, R_IN6P, R_IN7N, R_IN7P, R_IN8N, R_IN8P, R_OUT1N, R_OUT1P, R_OUT2N, R_OUT2P, R_OUT3N, R_OUT3P, R_OUT4N, R_OUT4P, R_OUT5N, R_OUT5P, R_OUT6N, R_OUT6P, R_OUT7N, R_OUT7P, R_OUT8N, R_OUT8P, R_X1N, R_X1P, R_X2N, R_X2P, R_X3N, R_X3P, R_X4N, R_X4P, R_X5N, R_X5P, R_X6N, R_X6P, R_X7N, R_X7P, R_X8N, R_X8P, U_AFE1, U_AFE2, U_AFE3, U_AFE4, U_AFE5, U_AFE6, U_AFE7, U_AFE8, U_ISO1, U_ISO2, U_ISO3, U_ISO4, U_ISO5, U_ISO6, U_ISO7, U_ISO8.
- adc_references_modes_clocks_reset_interfaces: C_CLK, C_FILT1_10U, C_FILT1_1U, C_FILT1_470U, C_FILT2_10U, C_FILT2_1U, C_FILT2_470U, C_LDO_A, C_LDO_D, C_OE, C_RST1, C_RST2, C_RST_T, C_TDM, C_TDM_SCH, C_VDDA1_10N, C_VDDA1_4U7, C_VDDA2_10N, C_VDDA2_4U7, C_VDDIO, C_VMID1_470N, C_VMID1_4U7, C_VMID2_470N, C_VMID2_4U7, J10, J11, Q_RST1, R_BCLK, R_CFG1, R_CFG2, R_CFG4, R_CFG5, R_FILT1P, R_FILT2P, R_FSYNC, R_MCH_BCLK_PD, R_MCH_FSYNC_PD, R_MCH_MCLK_PD, R_MCH_SENSE, R_MCH_SENSE_PD, R_MCLK, R_RESET_GPD, R_RESET_PU, R_RST_T, R_TDM, R_TDM_PD, U_CLK, U_OE, U_RST1, U_RST2, U_TDM, U_TDM_SCH.
- external_bias: R_VMID1_TOP, R_VMID1_BOT, C_VMID1_EXT_10U, C_VMID1_EXT_1U, R_VMID2_TOP, R_VMID2_BOT, C_VMID2_EXT_10U, C_VMID2_EXT_1U.
- buck_local_support: D_BUCK_IN, C_BUCK_IN, C_BUCK_IN2, C_BUCK_IN3, C_BUCK_BST, L_BUCK, C_BUCK_O1, C_BUCK_O2, C_BUCK_O3.
- subsystem_ics: U_ADC, U_BUCK.
- shared_power_spoke_connector_infrastructure: C_AUDIO, C_AUDIO_CT1, C_AUDIO_CT2, C_DUMP_LOGIC, C_DUMP_TIME, C_HOLD1, C_HOLD2, C_LDO_EN, C_LDO_IN, C_LDO_NR4, C_LDO_NR5, C_LDO_OUT, C_OPA_BULK, C_PWR, C_PWR_CT, D_HOLD, D_IN, D_QIN_GS, F1, F2, F3, F4, F5, F6, F7, F8, F_IN, J1, J2, J3, J4, J5, J6, J7, J8, J9, Q_DUMP, Q_IN, Q_PRE, Q_PRE_EN, R_ADC_BOT, R_ADC_TOP, R_AUDIO_PD, R_AUDIO_PU, R_DUMP, R_DUMP_PD, R_DUMP_TIME1, R_DUMP_TIME2, R_LDO_SET, R_OPA_BLEED1, R_OPA_BLEED2, R_PRE, R_PRE_G, R_PWR_BOT, R_PWR_PU, R_PWR_TOP, R_QIN_G, U_AUDIO, U_DUMP, U_ESD1, U_ESD2, U_ESD3, U_ESD4, U_ESD5, U_ESD6, U_ESD7, U_ESD8, U_LDO, U_LDO_EN, U_PWR.
