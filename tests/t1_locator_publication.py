#!/usr/bin/env python3
"""Portable replay controls for sealed assembly-locator evidence."""
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
from harness import FAB_SCRIPTS, KPY, ROOT, contains, main, must_fail, must_pass, run, test, tmpdir


RELEASE = (ROOT / "projects/crow-audio-carrier-v1/07_releases/"
           "v0.1.2-2026-09-16")


def replay(release):
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


@test("sealed release locator replays without pcbnew or Pillow")
def t_sealed_without_native_dependencies():
    result = must_pass(replay(RELEASE), "sealed locator without native dependencies")
    contains(result.out, "A-LOCATOR PASS")
    contains(result.out, "23/23 exception pages")


@test("portable sealed locator rejects a corrupt hashed member", kind="known_bad")
def t_sealed_without_native_dependencies_corrupt():
    root = tmpdir("locator_publication_")
    try:
        candidate = root / RELEASE.name
        shutil.copytree(RELEASE, candidate)
        (candidate / "fab/assembly_locator_001.png").unlink()
        must_fail(replay(candidate), "corrupt portable sealed locator",
                  "missing/corrupt manifest member")
    finally:
        shutil.rmtree(root)


if __name__ == "__main__":
    sys.exit(main())
