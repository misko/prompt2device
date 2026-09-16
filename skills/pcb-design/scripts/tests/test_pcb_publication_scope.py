#!/usr/bin/env python3
"""Tests for fail-closed boardless system publication expansion.

All project paths are synthesized under each test's temporary Git repository;
no live project, board, or release is consumed as a fixture.
"""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))

import pcb_publication_gate as gate  # noqa: E402


def project_path(name, *parts):
    """Repository-relative POSIX path in the isolated synthetic fixture."""
    return Path("projects", name, *parts).as_posix()


class SystemPublicationScopeTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="pcb-publish-scope-")
        self.root = Path(self._tmp.name)
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")

    def tearDown(self):
        self._tmp.cleanup()

    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=self.root, check=True, text=True,
            stdout=subprocess.PIPE).stdout.strip()

    def write(self, relative, text="fixture\n"):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def scope(self, children=None):
        return json.dumps({
            "schema": 1,
            "kind": "system-integration",
            "pcb_children": children or [
                project_path("child-a"), project_path("child-b")],
        }, indent=2) + "\n"

    def commit(self):
        self.git("add", ".")
        self.git("commit", "-qm", "fixture")
        return self.git("rev-parse", "HEAD")

    def populate_valid_system(self):
        self.write(
            project_path("system", "01_docs/project-scope.json"), self.scope())
        self.write(project_path("child-a", "04_kicad/a.kicad_pcb"))
        self.write(project_path("child-b", "04_kicad/b.kicad_pcb"))

    def test_marker_is_material(self):
        self.assertTrue(gate.is_material_project_path(
            project_path("system", "01_docs/project-scope.json")))

    def test_valid_parent_expands_to_all_children(self):
        self.populate_valid_system()
        head = self.commit()
        selected, integrations, findings = gate._expand_system_integrations(
            [project_path("system")], head, self.root, base=head)
        self.assertEqual(
            selected, [project_path("child-a"), project_path("child-b")])
        self.assertEqual(
            integrations,
            [(project_path("system"),
              (project_path("child-a"), project_path("child-b")))])
        self.assertEqual(findings, [])

    def test_parent_with_board_cannot_claim_boardless_scope(self):
        self.populate_valid_system()
        self.write(project_path("system", "04_kicad/former.kicad_pcb"))
        head = self.commit()
        selected, integrations, findings = gate._expand_system_integrations(
            [project_path("system")], head, self.root, base=head)
        self.assertEqual(selected, [])
        self.assertEqual(integrations, [])
        self.assertEqual(len(findings), 1)
        self.assertIn("owns or owned live board", findings[0][1])

    def test_missing_or_boardless_child_fails_scope(self):
        self.write(
            project_path("system", "01_docs/project-scope.json"), self.scope())
        self.write(project_path("child-a", "04_kicad/a.kicad_pcb"))
        self.write(project_path("child-b", "README.md"))
        head = self.commit()
        selected, integrations, findings = gate._expand_system_integrations(
            [project_path("system")], head, self.root)
        self.assertEqual(selected, [])
        self.assertEqual(integrations, [])
        self.assertEqual(len(findings), 1)
        self.assertIn("owns 0", findings[0][1])

    def test_parent_release_payload_cannot_hide_behind_children(self):
        self.populate_valid_system()
        self.write(project_path("system", "07_releases/fake/MANIFEST.txt"))
        head = self.commit()
        selected, integrations, findings = gate._expand_system_integrations(
            [project_path("system")], head, self.root, base=head)
        self.assertEqual(selected, [])
        self.assertEqual(integrations, [])
        self.assertEqual(len(findings), 1)
        self.assertIn("forbidden circuit/release payload", findings[0][1])

    def test_scope_parser_rejects_duplicate_children(self):
        text = self.scope([project_path("child-a"), project_path("child-a")])
        with self.assertRaisesRegex(ValueError, "sorted list.*unique"):
            gate._parse_system_scope(text, project_path("system"))


if __name__ == "__main__":
    unittest.main()
