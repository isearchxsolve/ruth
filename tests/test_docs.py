"""The documentation is part of the product, so the suite reads it.

The repository ships a README, usage examples, contribution guidelines and a
FAQ, and nothing used to check them, so a promised section could disappear or
rot without any build failing. These tests read the real files and fail when a
documented section is missing, when a Markdown link points at nothing, or when
placeholder text is left behind.

They are stdlib-only and offline: no numpy, no network, so they run on a blank
machine as part of `unittest discover`.
"""
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
CONTRIBUTING = ROOT / "CONTRIBUTING.md"

# Text that means a section was drafted but never written.
PLACEHOLDER = re.compile(
    r"\blorem ipsum\b|\bTODO\b|\bTBD\b|\bFIXME\b|coming soon|write me|"
    r"replace with actual implementation",
    re.I,
)

# A fenced code block opens or closes on a line that is exactly three backticks.
FENCE = "```"


def read(path):
    return path.read_text(encoding="utf-8")


def h2_sections(text):
    """Map every level-2 heading (lower-cased) to its body."""
    sections = {}
    headings = list(re.finditer(r"^##\s+(.+?)\s*$", text, re.M))
    for i, match in enumerate(headings):
        start = match.end()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        sections[match.group(1).strip().lower()] = text[start:end]
    return sections


def find_section(text, *fragments):
    """Body of the first level-2 section whose title contains a fragment."""
    for title, body in h2_sections(text).items():
        if any(fragment.lower() in title for fragment in fragments):
            return body
    return None


class TestReadme(unittest.TestCase):
    """The README is the front door: it must stay complete and honest."""

    def setUp(self):
        self.text = read(README)

    def test_readme_has_a_faq_section(self):
        body = find_section(self.text, "faq", "frequently asked")
        self.assertIsNotNone(
            body,
            "README must include a Frequently Asked Questions (FAQ) section")

    def test_faq_answers_multiple_real_questions(self):
        body = find_section(self.text, "faq", "frequently asked") or ""
        questions = re.findall(r"^###\s+\S.*\?$", body, re.M)
        self.assertGreaterEqual(
            len(questions), 8,
            "the FAQ must answer at least eight questions, each as a '### ...?' heading")

    def test_readme_has_usage_examples(self):
        body = find_section(self.text, "usage example", "examples")
        self.assertIsNotNone(body, "README must include a usage examples section")
        self.assertGreaterEqual(
            body.count(FENCE) // 2, 3,
            "the usage examples must contain at least three fenced code snippets")

    def test_readme_points_at_the_other_documents(self):
        self.assertIn("CONTRIBUTING.md", self.text,
                      "README must link the contribution guidelines")
        self.assertIn("docs/ARCHITECTURE.md", self.text,
                      "README must link the architecture document")

    def test_readme_documents_the_two_ways_in(self):
        for command in ("ruth app", "ruth talk"):
            self.assertIn(command, self.text,
                          f"README must document `{command}`")

    def test_relative_markdown_links_resolve(self):
        """A link to a file that does not exist is a broken front door."""
        missing = []
        for target in re.findall(r"\]\(([^)]+)\)", self.text):
            target = target.split("#", 1)[0].strip()
            if not target or "://" in target or target.startswith(("#", "..")):
                continue
            if target.endswith(".md") and not (ROOT / target).is_file():
                missing.append(target)
        self.assertEqual(missing, [], f"README links to missing files: {missing}")


class TestContributing(unittest.TestCase):
    """Contribution guidelines must actually tell a new contributor what to do."""

    def setUp(self):
        self.text = read(CONTRIBUTING)

    def test_contributing_file_is_not_empty(self):
        self.assertGreater(len(self.text.strip()), 400,
                           "CONTRIBUTING.md is empty or a stub")

    def test_covers_the_full_contribution_workflow(self):
        lowered = self.text.lower()
        expectations = {
            "how to install the package": ("pip install",),
            "how to run the test suite": ("unittest",),
            "a code-style rule": ("style", "line length", "pep 8", "pep8"),
            "how to open a change": ("pull request", "merge request", "pr "),
        }
        for what, needles in expectations.items():
            self.assertTrue(
                any(needle in lowered for needle in needles),
                f"CONTRIBUTING.md must document {what}")

    def test_names_the_two_mirror_points(self):
        """A contributor changing the brain must know about the C mirror."""
        self.assertIn("ruth/csrc/ruth_core.c", self.text)
        self.assertIn("test_token_free.py", self.text)


class TestDocumentationHygiene(unittest.TestCase):
    """Published prose must carry no placeholders and no machine profile."""

    def test_no_placeholder_text_in_published_docs(self):
        for path in (README, CONTRIBUTING):
            found = PLACEHOLDER.findall(read(path))
            self.assertEqual(found, [],
                             f"{path.name} still contains placeholder text: {found}")

    def test_no_absolute_machine_paths(self):
        pattern = re.compile(r"/home/(?!you\b|runner\b|user\b)[A-Za-z0-9_]+/")
        for path in (README, CONTRIBUTING):
            found = pattern.findall(read(path))
            self.assertEqual(found, [],
                             f"{path.name} pins an absolute home path: {found}")


def _load_guide():
    """Load ruth/guide.py as data, without importing the package or numpy."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("ruth_guide", ROOT / "ruth" / "guide.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _cli_available():
    """The shipped CLI needs numpy, her one runtime dependency."""
    import importlib.util
    return importlib.util.find_spec("numpy") is not None


class TestShippedGuideData(unittest.TestCase):
    """`ruth/guide.py` is the terminal's copy of the documentation.

    It is loaded straight from its file so this check needs no numpy and runs
    on a blank machine beside the README checks. The guide is part of the
    product now, not prose that only lives in the repository.
    """

    @classmethod
    def setUpClass(cls):
        cls.guide = _load_guide()

    def test_topics_render_to_real_sections(self):
        self.assertEqual(tuple(self.guide.TOPICS),
                         ("overview", "usage", "faq", "resources"))
        for topic in self.guide.TOPICS:
            self.assertTrue(self.guide.render(topic).strip(), topic)

    def test_the_faq_answers_at_least_eight_questions(self):
        self.assertGreaterEqual(len(self.guide.FAQ), 8)
        for question, answer in self.guide.FAQ:
            self.assertTrue(question.endswith("?"), question)
            self.assertGreater(len(answer.strip()), 20, question)

    def test_usage_examples_name_the_commands_people_start_with(self):
        usage = self.guide.render("usage")
        for command in ("ruth app", "ruth talk", "ruth teach", "ruth say",
                        "ruth think", "ruth sleep", "ruth check"):
            self.assertIn(command, usage)

    def test_a_missing_or_empty_topic_renders_the_whole_guide(self):
        for topic in (None, "", "   ", "\t"):
            whole = self.guide.render(topic)
            self.assertIn("RUTH QUICK REFERENCE", whole, repr(topic))
            self.assertIn("FREQUENTLY ASKED QUESTIONS", whole, repr(topic))

    def test_a_topic_is_trimmed_and_case_folded(self):
        self.assertEqual(self.guide.render(" FAQ "), self.guide.render("faq"))

    def test_an_unknown_topic_is_a_clear_error(self):
        with self.assertRaises(ValueError):
            self.guide.render("nope")

    def test_the_whole_guide_contains_every_section(self):
        whole = self.guide.render()
        for heading in ("OVERVIEW", "USAGE", "FREQUENTLY ASKED QUESTIONS",
                        "WHERE TO READ MORE"):
            self.assertIn(heading, whole)


@unittest.skipUnless(_cli_available(), "the CLI needs numpy, her runtime dependency")
class TestInProductGuide(unittest.TestCase):
    """The real entry point must expose the guide, not just the data module."""

    def _ruth(self, *argv, env=None):
        import os
        import subprocess
        import sys
        full_env = dict(os.environ)
        if env:
            full_env.update(env)
        return subprocess.run([sys.executable, "-m", "ruth", *argv],
                              capture_output=True, text=True, timeout=180,
                              env=full_env)

    def test_help_points_at_the_shipped_guide(self):
        done = self._ruth("--help")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("ruth guide", done.stdout)

    def test_guide_prints_every_section(self):
        done = self._ruth("guide")
        self.assertEqual(done.returncode, 0, done.stderr)
        for heading in ("OVERVIEW", "USAGE", "FREQUENTLY ASKED QUESTIONS"):
            self.assertIn(heading, done.stdout)

    def test_guide_faq_answers_at_least_eight_questions(self):
        done = self._ruth("guide", "faq")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertGreaterEqual(done.stdout.count("Q:"), 8)

    def test_guide_usage_names_the_two_ways_in(self):
        done = self._ruth("guide", "usage")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("ruth app", done.stdout)
        self.assertIn("ruth talk", done.stdout)

    def test_guide_needs_no_brain_and_no_lock(self):
        import tempfile
        with tempfile.TemporaryDirectory() as home:
            done = self._ruth("guide", "overview", env={"RUTH_HOME": home})
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn("OVERVIEW", done.stdout)

    def test_an_unknown_guide_topic_is_refused(self):
        done = self._ruth("guide", "nope")
        self.assertNotEqual(done.returncode, 0)
        self.assertIn("invalid choice", done.stderr)


if __name__ == "__main__":
    unittest.main()
