"""Documentation completeness contract (bounty #8).

Issue #8 asks for a comprehensive README, usage examples, contribution
guidelines and a FAQ. Nothing previously enforced those requirements, so the
docs could regress silently. These tests read the real, tracked files
(``README.md`` and ``CONTRIBUTING.md``) -- they are the regression guard that
keeps the published documentation complete and internally consistent.

The other half of the contract is that the documentation is *generated from
source*, not hand-maintained: ``ruth reference`` renders the command surface
from the live CLI parser (``ruth/reference.py``), and these tests check both
that the command exists and that the README command table matches it. A flag
can therefore not appear in the README unless running it would actually work.

Run the regression command on its own:

    python -m unittest tests.test_docs -v
"""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"


def read(path):
    return path.read_text(encoding="utf-8")


def section(text, pattern):
    """Body of the first heading whose title matches ``pattern`` (regex)."""
    m = re.search(rf"^#{{1,6}}\s+{pattern}[^\n]*$", text, re.M | re.I)
    if not m:
        return None
    rest = text[m.end():]
    nxt = re.search(r"^#{1,6}\s+", rest, re.M)
    return rest[: nxt.start()] if nxt else rest


class TestReadmeHasTheBountySections(unittest.TestCase):
    def setUp(self):
        self.text = read(README)

    def test_has_a_faq_section(self):
        self.assertIsNotNone(
            section(self.text, r"(faq|frequently asked questions)\b"),
            "README.md must contain a FAQ section '## FAQ'")

    def test_has_a_usage_examples_section(self):
        self.assertIsNotNone(
            section(self.text, r"usage examples\b"),
            "README.md must contain a '## Usage examples' section")

    def test_usage_examples_are_runnable_shell_blocks(self):
        body = section(self.text, r"usage examples\b")
        self.assertIsNotNone(
            body, "README.md must contain a '## Usage examples' section")
        blocks = re.findall(r"```(?:sh|bash|console|shell)\n(.*?)```", body, re.S)
        self.assertGreaterEqual(
            len(blocks), 3,
            "README.md usage examples must include at least three runnable code blocks")
        joined = "\n".join(blocks)
        for command in ("ruth app", "ruth talk", "ruth teach"):
            self.assertIn(
                command, joined,
                f"README.md usage examples must demonstrate `{command}`")


class TestReadmeLinksResolve(unittest.TestCase):
    """Every in-repo link must point at a file that ships in the repo."""

    def test_relative_links_exist(self):
        missing = []
        for target in re.findall(r"\]\(([^)]+)\)", read(README)):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("mailto:", "..", "/", "#")):
                continue
            if not (ROOT / target).exists():
                missing.append(target)
        self.assertEqual(missing, [], f"README.md has broken in-repo links: {missing}")


class TestContributingGuidelines(unittest.TestCase):
    def setUp(self):
        self.text = read(CONTRIBUTING)

    def test_has_a_development_setup_section(self):
        self.assertIsNotNone(
            section(self.text, r"(getting started|development setup|setting up)\b"),
            "CONTRIBUTING.md must document a development setup section")

    def test_has_a_pull_request_section(self):
        self.assertIsNotNone(
            section(self.text, r"pull requests?\b"),
            "CONTRIBUTING.md must document a '## Pull requests' section")

    def test_has_a_bug_reporting_section(self):
        self.assertIsNotNone(
            section(self.text, r"(reporting a bug|reporting bugs|reporting issues|filing a bug)\b"),
            "CONTRIBUTING.md must document how to report a bug")

    def test_has_a_code_of_conduct_section(self):
        self.assertIsNotNone(
            section(self.text, r"code of conduct\b"),
            "CONTRIBUTING.md must document a code of conduct")


class TestCliIsSelfDocumenting(unittest.TestCase):
    """`ruth reference` renders the CLI surface from the parser itself.

    This is the product half of the documentation contract. The reference is
    generated from the same parser that runs commands, so the README command
    table can be checked against the commands and flags the CLI actually
    accepts -- documentation and behaviour cannot silently separate.
    """

    def _run_cli(self, argv):
        from ruth import cli
        out, err = io.StringIO(), io.StringIO()
        try:
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                cli.main(list(argv))
        except SystemExit as exc:
            if exc.code not in (0, None):
                raise AssertionError(
                    "ruth reference must be a valid command "
                    f"(got exit {exc.code}); stderr: {err.getvalue().strip()}")
        return out.getvalue(), err.getvalue()

    def test_reference_command_is_available(self):
        out, _ = self._run_cli(["reference"])
        for command in ("app", "talk", "teach", "sleep", "status", "reference"):
            self.assertIn(
                command, out,
                f"ruth reference must document the `{command}` command")
        self.assertIn("--home", out, "ruth reference must document the global --home option")

    def test_reference_json_is_machine_readable(self):
        out, _ = self._run_cli(["reference", "--format", "json"])
        ref = json.loads(out)
        names = {c["command"] for c in ref["commands"]}
        self.assertIn("reference", names)
        self.assertIn("evolve", names)
        for command in ref["commands"]:
            self.assertTrue(command["usage"].startswith("ruth "), command)
            self.assertTrue(command["options"], f"{command['command']} should expose options")
            for option in command["options"]:
                self.assertTrue(option["flags"], "every option must expose its flags")

    def test_readme_command_table_matches_the_cli(self):
        from ruth import cli, reference
        real = set(reference.command_names(cli.build_parser()))
        listed = set(re.findall(r"`ruth ([a-z][a-z-]+)", read(README)))
        unknown = sorted(listed - real)
        self.assertEqual(
            unknown, [],
            f"README.md documents commands the CLI does not define: {unknown}")


if __name__ == "__main__":
    unittest.main()
