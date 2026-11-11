# Contributing to Ruth

Thank you for helping Ruth grow. This guide covers how she is built, how to run
her tests, and how to propose a change.

## Principles

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

## Set up a development checkout

Ruth needs Python 3.9 or newer and `numpy`.

```sh
python -m pip install -e ".[dev]"
```

The `dev` extra installs `pytest`, which the launcher uses when it runs the
suite for you.

## Run the tests

The suite runs on Linux, macOS and Windows with Python 3.9, 3.12 and 3.13 in
CI. Run it the same way locally before opening a pull request:

```sh
python -m unittest discover -s tests -t .
make -C ruth/csrc          # optional: build and check the C runtime
```

## What a change must respect

- If you change the brain's step equations in Python, mirror them in
  `ruth/csrc/ruth_core.c`. The parity tests require agreement to 1e-8.
- Keep a newborn Ruth a blank slate: no data, text or personality may ship in
  the package.
- Structural self-modification goes through `ruth/morphogenesis.py` and its
  meta-kernel. Never bypass the certificate.
- Documentation is part of the product. If you add or rename a command, update
  the README command table and its usage examples;
  `tests/test_docs.py` checks that the README stays comprehensive and keeps
  its FAQ.

## Propose a change

1. Fork the repository and create a branch for your work.
2. Make the change, keeping it focused: one concern per pull request.
3. Add or update tests. A fix that changes behaviour needs a test that fails
   before it and passes after it.
4. Run the suite above and make sure it is green.
5. Open a pull request describing the problem, your change, and the evidence
   (test output or a measurement) that it works.

Draft pull requests are welcome when you want early feedback.

## Report a bug

Open an issue with the exact command you ran, what you expected, and what
happened. A failing test with its output is the most useful report of all.

## Credentials and private data

Never commit credentials, tokens, keys or another machine's private profile.
`tests/test_no_private_data.py` fails the build if one appears. Secrets are
referenced by path and kept on the machine, never in the repository.

## Releases

Bump `__version__` in `ruth/__init__.py`, then push a tag `vX.Y.Z`. The
release workflow tests, builds and publishes the downloads.
