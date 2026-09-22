# Canonical PDF diagnostic triage — 2026-09-22

SOL agent crow_readability_repair inspected all40pages of the current delivered PDF. This was bounded read-only diagnostic work, not formal schematic acceptance.

No page-edge clipping or verified text overlap was found. All headings and circuit content remain within page bounds. The112producer outside_sheet advisories occur on pages1,26,27,31,32,35,36,37 (counts5,14,2,37,3,15,10,26); PDF auto-fit retains visible margins. Therefore those advisories alone do not establish clipping in the delivered artifact.

Page31 (U_XU) is the densest: all129pins are present, with very small but separated text at full-resolution inspection. Readability at intended viewing size remains for the formal review. Pages5,24,40 contain narrow portrait-oriented circuits, intact in the delivered PDF.

Root also inspected the40page contact sheet; it supports the page-envelope observation but is too small to establish pin-level legibility. No source change or gate waiver follows from this diagnostic.

Source presentation owners:03_tscircuit/src/z_schematic_presentation.tsx and z_analog_schematic_presentation.tsx. Retained local diagnostic images and warning inventory:06_build/verification/canonical-pdf-triage/.

PDF SHA256: `96b7b97cf123fd394b17f36794f12bebe1fab15161d4a0f5357549bfad2448b5`.

contact.png SHA256: `016b54fd88698ac7ca67fee43f4d82d7fa5157a3530f8ab7ee290dd72ae21510`.

advisory-pages.png SHA256: `72ab7db905b5f8b9c7e41894cb93b25447980196b659099793a6b648d416647b`.
