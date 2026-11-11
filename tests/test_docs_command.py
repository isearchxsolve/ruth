"""Regression tests for the `ruth docs` product feature (issue #6).

The documentation bounty is not only prose: the product must be able to read
and check the documentation it ships. These tests drive `ruth/docs.py` and the
`docs` subcommand directly -- no mind, no network, no TTY -- and then try to
break the read-only path from several threads at once, because `ruth docs` is
meant to be safe to run while `ruth app` owns her.

They fail on the unpatched tree (there is no `ruth.docs` module) and pass once
the command exists, which is what makes them the regression test for the fix.
"""
import contextlib
import io
import json
import os
import shutil
import tempfile
import threading
import unittest
from unittest import mock

from ruth import docs
import ruth.cli as cli

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
README = os.path.join(ROOT, "README.md")
CONTRIBUTING = os.path.join(ROOT, "CONTRIBUTING.md")
ARCHITECTURE = os.path.join(ROOT, "docs", "ARCHITECTURE.md")


def readme_text():
    with open(README, encoding="utf-8") as handle:
        return handle.read()


def run(*argv):
    """Run ``cli.main(argv)`` and capture (exit code, stdout, stderr).

    `main` returns None on success and raises SystemExit on failure, exactly as
    a real terminal would see it.
    """
    out, err = io.StringIO(), io.StringIO()
    code = 0
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            result = cli.main(list(argv))
        except SystemExit as exc:
            code = exc.code if isinstance(exc.code, int) else 1
        else:
            assert result is None, "main() should not return a value"
    return code, out.getvalue(), err.getvalue()


class TestLocate(unittest.TestCase):
    def test_finds_the_repository_documents(self):
        root = docs.resolve_root()
        self.assertEqual(os.path.abspath(root), ROOT)
        for rel in ("README.md", "CONTRIBUTING.md"):
            self.assertTrue(os.path.isfile(os.path.join(root, rel)), rel)

    def test_explicit_directory_is_validated(self):
        with tempfile.TemporaryDirectory() as empty:
            with self.assertRaises(docs.DocsNotFound):
                docs.resolve_root(empty)
            for name in ("README.md", "CONTRIBUTING.md"):
                with open(os.path.join(empty, name), "w", encoding="utf-8") as f:
                    f.write("# x\n")
            self.assertEqual(docs.resolve_root(empty), os.path.abspath(empty))

    def test_environment_override_is_honoured(self):
        with mock.patch.dict(os.environ, {"RUTH_DOCS_DIR": ROOT}):
            self.assertEqual(os.path.abspath(docs.resolve_root()), ROOT)


class TestReading(unittest.TestCase):
    def test_index_lists_every_topic(self):
        text = docs.index()
        for name in ("readme", "contributing", "architecture"):
            self.assertIn(name, text)
        self.assertIn("FAQ", text)

    def test_readme_and_its_aliases_read_the_shipped_documents(self):
        faq = docs.document("faq")
        self.assertTrue(faq.startswith("## FAQ"), faq[:20])
        usage = docs.document("usage")
        self.assertTrue(usage.startswith("## Usage examples"), usage[:30])

    def test_section_lookup_is_case_insensitive(self):
        body = docs.document("readme", "honest status")
        self.assertTrue(body.startswith("## Honest status"), body[:30])

    def test_unknown_topic_raises(self):
        with self.assertRaises(docs.DocsError):
            docs.document("does-not-exist")

    def test_unknown_section_names_the_alternatives(self):
        with self.assertRaises(docs.SectionNotFound) as caught:
            docs.document("readme", "no such section")
        self.assertIn("Honest status", str(caught.exception))

    def test_null_and_empty_arguments_do_not_crash(self):
        self.assertIn("README.md", docs.document(None))          # index
        self.assertIsNone(docs.find_section(readme_text(), ""))
        self.assertIsNone(docs.find_section(readme_text(), None))
        # an empty section string means "the whole document", never a crash
        self.assertEqual(docs.document("readme", ""), docs.document("readme"))

    def test_faq_keeps_its_own_subsections(self):
        faq = docs.find_section(readme_text(), "FAQ")
        self.assertIsNotNone(faq)
        questions = [ln for ln in faq.body.splitlines()
                     if ln.startswith("###") and ln.rstrip().endswith("?")]
        self.assertGreaterEqual(len(questions), 8)

    def test_payload_is_structured(self):
        payload = docs.payload("readme", "FAQ")
        self.assertEqual(payload["topic"], "readme")
        self.assertEqual(payload["section"], "FAQ")
        self.assertEqual(payload["level"], 2)
        self.assertIn("text", payload)
        index = docs.payload()
        self.assertIn("topics", index)
        self.assertEqual([t["name"] for t in index["topics"]],
                         ["readme", "contributing", "architecture"])


class TestAudit(unittest.TestCase):
    def test_the_shipped_documentation_satisfies_the_contract(self):
        self.assertEqual(docs.audit(), [])

    def test_audit_reports_a_missing_faq(self):
        """The checker must catch the exact regression the issue is about."""
        body = readme_text()
        start, end = body.index("## FAQ"), body.index("## Honest status")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
                f.write(body[:start] + body[end:])
            shutil.copy(CONTRIBUTING, os.path.join(d, "CONTRIBUTING.md"))
            os.makedirs(os.path.join(d, "docs"))
            shutil.copy(ARCHITECTURE, os.path.join(d, "docs", "ARCHITECTURE.md"))
            problems = docs.audit(d)
        self.assertTrue(any("FAQ" in p for p in problems), problems)

    def test_flat_install_layout_is_tolerated(self):
        """A build that drops the docs/ subfolder must still be readable."""
        with tempfile.TemporaryDirectory() as d:
            shutil.copy(README, os.path.join(d, "README.md"))
            shutil.copy(CONTRIBUTING, os.path.join(d, "CONTRIBUTING.md"))
            shutil.copy(ARCHITECTURE, os.path.join(d, "ARCHITECTURE.md"))
            self.assertEqual(docs.audit(d), [])
            self.assertGreater(len(docs.document("architecture", root=d)), 2000)


class TestCli(unittest.TestCase):
    def test_index_prints_a_table(self):
        code, out, err = run("docs")
        self.assertEqual(code, 0, err)
        self.assertIn("README.md", out)
        self.assertEqual(err, "")

    def test_faq_and_usage_aliases_print_the_readme_sections(self):
        code, out, _ = run("docs", "faq")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("## FAQ"), out[:20])
        code, out, _ = run("docs", "usage")
        self.assertEqual(code, 0)
        self.assertTrue(out.startswith("## Usage examples"), out[:30])

    def test_json_is_parseable(self):
        code, out, _ = run("docs", "readme", "FAQ", "--json")
        self.assertEqual(code, 0)
        payload = json.loads(out)
        self.assertEqual(payload["section"], "FAQ")
        code, out, _ = run("docs", "--json")
        self.assertEqual(code, 0)
        self.assertIn("Usage examples", out)
        self.assertEqual(json.loads(out)["topics"][0]["name"], "readme")

    def test_check_passes_on_the_shipped_docs(self):
        code, out, _ = run("docs", "--check")
        self.assertEqual(code, 0)
        self.assertTrue(json.loads(out)["ok"])

    def test_unknown_topic_exits_two_with_a_diagnostic(self):
        code, out, err = run("docs", "nonsense")
        self.assertEqual(code, 2)
        self.assertIn("ruth docs:", err)
        self.assertIn("unknown documentation topic", err)

    def test_bad_dir_exits_two_with_a_diagnostic(self):
        with tempfile.TemporaryDirectory() as empty:
            code, out, err = run("docs", "--dir", empty)
            self.assertEqual(code, 2)
            self.assertIn("ruth docs:", err)

    def test_check_exits_one_when_the_contract_is_broken(self):
        body = readme_text()
        start, end = body.index("## FAQ"), body.index("## Honest status")
        with tempfile.TemporaryDirectory() as d:
            with open(os.path.join(d, "README.md"), "w", encoding="utf-8") as f:
                f.write(body[:start] + body[end:])
            shutil.copy(CONTRIBUTING, os.path.join(d, "CONTRIBUTING.md"))
            os.makedirs(os.path.join(d, "docs"))
            shutil.copy(ARCHITECTURE, os.path.join(d, "docs", "ARCHITECTURE.md"))
            code, out, _ = run("docs", "--check", "--dir", d)
        self.assertEqual(code, 1)
        self.assertFalse(json.loads(out)["ok"])


class TestConcurrency(unittest.TestCase):
    def test_parallel_reads_are_consistent_and_never_mix_documents(self):
        """`ruth docs` must be safe to call many times at once (it is read-only
        and shares no mutable state); every thread must see the same FAQ."""
        reads, errors = [], []
        start = threading.Barrier(8)

        def worker():
            try:
                start.wait(timeout=10)
                for _ in range(25):
                    faq = docs.document("faq")
                    reads.append((faq.startswith("## FAQ"),
                                  "## Honest status" not in faq,
                                  docs.document("contributing").startswith(
                                      "# Contributing")))
            except Exception as exc:            # pragma: no cover - asserted below
                errors.append(repr(exc))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join(timeout=30)
        self.assertEqual(errors, [])
        self.assertEqual(len(reads), 8 * 25)
        self.assertEqual(set(reads), {(True, True, True)})


if __name__ == "__main__":
    unittest.main()
