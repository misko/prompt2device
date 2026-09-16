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


def release_without_pcbnew(hostile=False):
    LocatorTests.setUpClass()
    case = LocatorTests("test_clean_full_denominators")
    case.setUp()
    try:
        release = case.make_release()
        if hostile:
            (release / "fab/assembly_locator_001.png").unlink()
        code = r'''
import builtins, runpy, sys
original = builtins.__import__
def blocked(name, *args, **kwargs):
    if name == "pcbnew" or name == "PIL" or name.startswith("PIL."):
        raise ModuleNotFoundError("simulated publication runner has no native CAD/raster dependencies")
    return original(name, *args, **kwargs)
builtins.__import__ = blocked
sys.argv = [sys.argv[1], "release", sys.argv[2]]
runpy.run_path(sys.argv[0], run_name="__main__")
'''
        return run([KPY, "-c", code, FAB_SCRIPTS / "assembly_locator_check.py",
                    release])
    finally:
        case.tearDown()
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


@test("sealed release locator replays without pcbnew")
def t_sealed_without_pcbnew():
    result = must_pass(release_without_pcbnew(), "sealed locator without pcbnew")
    contains(result.out, "A-LOCATOR PASS")
    contains(result.out, "2/2 exception pages")


@test("sealed release locator without pcbnew rejects corrupt members", kind="known_bad")
def t_sealed_without_pcbnew_corrupt():
    must_fail(release_without_pcbnew(True), "corrupt sealed locator without pcbnew",
              "missing/corrupt manifest member")


if __name__ == "__main__":
    sys.exit(main())
