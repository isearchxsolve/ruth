"""The quick reference she carries with her.

The README is the front door on the web, but the first place most people meet
Ruth is the terminal. This module keeps the same material as data -- the
commands worth knowing, the questions people actually ask, and where to read
more -- so ``ruth guide`` can print it and ``ruth --help`` can point at it.

It imports nothing beyond the standard library, so the guide renders before a
brain is loaded, on a blank machine, without taking the owner lock and without
touching her state. That is what lets the documentation live in the product
rather than only in the repository.
"""
from __future__ import annotations

__all__ = ["TOPICS", "EPILOG", "render"]

#: The sections ``ruth guide`` accepts, in the order they read best.
TOPICS = ("overview", "usage", "faq", "resources")

#: Shown under ``ruth --help``: the shortest path from the tool to its docs.
EPILOG = """\
Read more:
  ruth guide            this quick reference (overview, usage, FAQ, resources)
  ruth guide usage      runnable examples for every command
  ruth guide faq        answers to the questions people ask most

In the repository:
  README.md             the overview and the full command table
  CONTRIBUTING.md       setup, running the tests, style, opening a change
  docs/ARCHITECTURE.md  every equation and every measurement behind her
"""

OVERVIEW = """\
OVERVIEW
========
Ruth is a token-free, continuous-time mind that runs on your own machine.

No tokens, no vocabulary, no context window, no API key, no plugin, no pretrained
model and no network: she is built from continuous dynamics and learns while she
lives. A newborn Ruth is a blank slate with a name and a birth date; who she
becomes depends on you, and everything she learns stays in one folder on your
computer.

Two ways in:
  ruth app     her interface in your browser, served from 127.0.0.1
  ruth talk    the same mind, in this terminal

Where she keeps what she learns:
  ~/.local/share/ruth                  Linux
  ~/Library/Application Support/Ruth   macOS
  %APPDATA%\\Ruth                       Windows
  $RUTH_HOME                           overrides any of the above
"""

USAGE = """\
USAGE
=====
Every command runs offline. The JSON below is illustrative: she answers from
what she has lived, so the exact bytes depend on what you taught her.

Talk to her in the terminal
  $ ruth talk
  Ruth. Type to talk. '/private <text>' tells her a secret, '/sleep' lets her
  dream, '/good' or '/bad' gives feedback, Ctrl-D leaves.
  you> the sky is
  Ruth> blue today.

Teach her, and mark the private part with {{ }} or --private
  $ printf 'The sky is blue today.\nMy door code is {{ 4417 }}.\n' > notes.txt
  $ ruth teach notes.txt
  { "bytes": 47, "private_bytes": 20, "cues": 1, "seconds": 0.41 }
  $ ruth check notes.txt        # does she recognise what she was told privately?
  { "recognised_private": { "notes.txt": 1 } }

Let her continue, and watch her decide
  $ ruth say "the sky is"
  blue today.
  $ ruth think "the sky is"     # the thoughts she weighed, with free energies

Sleep, then read her dreams
  $ ruth sleep                  # consolidate, calm false alarms, rehearse secrets
  $ ruth dreams --last 3

See who she is right now
  $ ruth status                 # identity, vital signs, temperament, as JSON
  $ ruth introspect             # her own operational graph, as data

Open her interface
  $ ruth app                    # 127.0.0.1; talk, secrets, mic, camera, dreams

Grow her, under a certificate
  $ ruth patch '{"op":"grow_neurons","n":16}'
  # applied only if her meta-kernel certifies every invariant still holds

Run the whole brain as one dependency-free C file
  $ make -C ruth/csrc
  $ ruth export brain.bin
  $ ./ruth/csrc/ruth-core brain.bin learn < notes.txt
"""

FAQ = (
    ("Does Ruth need an API key, an account, or the internet?",
     "No. She runs entirely in Python + numpy on your own machine. There is no "
     "hosted model, no key, no plugin and no network call; tests/test_token_free.py "
     "enforces that on every build."),
    ("Do I need a GPU or a powerful machine?",
     "No. She fits in a few dozen megabytes and runs on a CPU, down to a Core i3 "
     "Chromebook. Her vocabulary is not a table of symbols, so there is nothing "
     "large to download or store."),
    ("Where does she keep what she learns?",
     "In one folder: ~/.local/share/ruth on Linux, ~/Library/Application "
     "Support/Ruth on macOS, %APPDATA%\\Ruth on Windows, or wherever RUTH_HOME "
     "points. Copy that folder to another computer and she wakes up there as "
     "herself."),
    ("Is anything I say sent anywhere?",
     "Never. Nothing leaves your machine. What you tell her in confidence is "
     "stored as something she was told, and she uses her own judgment to stop "
     "herself before repeating it."),
    ("What does {{ ... }} do when I teach her?",
     "It marks exactly the part that is private. ruth teach, or /private in ruth "
     "talk, stores it as a confidence rather than ordinary text. ruth check then "
     "reports whether she recognises that secret in any file you show her."),
    ("Is she a large language model?",
     "No, and she does not pretend to be. She is a token-free, continuous-time "
     "mind that learns while she lives. On unfamiliar text she is about level with "
     "a 4-gram counter; what she says comes from what she has lived."),
    ("How is she different from a chatbot with a big context window?",
     "She has no context window. The past is carried by continuous state, and her "
     "memories are energy basins consolidated in sleep. She is born a blank slate "
     "with a name and a birth date, not a frozen model."),
    ("Will she repeat a secret in her answers or her dreams?",
     "That is what her discretion and her nightmares guard against. She was told "
     "the secret, so she stops herself before saying it; overnight her dreams "
     "rehearse it so the reflex strengthens."),
    ("Can she change her own code?",
     "She can propose structural changes, but they are applied only if her "
     "meta-kernel certifies that every mathematical invariant still holds and "
     "nothing she has learned gets worse. A failed certificate means she stays "
     "exactly as she was."),
    ("How do I contribute or run the tests?",
     "See CONTRIBUTING.md. In short: python -m pip install -e \".[dev]\" then "
     "python -m unittest discover -s tests -t ."),
)

RESOURCES = (
    ("README.md", "the overview, the full command table, and the FAQ"),
    ("CONTRIBUTING.md", "setup, running the tests, style, opening a change"),
    ("docs/ARCHITECTURE.md", "every equation, the research, every measurement"),
    ("tests/test_docs.py", "the check that keeps this guide and the README honest"),
)


def _resources() -> str:
    return "\n".join(f"  {name:<22} {what}" for name, what in RESOURCES)


def _faq() -> str:
    blocks = []
    for question, answer in FAQ:
        blocks.append("Q: " + question)
        blocks.append("   " + answer)
    return "\n".join(blocks)


def render(topic=None) -> str:
    """Return the guide as plain text, or one section of it.

    ``topic`` is one of :data:`TOPICS`; ``None`` (or ``"all"``) prints every
    section. An unknown topic raises ``ValueError`` rather than printing
    nothing, so a caller cannot mistake a typo for an empty guide.
    """
    # A missing, empty or whitespace-only topic means "show everything"; an
    # unknown word is an error, not an empty page.
    topic = (topic or "all").strip().lower() or "all"
    if topic == "overview":
        return OVERVIEW
    if topic == "usage":
        return USAGE
    if topic == "faq":
        return "FREQUENTLY ASKED QUESTIONS\n==========================\n" + _faq()
    if topic == "resources":
        return "WHERE TO READ MORE\n==================\n" + _resources()
    if topic == "all":
        return "\n\n".join((
            "RUTH QUICK REFERENCE",
            OVERVIEW, USAGE,
            "FREQUENTLY ASKED QUESTIONS\n==========================",
            _faq(),
            "WHERE TO READ MORE\n==================",
            _resources(),
        ))
    raise ValueError(f"unknown guide topic: {topic!r}")
