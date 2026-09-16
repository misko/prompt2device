#!/usr/bin/env python3
"""Default-suite entry for the independent assembly locator and its consumers."""
from pathlib import Path
import re
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import FAB_SCRIPTS, KPY, check, contains, main, must_fail, must_pass, run, test
sys.path.insert(0, str(FAB_SCRIPTS / "tests"))
from test_assembly_locator import LocatorTests


def cli_fixture(hostile=False):
    LocatorTests.setUpClass()
    try:
        root = Path(LocatorTests.base.name)
        if hostile:
            (root / "out/assembly_locator_001.png").unlink()
        return run([KPY, FAB_SCRIPTS / "assembly_locator_check.py", "exact",
                    root / "board.kicad_pcb", root / "bom.csv", root / "cpl.csv",
                    root / "config.yaml", root / "out"])
    finally:
        LocatorTests.tearDownClass()


@test("assembly locator public CLI reports complete reference and page coverage")
def t_public_coverage():
    result = must_pass(cli_fixture(), "complete native locator")
    contains(result.out, "3/3 references")
    contains(result.out, "2/2 exception pages")


@test("assembly locator public CLI rejects a missing required page", kind="known_bad")
def t_missing_page_blocks():
    must_fail(cli_fixture(True), "locator with missing page", "missing/corrupt manifest member")


@test("assembly locator native hostile cases and owning review/release consumers", kind="known_bad")
def t_native_controls():
    result = must_pass(run([KPY, FAB_SCRIPTS / "tests/test_assembly_locator.py"]), "locator controls")
    count = re.search(r"Ran (\d+) tests", result.out)
    check(count is not None and int(count.group(1)) >= 25, "all existing hostile and acceptance controls ran")
    contains(result.out, "OK")


if __name__ == "__main__":
    sys.exit(main())
