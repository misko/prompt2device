# Addendum: artifact identity

The original probe audit directly read and SHA-256 hashed `projects/crow-usb-carrier-v1/03_tscircuit/build/circuit.json` **before its replacement**. The terminal result at that time was:

`30377f6fdecb4e69cefb3a2b24b91fa9288607ec40db4fe2f4e6a123a22a1033`

That is the prefix printed in `/tmp/crow-detail-probe.pdf`; the original report's PDF-to-candidate identity claim was based on this direct pre-replacement hash, not an inference from the prompt.

The current file now hashes to:

`4bbd4ca2d358814edf6617c2a2781253f2c4af8d63b3e0147081d916da64e138`

No new PDF comparison was performed. A read-only check of the current Circuit JSON confirms the XMOS sheet remains `schematic_sheet_29`, sheet index 30, with 129 ports and the same four-side perimeter pin arrangement (left/right/top/bottom pin sequences) recorded during the probe. The coverage result therefore remains a claim about the fixed probe PDF and the directly hashed former candidate, not a witness for the current candidate or any canonical SOUND record.
