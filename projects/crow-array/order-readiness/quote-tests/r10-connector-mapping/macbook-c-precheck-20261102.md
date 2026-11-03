# Pod J1 test C precheck: stopped before upload

2 November 2026. Base commit `138fee9817f7bf474737c2bed339afcf6f7da3d6`.
The existing `POD J1 AB TEST NOT FOR ORDER` draft opened; it remains on HOLD.
No C test or other CPL upload was made.

- JLC's BOM/CPL dialog showed `pod-cpl-J1-000-BASELINE.csv` as the saved CPL.
- JLC's loaded merge record showed J1 `ec` X `10.556`, Y `-8.373`, angle `0`;
  `lc_code` `C599441`, `is_mount` and `sel_mount` were true. Its default panel
  set had `x_offset: 0`, `y_offset: 0`, `ang: 0`. The BOM showed 20 grouped
  lines confirmed and the J1 row matched RJHSE-5080 / C599441.
- The PCB summary showed PCBA quantity 8. The saved fabrication quantity and
  both automatic review preferences could not be confirmed. The viewer's
  `Change PCB specifications` link opened the quote form at a URL containing
  the draft identifier, but it displayed **Add gerber file** and default
  values including 5 boards and 100 x 100 mm. This blank form is not evidence
  of the draft's actual fabrication quantity or preferences; no field was
  changed or submitted. Browser Back returned to the existing BOM.
- The documented read-only model-cache query returned the already-loaded OBJ
  for `7d3d1c9e95104606a19576559311bb67`: 523,591 characters, UTF-8 SHA-256
  `7e16867569831cd98a298dcf3dc5d4692343d067e36dc1aed26f7216d8ff39da`,
  matching the backend's independently downloaded measured asset.
- JLC displayed an automatic-save timestamp after navigation; no placement,
  BOM selection, quantity, preference, or file was deliberately changed.

Because the prerequisite saved quantity and review settings could not be
verified, stopped before uploading C. A remains in place; no C persistence,
mouth direction, or final restoration test was performed. No carrier check,
purchase, reservation, substitution, vendor message, or manufacturing
approval occurred. Native boards and production-intent drafts were untouched.
