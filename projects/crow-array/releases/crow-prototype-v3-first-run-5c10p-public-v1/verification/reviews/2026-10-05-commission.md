# Independent PCB-COMMISSION admission review — 2026-10-05

Verdict: **PASS for commission admission only.** I independently read the five exact source subjects below, the project contracts, active hold, live status and commission journal. The selected repair-9/review-10 history is an unaccepted design baseline, not a commission fact or a substitute for the five reviewed inputs. This review makes no architecture, sourcing, schematic, firmware, physical-test, purchasing, fabrication or deployment acceptance claim. The coordinator alone may issue/check a current commission certificate and record promotion; this review does not remove the hold.

**Scope.** The original prompt and chronological decisions support two board types, eight microphone pods on an 8 m-diameter circle on a flat roof, five complete arrays (five carriers and 40 pods), eight raw channels over USB to a Raspberry Pi, pod buzzers controlled independently over USB for calibration, and CAT5/6 carrier-to-pod service. The later decision selects 12 V as the sole operating power and USB as data/control; USB VBUS may be sensed without supplying operating rails. Direction/position or timing-fingerprint computation is later work, not crow identity/analysis or a guaranteed localization result. The brief and R1–R9 trace these requirements and preserve the prompt/decision hashes. No prior Crow parts, budget, range or hardware capability is inherited. The `spares: 0` rule is a five-array quantity baseline, not a user prohibition on later spares.

**Input envelope.** The brief and requirements identify 10.8–13.2 V, an isolated regulated adapter rated at least 1 A continuous and no more than 2 A sustained short, at most 6 m copper four-pair CAT5e/6 runs and at most 0.5 ohm per supply/return path including hot contacts, electronics air −20 to 60 °C, 24 ksps/eight 24-bit transport words, useful 300 Hz–8 kHz audio, and source AC no more than 15 mVrms as *designer-proposed bounds*. These are not user equipment facts, an adapter identification, a guaranteed audio range/ENOB, or verified site conditions. No exact adapter, installed cable length, Pi model, cost ceiling or recording range is known. This is sufficient to commission a bounded prototype investigation, provided the architecture and circuit reviews prove compatibility with the bounds. Specify and verify the actual adapter, harness and site before connection/installation; if they fall outside the bounds, reopen the affected source and review. Circuit load, fault and margin calculations belong to the architecture/schematic reviews, not this commission verdict. A known circuit contradiction cannot be waived into a later physical test.

**Applicability.** Two flat non-RF board types, USB/high-speed digital timing, shared audio clocks, analog acquisition, interboard power/control/audio harnesses, sourcing/assembly, and outdoor mechanical qualification are in scope. CAT5/6 specifies cable service, not Ethernet or PoE. The profile's USB full-speed module, imported KiCad producer and flat hierarchy are designer assessments/source-route declarations, not user-mandated parts or proof of implementation. RF, galvanic isolation, lightning immunity and manufacturing readiness are explicitly unclaimed. USB timing and interboard return paths still need downstream engineering review.

**Qualification and authority boundary.** The proposed envelopes permit design work through editable complete schematic acceptance, subject to independent architecture, exact-source, harness, native-parity, PDF/readability and ERC review. They do not authorize a working board claim. Adapter/cable identity and continuity, first-article electrical/audio/thermal/EMC behavior, acoustic calibration, firmware and roof/ingress/site bonding remain explicit later falsifiers or deployment obligations. Physical requirements that depend on the installed roof and actual equipment are not fabricated as present facts. Placement, routing, buying, vendor contact, firmware implementation, physical modification/testing and fabrication are forbidden in this run. Stop for reflection at schematic acceptance. No further user choice is necessary to admit this bounded scope; a changed installed environment or an unbounded requirement would require a new decision/review before use.

```json
{
  "schema": 1,
  "stage": "PCB-COMMISSION",
  "author": "Astra adoption author",
  "reviewer": "SOL independent commission reviewer",
  "verdict": "PASS",
  "subjects": {
    "01_docs/BRIEF.md": "2fd110154d1234840a285f95d1b87f92219a32dbe1b8bcd7dc4ae18386c86699",
    "01_docs/capability-profile.json": "d9b204845b556dbe77b7c00593d9bb377fad2ccb00c3cb244360cda40866577b",
    "01_docs/inputs/PROMPT.md": "ffc7683516e2022a1bf6e2e1c834d2fbf460f8a1e17ac97b869a5bbb0542240c",
    "01_docs/inputs/USER_DECISIONS.md": "c1fa2df564fba7ae4d5cf3a62d28db11ecb124b7f0d1e5b1c3f7a67014609309",
    "03_src/rules/requirements.yaml": "56a9ee7d78f66c410bf244cdbac312d89c166164f25c2757a5722b85bb96658b"
  },
  "checks": {
    "scope": {
      "verdict": "PASS",
      "evidence": ["01_docs/BRIEF.md", "01_docs/inputs/PROMPT.md", "01_docs/inputs/USER_DECISIONS.md", "03_src/rules/requirements.yaml"],
      "rationale": "R1–R9 trace the two board types, eight pods and raw channels, calibration buzzers, CAT5/6, five complete arrays, later timing use and 12-V-only operating power to preserved chronological user inputs. Supersession and the schematic-only stop are explicit; no inherited budget or hardware is treated as authority."
    },
    "input_envelope": {
      "verdict": "PASS",
      "evidence": ["01_docs/BRIEF.md", "01_docs/inputs/PROMPT.md", "01_docs/inputs/USER_DECISIONS.md", "03_src/rules/requirements.yaml"],
      "rationale": "Critical supply, cable, temperature and acquisition limits are explicit, bounded designer assumptions, not user facts; unknown actual adapter and site/cable conditions have named verification before physical use. No circuit margin or actual equipment compatibility is certified by this criterion."
    },
    "applicability": {
      "verdict": "PASS",
      "evidence": ["01_docs/capability-profile.json", "01_docs/BRIEF.md", "03_src/rules/requirements.yaml", "01_docs/inputs/PROMPT.md"],
      "rationale": "The proposed two-flat-board non-RF route still identifies USB/high-speed digital, analog, clock, interboard harness, outdoor and assembly review obligations. CAT5/6 does not imply Ethernet/PoE; proposed producer/interface choices are not represented as user mandates or proven capabilities."
    },
    "qualification_boundary": {
      "verdict": "PASS",
      "evidence": ["01_docs/BRIEF.md", "01_docs/capability-profile.json", "03_src/rules/requirements.yaml", "01_docs/inputs/PROMPT.md", "01_docs/inputs/USER_DECISIONS.md"],
      "rationale": "The sources distinguish schematic-stage evidence from later fabrication/deployment and first-article obligations, preserve the no-purchase/no-physical/no-firmware/no-layout authorization and stop after schematic acceptance. Unknown physical conditions require verification; known contradictions cannot be postponed as tests."
    }
  }
}
```
