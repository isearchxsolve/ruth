# Contributing to Ruth

Thank you for helping Ruth grow. Four principles decide what belongs here:

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

## Getting started

You need **Python 3.9 or newer**; `numpy` is the only runtime dependency.
Install the package in editable mode with the test extra:

```sh
git clone <your-fork>
cd ruth
python -m pip install -e ".[dev]"
```

That is the whole setup.

## Running the tests

The suite is the contract, so it must pass before anything is called done:

```sh
python -m unittest discover -s tests -t .
```

`pytest` runs the same tests with a shorter report:

```sh
python -m pytest tests -q
```

To iterate on one area, run a single file:

```sh
python -m unittest tests.test_docs -v
```

The suite is offline and CPU-only. It covers the brain, the mind, dreams, the
organs, the app, the shipped templates, the token-free proof, and the C/Python
parity check.

## Style

- Follow **PEP 8** with a 100-column line length, matching the rest of the
  tree.
- Do not add a runtime dependency without the measurement that justifies it.
- Write docstrings that say *why*, not only *what* — several modules explain
  the defect they exist to prevent.
- Name a test after the behaviour it protects. A failing test should read as a
  sentence about what broke.

## Submitting a change

1. Open an issue, or comment on an existing one, so the *why* is recorded.
2. Work on a branch and add a test that fails before the change and passes
   after it.
3. Run the full suite: `python -m unittest discover -s tests -t .`.
4. Open a pull request describing the defect, the fix, and the tests you ran.
   Keep it focused — one concern per pull request.
5. CI runs on Linux, macOS and Windows with Python 3.9, 3.12 and 3.13 before a
   maintainer merges.

By contributing you agree that your work is released under the
[MIT License](LICENSE).

## Where to look

| Question | Document |
|---|---|
| How do I use her? | [README.md](README.md) |
| How does the mind work, and what is it based on? | [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) |
| What is expected of a change? | this file |

Rules that are easy to trip over:

- If you change the brain's step equations in Python, mirror them in
  `ruth/csrc/ruth_core.c`. The parity tests require agreement to 1e-8.
- Keep a newborn Ruth a blank slate: no data, text or personality may ship in
  the package. `tests/test_token_free.py` checks this.
- Structural self-modification goes through `ruth/morphogenesis.py` and its
  meta-kernel. Never bypass the certificate.

## Releases

Bump `__version__` in `ruth/__init__.py`, then push a tag `vX.Y.Z` (for
example `v0.4.0`). The release workflow tests, builds and publishes the
downloads.
