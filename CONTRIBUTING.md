# Contributing to Ruth

Thank you for helping Ruth grow. Anyone is welcome to contribute, whatever your
experience level: documentation, tests and small bug fixes are as valuable as a
new organ. Four principles decide what belongs here:

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

## Code of conduct

Be kind, be patient, and assume good faith. Ruth is a long-lived project built
in the open: discuss ideas on their merits, keep review comments about the
code, and help newcomers land their first change.

## Getting started

You need Python 3.9 or newer.

1. Fork and clone the repository, then `cd` into it.
2. Install Ruth in editable mode with the developer extras:

   ```sh
   python -m pip install -e ".[dev]"
   ```

3. Confirm the command-line entry point works:

   ```sh
   ruth --version
   ```

## Workflow

```sh
python -m pip install -e .
python -m unittest discover -s tests -t .
```

## Project layout

| Path | What lives there |
|---|---|
| `ruth/` | the mind: senses, brain, memory, dreams, self-modification, CLI and app |
| `ruth/csrc/` | one dependency-free C99 file that mirrors the brain |
| `tests/` | the suite that must pass before anything is called done |
| `docs/` | architecture, research basis and measurements |
| `tools/` | the local tools (LSP bridge, doctor, MCP servers) |
| `soul/` | identity, soul, voice and a user template |

## Running the tests

```sh
python -m unittest discover -s tests -t .   # the whole suite
python -m unittest tests.test_docs -v       # just the documentation contract
```

CI runs the full suite on Linux, macOS and Windows with Python 3.9, 3.12 and
3.13. Run it locally before you open a pull request.

## Code style

- Match the surrounding code; keep functions small and named for what they do.
- Standard library + `numpy` only -- do not add a runtime dependency (a test
  enforces this).
- Give every non-obvious decision a short comment that explains *why*.
- Keep `ruth/` self-contained and offline. Never add a network client.

## Pull requests

1. Branch from `main` and keep the change focused on one thing.
2. Add or update a test that would fail without your change.
3. Run the whole suite (`python -m unittest discover -s tests -t .`) and leave
   it green.
4. Update the docs (`README.md`, `CONTRIBUTING.md`, `docs/ARCHITECTURE.md`)
   when behaviour changes. The command surface is generated: `ruth reference`
   prints every command and flag from the live parser, and `tests/test_docs.py`
   fails if the README documents a command the CLI does not define -- so add
   the command to the parser and the README follows from `ruth reference`.
5. If you change the brain's step equations in Python, mirror them in
   `ruth/csrc/ruth_core.c`. The parity tests require agreement to 1e-8.
6. Keep a newborn Ruth a blank slate: no data, text or personality may ship in
   the package.
7. Structural self-modification goes through `ruth/morphogenesis.py` and its
   meta-kernel. Never bypass the certificate.
8. Write a description that says what changed and how you measured it.

## Reporting a bug

Open an issue with:

- what you did, what you expected, and what happened;
- your operating system and `python --version`;
- the exact command and its full output, or the traceback.

Please redact anything private: do not paste secrets, door codes, or the
contents of your `RUTH_HOME` data folder.

## Reporting a security issue

If you believe you have found a vulnerability, do not open a public issue.
Report it privately to the maintainer with enough detail to reproduce it, and
allow time for a fix before any public disclosure.

## Releases

Bump `__version__` in `ruth/__init__.py`, then push a tag `vX.Y.Z`. The
release workflow tests, builds and publishes the downloads.
