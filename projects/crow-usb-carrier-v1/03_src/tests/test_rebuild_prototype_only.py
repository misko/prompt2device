#!/usr/bin/env python3
"""Policy regression for Crow's isolated prototype-only producer."""
import subprocess
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "rebuild_prototype_only.sh"


class PrototypeOnlyProducerTests(unittest.TestCase):
    def test_is_explicitly_admitted_and_has_no_downstream_escape(self):
        source = SCRIPT.read_text()
        subprocess.run(["bash", "-n", str(SCRIPT)], check=True)
        self.assertIn("critical_part_selection_admission.py\" . --require-prototype", source)
        self.assertIn('OUT="06_build/prototype_only/$STAMP"', source)
        self.assertIn('"status": "PROTOTYPE_ONLY"', source)
        # These are the ordinary downstream authority entry points.  Their
        # absence keeps a successful prototype run from looking like layout,
        # release, fabrication, or order acceptance.
        executable = "\n".join(line for line in source.splitlines()
                               if not line.lstrip().startswith("#"))
        for forbidden in (
            "rebuild_all.sh", "rebuild_reuse.sh", "pcb_flow.py",
            "generate_board_generic.py", "route_and_stitch_generic.py",
            "release_freshness_check.py", "release_review_preflight.py",
            "release_rehearsal.py", "pcb_publication_gate.py",
            "export_jlc_package.py", "jlc_pcba_availability.py",
        ):
            self.assertNotIn(forbidden, executable)


if __name__ == "__main__":
    unittest.main()
