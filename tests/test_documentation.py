"""The documentation contract for issue #6.

The project must ship a comprehensive README (installation, usage examples and
a FAQ), contribution guidelines that cover the test workflow, the pull request
process and bug reporting, and links that let a newcomer get from clone to a
running test without guessing.

These tests read the shipped Markdown only. They never import the package, open
a socket or touch Ruth's state, so they are safe to run anywhere and they fail
the build when a document regresses the same way a code test would.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
ARCHITECTURE = ROOT / "docs" / "ARCHITECTURE.md"

_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")


def read(path):
    """Read a document, or return "" when it is missing (the test asserts)."""
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def find_section(text, title_pattern):
    """Body of the first heading whose text matches ``title_pattern``, or None.

    The body runs until the next heading of the same or a higher level, so a
    section's own subsections are included. Titles are matched case-insensitively
    against the heading text with the leading hashes removed.
    """
    lines = text.splitlines()
    pattern = re.compile(title_pattern, re.I)
    for i, line in enumerate(lines):
        m = _HEADING.match(line)
        if not m or not pattern.search(m.group(2)):
            continue
        level = len(m.group(1))
        body = []
        for later in lines[i + 1:]:
            m2 = _HEADING.match(later)
            if m2 and len(m2.group(1)) <= level:
                break
            body.append(later)
        return "\n".join(body)
    return None


class TestReadme(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(README)

    def test_readme_exists(self):
        self.assertTrue(README.is_file(), "README.md is missing")
        self.assertGreater(len(self.text), 2000,
                           "README.md is too short to be comprehensive")

    def test_readme_documents_installation_on_every_platform(self):
        for needle in ("install.sh", "install.ps1", "python -m pip install", "3.9"):
            self.assertIn(needle, self.text,
                          f"README.md must document installation ({needle})")

    def test_readme_has_a_usage_examples_section(self):
        body = find_section(self.text, r"usage examples?")
        self.assertTrue(body is not None,
                        "README.md must contain a Usage examples section")
        commands = re.findall(r"^\s*\$?\s*ruth\s+\S+", body or "", re.M)
        self.assertGreaterEqual(
            len(commands), 6,
            "README.md usage examples must show at least six runnable "
            "ruth commands")

    def test_readme_has_a_faq_section(self):
        body = find_section(self.text, r"faq|frequently asked questions")
        self.assertTrue(body is not None,
                        "README.md must contain a FAQ section")
        questions = re.findall(r"^#{3,4}\s+.*\?\s*$", body or "", re.M)
        self.assertGreaterEqual(
            len(questions), 8,
            "README.md FAQ must answer at least eight questions")

    def test_readme_links_to_contributing_and_architecture(self):
        self.assertIn("CONTRIBUTING.md", self.text,
                      "README.md must link to CONTRIBUTING.md")
        self.assertIn("docs/ARCHITECTURE.md", self.text,
                      "README.md must link to docs/ARCHITECTURE.md")

    def test_readme_code_fences_are_balanced(self):
        fences = re.findall(r"^\s*```", self.text, re.M)
        self.assertEqual(len(fences) % 2, 0,
                         "README.md has an unclosed code fence")


class TestContributing(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = read(CONTRIBUTING)

    def test_contributing_documents_bug_reporting(self):
        body = find_section(self.text, r"reporting bugs|bug reports")
        self.assertTrue(body is not None,
                        "CONTRIBUTING.md must contain a Reporting bugs section")

    def test_contributing_documents_the_pull_request_process(self):
        body = find_section(self.text, r"pull request")
        self.assertTrue(body is not None,
                        "CONTRIBUTING.md must contain a Pull request process "
                        "section")
        self.assertIn("[ ]", body or "",
                      "CONTRIBUTING.md pull request process must include a "
                      "checklist")

    def test_contributing_documents_the_test_workflow(self):
        self.assertIn("unittest discover", self.text,
                      "CONTRIBUTING.md must document how to run the tests")
        self.assertIn("pip install -e", self.text,
                      "CONTRIBUTING.md must document the editable install")

    def test_contributing_exists(self):
        self.assertTrue(CONTRIBUTING.is_file(), "CONTRIBUTING.md is missing")

    def test_contributing_keeps_the_design_principles(self):
        for principle in ("Token-free", "Self-contained",
                          "Security is her judgment", "Measured, not assumed"):
            self.assertIn(principle, self.text,
                          f"CONTRIBUTING.md must keep the {principle} principle")


class TestDocsTree(unittest.TestCase):
    def test_architecture_document_exists(self):
        self.assertTrue(ARCHITECTURE.is_file(),
                        "docs/ARCHITECTURE.md is missing")
        self.assertGreater(len(read(ARCHITECTURE)), 2000,
                           "docs/ARCHITECTURE.md is too short to be the "
                           "research reference")


if __name__ == "__main__":
    unittest.main()
