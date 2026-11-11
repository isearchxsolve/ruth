"""Documentation contract: README, usage examples, contribution guide, FAQ.

Issue #7 asks for a comprehensive README, usage examples, contribution
guidelines and a FAQ section. Those live in the product docs, so they are
covered by the same suite that covers the code: a change that drops a section,
empties the FAQ or stops linking the guides fails here instead of being noticed
by a reader. The check reads the real files and needs nothing beyond the
standard library, so it runs on every platform CI targets.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"
LICENSE = ROOT / "LICENSE"
FAQ = ROOT / "FAQ.md"

README_HEADINGS = ("what makes her different", "how she works", "using ruth")


def read(path: pathlib.Path) -> str:
    return path.read_text(encoding="utf-8")


def level_two_headings(md: str):
    """The `## ...` section titles, in document order."""
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", md, re.M)]


def fenced_blocks(md: str):
    return re.findall(r"```[^\n]*\n(.*?)```", md, re.S)


def section(md: str, name: str) -> str:
    """The body of the level-two section `name` (case-insensitive)."""
    out, capturing = [], False
    for line in md.splitlines():
        if re.match(r"^##\s+", line):
            capturing = re.sub(r"^##\s+", "", line).strip().lower() == name.lower()
            continue
        if capturing and re.match(r"^#\s+", line):  # a top-level heading ends it
            break
        if capturing:
            out.append(line)
    return "\n".join(out)


class TestReadmeIsComprehensive(unittest.TestCase):
    def setUp(self):
        self.assertTrue(README.exists(), "README.md must exist")
        self.body = read(README)

    def test_readme_covers_the_project(self):
        self.assertGreater(len(self.body), 3000,
                           "README must be a comprehensive overview, not a stub")
        for word in ("ruth", "install", "license"):
            self.assertIn(word, self.body.lower(),
                          f"README must mention {word!r}")

    def test_readme_keeps_the_core_sections(self):
        headings = [h.lower() for h in level_two_headings(self.body)]
        for wanted in README_HEADINGS:
            self.assertIn(wanted, headings,
                          f"README must keep the {wanted!r} section")

    def test_readme_has_a_faq_section(self):
        has_heading = "faq" in [h.lower() for h in level_two_headings(self.body)]
        if not (has_heading or FAQ.exists()):
            self.fail("an FAQ section must exist: a '## FAQ' heading in "
                      "README.md or a FAQ.md file")

    def test_readme_shows_runnable_usage_examples(self):
        runnable = [b for b in fenced_blocks(self.body)
                    if re.search(r"^\s*(?:ruth\s|python -m pip|sh install)", b, re.M)]
        self.assertGreaterEqual(
            len(runnable), 2,
            "README must contain usage examples with runnable commands")

    def test_faq_answers_multiple_questions(self):
        body = read(FAQ) if FAQ.exists() else section(self.body, "faq")
        self.assertTrue(body.strip(), "the FAQ section must not be empty")
        self.assertGreaterEqual(
            body.count("?"), 4,
            "the FAQ section must answer at least four questions")

    def test_readme_points_to_the_contribution_guide(self):
        self.assertIn(
            "CONTRIBUTING.md", self.body,
            "README must link to the contribution guidelines")

    def test_readme_states_the_license(self):
        self.assertIn("LICENSE", self.body, "README must link the license")


class TestContributionGuide(unittest.TestCase):
    def setUp(self):
        self.assertTrue(CONTRIBUTING.exists(), "CONTRIBUTING.md must exist")
        self.body = read(CONTRIBUTING)

    def test_guide_explains_the_workflow(self):
        self.assertIn("python -m unittest", self.body,
                      "the guide must show how to run the test suite")

    def test_guide_describes_the_pull_request_process(self):
        self.assertRegex(self.body, r"(?i)pull request",
                         "the guide must describe how to propose a change")

    def test_guide_is_substantial(self):
        self.assertGreater(len(self.body), 1800,
                           "contribution guidelines must be more than a stub")


class TestLicense(unittest.TestCase):
    def test_license_exists(self):
        self.assertTrue(LICENSE.exists(), "LICENSE must exist")


if __name__ == "__main__":
    unittest.main()
