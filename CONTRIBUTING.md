# Contributing to Ruth

Thank you for helping Ruth grow. This guide covers the design principles, how
to set up a development environment, how to run the tests, and how to get a
change merged.

## Design principles

Four principles decide what belongs here:

1. **Token-free.** No tokenizer, vocabulary, embedding table of symbols, or
   pretrained model. Signals stay continuous; `tests/test_token_free.py`
   enforces this on every build.
2. **Self-contained.** Python standard library + numpy only, and no network
   access. The C runtime stays dependency-free C99.
3. **Security is her judgment.** Privacy comes from what she was told and
   her discretion, not from filters or keys.
4. **Measured, not assumed.** A change that claims to help comes with a
   measurement (`ruth bench`, a test, or a documented experiment), and null
   results are written down in `docs/ARCHITECTURE.md` too.

## Ways to contribute

You do not have to write brain equations to help:

- **Report a bug.** A precise report with a reproduction is worth a patch.
- **Improve the documentation.** The README, this guide, the FAQ and
  `docs/ARCHITECTURE.md` are part of the product.
- **Add or sharpen a test.** Boundary cases, regressions and parity checks are
  always welcome.
- **Share a measurement.** A documented experiment, including one that shows a
  change did *not* help, saves the next person the work.
- **Send code.** Keep it small, focused and covered by a test.

## Development setup

```sh
git clone <repository-url>
cd ruth
python -m venv .venv
. .venv/bin/activate            # Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
```

`-e` keeps the installed package pointed at your working tree, and `[dev]` adds
`pytest`, which the launchers use. Python 3.9 or newer is required; `numpy` is
the only runtime dependency.

## Running the tests

```sh
python -m unittest discover -s tests -t .       # the canonical suite
python -m unittest tests.test_token_free -v     # one module
make -C ruth/csrc                               # optional C runtime
```

- Run the suite before opening a pull request; CI runs the same command on
  Linux, macOS and Windows with Python 3.9, 3.12 and 3.13.
- `tests/test_token_free.py` proves the token-free and self-contained rules and
  the blank slate. Do not weaken it.
- `tests/test_no_private_data.py` proves that no credentials, owner paths or
  private repository names are committed. Do not add fixtures outside the
  explicit, auditable exemptions in that file.
## Code style and conventions

- Standard library + numpy only inside `ruth/`; no network access, ever.
- If you change the brain's step equations in Python, mirror them in
  `ruth/csrc/ruth_core.c`. The parity tests require agreement to 1e-8.
- Keep a newborn Ruth a blank slate: no data, text or personality may ship in
  the package.
- Structural self-modification goes through `ruth/morphogenesis.py` and its
  meta-kernel. Never bypass the certificate.
- Give public functions and modules a docstring that explains *why*, not just
  *what*. Match the surrounding style, keep lines readable, and prefer a clear
  name over a comment.
- Prefer small, focused commits over one large change.
- Never commit credentials, tokens, personal data, owner paths or private
  repository names. `tests/test_no_private_data.py` fails the build if you do.

## Pull request process

1. Fork the repository and branch from `main` (for example
   `fix/faq-typo` or `feat/ear-window`).
2. Make the smallest change that solves the problem, with a test that would
   fail without it.
3. Run `python -m unittest discover -s tests -t .` and confirm it is green.
4. Write a commit message that says what changed and why.
5. Open a pull request that explains the problem, the approach and how you
   tested it. Link the issue it closes.
6. Stay responsive to review; small follow-up commits are fine.

A pull request is ready when:

- [ ] the full suite passes locally;
- [ ] new behavior has a test, and regressions have a regression test;
- [ ] user-facing changes are reflected in `README.md`, the FAQ or
      `docs/ARCHITECTURE.md`;
- [ ] no new runtime dependency, network call or pretrained asset is added;
- [ ] no credential, personal datum or private path is committed.

## Reporting bugs

Open an issue with enough detail that someone else can reproduce it:

- your operating system and `python --version`;
- the exact command you ran;
- the full traceback or output, not just the last line;
- the output of `ruth status`, if Ruth starts at all;
- whether it still happens with a fresh mind folder
  (`RUTH_HOME=/tmp/fresh-ruth ruth ...`);
- the smallest input that triggers it, when the bug involves data.

Redact anything private before pasting. Never put a real secret in an issue.

## Proposing features

Open an issue before writing a large patch. Describe the problem you are trying
to solve, why it belongs in Ruth, how you would measure whether it helped, and
whether it needs anything beyond the standard library and numpy (usually it
should not). The design principles above are the tie-breaker.

## Documentation

Documentation is part of the product, not an afterthought. Keep commands
copy-pasteable, keep quoted output accurate, and keep the FAQ current: if a
question comes up twice, it belongs in the FAQ. `ruth docs --check` reads these
files and exits non-zero when the contract below is broken, so run it (or the
suite, which calls the same checker) after editing any document. The main
documents are:

- `README.md` — what Ruth is, how to install her, usage examples and the FAQ;
- `CONTRIBUTING.md` — this guide;
- `docs/ARCHITECTURE.md` — equations, research basis and measurements;
- `AGENTS.md` — standing instructions for agents working in this repository.

## Releases

Bump `__version__` in `ruth/__init__.py`, then push a tag `vX.Y.Z`. The
release workflow tests, builds and publishes the downloads.
