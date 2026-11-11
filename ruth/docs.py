"""`ruth docs` -- read and check the project's own documentation, offline.

The README, the contribution guide and the architecture notes are part of the
product (issue #6), so they ship with the code and must be readable without a
network connection. This module finds those files -- next to the package, in the
working tree, or wherever ``RUTH_DOCS_DIR`` points -- turns them into navigable
sections and audits them, so the shipped documentation can be checked on every
build the same way code is.

Nothing here imports a mind, opens a socket or touches Ruth's state, so
``ruth docs`` works while ``ruth app`` is awake and owns her.
"""
from __future__ import annotations

import dataclasses
import os
import re
import sys

# The documents that make up the shipped documentation, in reading order.
TOPICS = {
    "readme": "README.md",
    "contributing": "CONTRIBUTING.md",
    "architecture": os.path.join("docs", "ARCHITECTURE.md"),
}

# Convenience aliases: the two deliverables of the issue -- the usage examples
# and the FAQ -- live inside the README, and a reader asks for them by name.
ALIASES = {
    "faq": ("readme", "FAQ"),
    "faqs": ("readme", "FAQ"),
    "usage": ("readme", "Usage examples"),
    "examples": ("readme", "Usage examples"),
}

# A folder is a documentation root when it carries the entry-point documents.
_MARKERS = ("README.md", "CONTRIBUTING.md")
_HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
_CODE_FENCE = re.compile(r"^\s*```")
_RUNNABLE = re.compile(r"^\s*\$?\s*ruth\s+\S+", re.M)
_QUESTION = re.compile(r"^#{3,4}\s+.*\?\s*$", re.M)
_SECTION_WORD = re.compile(r"\b(reporting bugs|bug reports)\b", re.I)
_UPDATE = re.compile(r"(?im)^#{1,6}\s+.*\bpull request\b")


class DocsError(Exception):
    """The documentation could not be read, or the request could not be met."""


class DocsNotFound(DocsError):
    """The shipped documentation could not be located on this machine."""


class SectionNotFound(DocsError):
    """No section of a document matched the requested title."""


@dataclasses.dataclass(frozen=True)
class Section:
    """One Markdown heading and the body under it, up to the next peer."""

    level: int
    title: str
    body: str

    def render(self) -> str:
        """The section as it appears in the document, ready to print."""
        heading = "#" * self.level + " " + self.title
        body = self.body.strip("\n")
        return (heading + ("\n\n" + body if body else "")).rstrip() + "\n"


# ------------------------------------------------------------------ locating
def _walk_up(start):
    """Yield ``start`` and its parents, so a nested checkout still matches."""
    path = os.path.abspath(start)
    while True:
        yield path
        parent = os.path.dirname(path)
        if parent == path:
            return
        path = parent


def _is_root(path):
    return all(os.path.isfile(os.path.join(path, marker)) for marker in _MARKERS)


def _search_starts():
    """Places to look for the docs, most specific first."""
    starts = []
    seen = set()

    def add(path):
        if path and path not in seen:
            seen.add(path)
            starts.append(path)

    # next to the installed package (source checkout and editable installs)
    here = os.path.dirname(os.path.abspath(__file__))
    add(here)
    add(os.path.dirname(here))
    # the tree the command was run from
    add(os.getcwd())
    # a wheel/bundle installs the documents under <prefix>/share
    prefixes = [sys.prefix, getattr(sys, "base_prefix", sys.prefix)]
    for prefix in prefixes:
        add(os.path.join(prefix, "share", "ruth"))
        add(os.path.join(prefix, "share", "doc", "ruth"))
    return starts


def resolve_root(explicit=None):
    """Return the folder that holds the shipped documents.

    ``explicit`` (or ``RUTH_DOCS_DIR``) is honoured first and validated, so a
    typo is reported instead of silently ignored. Without one, the package file,
    the working directory and the install prefix are searched, closest first.
    """
    explicit = explicit or os.environ.get("RUTH_DOCS_DIR")
    if explicit:
        root = os.path.abspath(explicit)
        if not _is_root(root):
            raise DocsNotFound(
                f"{root} is not a Ruth documentation folder "
                "(README.md and CONTRIBUTING.md are missing)")
        return root
    for start in _search_starts():
        for path in _walk_up(start):
            if _is_root(path):
                return path
    raise DocsNotFound(
        "the shipped documentation (README.md, CONTRIBUTING.md) was not found; "
        "run ruth from the project directory or set RUTH_DOCS_DIR to the folder "
        "that holds them")


def _read_file(root, rel):
    """Read a document, tolerating a flat install that dropped its subfolder.

    A source tree keeps ``docs/ARCHITECTURE.md``; a build that flattens the
    install could leave ``ARCHITECTURE.md`` beside the README, so both spellings
    are tried before the file is called missing.
    """
    errors = []
    for candidate in (rel, os.path.basename(rel)):
        path = os.path.join(root, candidate)
        try:
            with open(path, encoding="utf-8") as handle:
                return handle.read()
        except OSError as exc:
            errors.append(str(exc))
    raise DocsNotFound(f"cannot read {os.path.join(root, rel)}: {errors[-1]}")


# ------------------------------------------------------------------ sections
def parse_sections(text):
    """Every heading in ``text`` with the body under it.

    A section's body runs until the next heading of the same or a higher level,
    so a ``##`` section keeps its own ``###`` subsections -- which is what makes
    ``ruth docs faq`` print all of the answers, not just the first.
    """
    lines = text.splitlines()
    sections = []
    for i, line in enumerate(lines):
        match = _HEADING.match(line)
        if not match:
            continue
        level = len(match.group(1))
        body = []
        for later in lines[i + 1:]:
            following = _HEADING.match(later)
            if following and len(following.group(1)) <= level:
                break
            body.append(later)
        sections.append(Section(level=level, title=match.group(2).strip(),
                                body="\n".join(body).strip("\n")))
    return sections


def find_section(text, query):
    """The first section whose title equals, then merely contains, ``query``."""
    wanted = (query or "").strip().lower()
    if not wanted:
        return None
    sections = parse_sections(text)
    for section in sections:
        if section.title.lower() == wanted:
            return section
    for section in sections:
        if wanted in section.title.lower():
            return section
    return None


def _resolve_topic(topic):
    """Map a topic or alias to ``(topic, relative path, forced section)``."""
    key = (topic or "").strip().lower()
    if key in TOPICS:
        return key, TOPICS[key], None
    if key in ALIASES:
        base, section = ALIASES[key]
        return base, TOPICS[base], section
    raise DocsError("unknown documentation topic %r; choose from %s"
                    % (topic, ", ".join(TOPICS)))


# ------------------------------------------------------------------ reading
def _topic_index(root):
    entries = []
    for name, rel in TOPICS.items():
        entry = {"name": name, "path": rel, "sections": []}
        try:
            text = _read_file(root, rel)
        except DocsNotFound:
            entry["missing"] = True
        else:
            entry["sections"] = [s.title for s in parse_sections(text)
                                 if s.level == 2]
        entries.append(entry)
    return entries


def index(root=None):
    """A short table of contents for everything that is shipped."""
    root = resolve_root(root)
    lines = ["Ruth documentation in " + root, ""]
    for entry in _topic_index(root):
        state = "  (missing)" if entry.get("missing") else ""
        lines.append("  %-13s %s%s" % (entry["name"], entry["path"], state))
        for title in entry["sections"]:
            lines.append("      - " + title)
    lines.append("")
    lines.append("Read a topic:  ruth docs <topic> [section]")
    lines.append("Aliases:       " + ", ".join(sorted(ALIASES)))
    return "\n".join(lines).rstrip() + "\n"


def payload(topic=None, section=None, root=None):
    """The structured form of a request: a topic index, or one document."""
    root = resolve_root(root)
    if topic is None:
        return {"root": root, "topics": _topic_index(root)}
    base, rel, alias_section = _resolve_topic(topic)
    text = _read_file(root, rel)
    wanted = section or alias_section
    if wanted:
        found = find_section(text, wanted)
        if found is None:
            titles = ", ".join(s.title for s in parse_sections(text))
            raise SectionNotFound(
                "%s has no section matching %r; sections: %s"
                % (rel, wanted, titles))
        return {"root": root, "topic": base, "path": rel,
                "section": found.title, "level": found.level,
                "text": found.render()}
    if not text.endswith("\n"):
        text += "\n"
    return {"root": root, "topic": base, "path": rel, "section": None,
            "text": text}


def document(topic=None, section=None, root=None):
    """The text to print for a request; the index when no topic is given."""
    if topic is None:
        return index(root=root)
    return payload(topic, section, root=root)["text"]


# ------------------------------------------------------------------ checking
def audit(root=None):
    """Return the documentation contract violations, or ``[]`` when clean.

    This is the issue's checklist as code: a comprehensive README with
    installation on every platform, a usage-examples section, a FAQ, links to
    the contribution guide and the architecture notes, and a contribution guide
    with the test workflow and the pull-request process. ``ruth docs --check``
    exits non-zero while this list is non-empty.
    """
    root = resolve_root(root)
    problems = []

    def note(condition, message):
        if not condition:
            problems.append(message)

    readme = _read_file(root, TOPICS["readme"])
    note(len(readme) > 2000, "README.md is too short to be comprehensive")
    for needle in ("install.sh", "install.ps1", "python -m pip install", "3.9"):
        note(needle in readme,
             "README.md must document installation (%s)" % needle)
    usage = find_section(readme, "usage examples")
    note(usage is not None,
         "README.md must contain a Usage examples section")
    note(usage is not None and len(_RUNNABLE.findall(usage.body)) >= 6,
         "README.md usage examples must show at least six runnable ruth commands")
    faq = find_section(readme, "FAQ")
    note(faq is not None, "README.md must contain a FAQ section")
    note(faq is not None and len(_QUESTION.findall(faq.body)) >= 8,
         "README.md FAQ must answer at least eight questions")
    note("CONTRIBUTING.md" in readme, "README.md must link to CONTRIBUTING.md")
    note("docs/ARCHITECTURE.md" in readme,
         "README.md must link to docs/ARCHITECTURE.md")
    note(len(_CODE_FENCE.findall(readme)) % 2 == 0,
         "README.md has an unclosed code fence")

    contributing = _read_file(root, TOPICS["contributing"])
    note(_SECTION_WORD.search(contributing) is not None,
         "CONTRIBUTING.md must contain a Reporting bugs section")
    note(_UPDATE.search(contributing) is not None,
         "CONTRIBUTING.md must contain a Pull request process section")
    note("[ ]" in contributing,
         "CONTRIBUTING.md pull request process must include a checklist")
    note("unittest discover" in contributing,
         "CONTRIBUTING.md must document how to run the tests")
    note("pip install -e" in contributing,
         "CONTRIBUTING.md must document the editable install")

    try:
        architecture = _read_file(root, TOPICS["architecture"])
    except DocsNotFound:
        problems.append("docs/ARCHITECTURE.md is missing")
    else:
        note(len(architecture) > 2000,
             "docs/ARCHITECTURE.md is too short to be the research reference")

    return problems
