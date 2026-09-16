# Current source verification receipt

source_commit: 2378791ff6398e31ab41a506958b94deaae05166
completed_at: 2026-09-10T17:37:14.429186+00:00
reviewer: root source author and coordinator
independence: AUTHOR VERIFICATION ONLY; not an independent schematic witness
review_stage: source-verification
subject: crow-audio-carrier-v1 canonical v9 producer outputs
acceptance: PENDING independent exact topology and integrated native/PDF review
order_verdict: DO-NOT-ORDER

03_tscircuit/build/circuit.json: 78c7ffbf7defc297dfa6ca88d5b24e2ae9bd4e2de96931c0f8cb91ba1488bb3f
03_tscircuit/build/schematic.pdf: 194529d5a49eda59bfeeb7f028acda030c8916f670518ca241c12e440a282a8e
04_kicad/crow_audio_carrier_v1.kicad_sch: 43eaaa45fb16a68ee45f910765976f443a4070aafd86d67c9039f3b02bf9a0ef
06_build/netlists/crow_audio_carrier_v1.net: 6eddbc460ce1a05e34df68e37bf955adbca8ef8dba7982609d7b1f79adf36980
netlist_sha256: 471b96bf68be1fc3e5425b97cdace0f4a11cf929929011cf55170248f2129f9a
design_rules_sha256: 672f0b9be3b3f9b6c2a9c9c1b1ea0e12ff4d91f061ede29ac36d6ac71965b8a4
parts_sha256: 2f76a9ca1a8b2e3cf948d3b43fbbbc6ad101f1fccd58de1d7ecd05c556b2f38d

The canonical rebuild completed91.331s with its intentional prelayout pause.
The existing authorized public-catalog path resumed in3.339s and stopped only
at seven stale independent-review bindings. Frozen input coverage455/455,
prelayout checkpoint11/11 and schematic checkpoint7/7 were established by
their owning gates. No checkpoint was restamped to admit changed source.
The prior complete459-entry cohort was archived before producer restart.
The generated prelayout request has51code rows; the operator response remains
blank. No allocation or manufacturer response is claimed.

Full source unittest discovery:325/325PASS in129.988s. Shared converter:
57/57PASS,18known-bad. Native occlusion:34/34PASS,17known-bad plus the existing
one declared pin-name/number text blind spot. Shared contracts:17/17PASS,
13known-bad. All these runs use the live committed methods and actual producer
outputs where applicable; none substitutes for independent human judgment.

The final new tests were run with both live shared methods temporarily replaced
by exact git74fd38dd bytes, then restored in a finally block. Converter selection
is1PASS/2FAIL: passive/supplier-only controls remain valid while missing MPN and
missing authored native headings fail actual KiCad glyph assertions. Occlusion
selection is1PASS/3FAIL: unsupported effects still refuse, while supported
free-text collisions, clear geometry and independently rendered calibration
are unmodelled by the old checker. The repaired full suites pass. Hidden
manufacturer and complete multivendor/multicode sourcing data are also read
back through KiCad's XML exporter, including quoted purchasing strings.

Current native ERC has0errors. The separate all-severity report has2610warnings;
this is not an all-severity-zero claim. Native S-OCCL reports0findings over2986
placed drawable objects, zero unmodelled; S-WNET reports0ambiguities over2106
wires and282junctions. There are333source component identities and937physical
pins. The complete native PDF/SVG exports measure632.460x3000.375mm, with all
foreground/frame stroke bounds(8.8708,9.9238)..(622.5362,2990.4562) inside.
This is the fresh canonical export verification completed17:28:47Z within its
120s bound; the earlier private report written0.179s after its own deadline
is explicitly forensic and supplies no acceptance here.

An independent KiCad netlist export matches the preceding74fd electrical sets:
178named nets,895connected memberships,42intentional NC. All333native package
assignments are equal and all333source manufacturer/supplier maps are retained.
54Values now display authored MPNs; engineering R/C values are retained. Native
headings retain source function/inductance annotations, including the TDM
inverter/buffer distinction. Source control-pin arrangement and explicit label
anchors change drawing geometry. The new authored group renumbers333source
component group pointers through three bijective group-ID changes; every other
source_component field agrees. These are measured distinctions, not an
assertion that the full Circuit JSON or normalized native netlist is unchanged.

No full-policy, current PCB, placement, routing, release, manufacturer allocation,
physical qualification or order acceptance follows. The required fresh exact
independent schematic reviews remain pending. Realized copper/return/thermal
obligations, all inherited bounded-model qualifications and actual first-article
measurements remain assigned to their owning later gates.

Exact root execution-log SHA256 values (private logs retained under
/tmp/carrier-policy-repair-20260910.oc5jllj4; this receipt records observed results):

- source-tests-v9.log: e6f39b136584882a657366236d0da255f5ffc6a0fb9c59bbe920d42efb8023e4
- native-converter-v9-green.log: 3b88f8a2d686b85207c0bd72d20a028e88e81880e203af1ff80bf1887411081a
- native-occlusion-identity-green-final.log: 71736c3bf48036a041be27b836bb7c25f81f116b3994b6f9226598da61717920
- contracts-v9-green.log: 4eedddbcfec8afb507da0c6ffe18ac8a1ba036b93c6653d117f8192b0e03110a
- native-v9-final-git-swap-red-t1_converter.py.log: c148b96d2434564dce3773b1bb00914f62c524034bec67d2509d3d03159c0141
- native-v9-final-git-swap-red-t1_occlusion.py.log: ab05dc8cf43a72864bcc6573ad1c9511fd770b398a7dde0fe985bf2efed5dfeb
- regenerate-v9.log: 238eb5b32e962453315e1acd1bfbe42888c948c55c85da876f7ecd4891ae8b87
- public-resume-v9.log: 6a4b925d35d4ae3512df0671da5c27544cbac4bdf95ccae82018d42a22b1f5f2
- native-v9-occlusion.json: c68b22e814e35f197c0ee8c8c95869619c4c83edfb262cce5d2f18e2359bd934
- native-v9-current-export/root-verification.json: 860401c472e0ab9c93f757d54c7d5787f56f62ac56aa1e1c38921a22d340875d


Downstream identity follow-up: the shared board-generator regression suite
passes58/58, including35known-bad cases. Read-only resolution of the current
native netlist loads333/333 exact source footprints; none carries a static
LCSC Part field that could conflict after the Value change. The authoritative
Circuit JSON code reader returns300coded references, and the fabrication
exporter consumes that per-refdes source directly. No current project PCB was
generated during this check and no board-stage acceptance is inferred.

- generator-native-identity-v9.log: 0e54e2341b31e185e70132799ed34add6ae294b9153706f36f3234743fd2561e
- native-v9-downstream-identity.json: 25ad64608aa015aec5213f8adbb9c1c522bd0e7f2d1583f7346c73fb1a5a8380
