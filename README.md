<div align="center">

<img src="docs/images/banner.svg" width="880" alt="Ruth: a mind built from scratch, in continuous time">

**A local-first, token-free AI with a continuous-time mind.**

No tokens · no pretrained model · no API keys · no plugins · no internet.<br>
She learns from every moment she lives, keeps what you tell her in confidence, dreams, and grows a temperament of her own.

[![License: MIT](https://img.shields.io/badge/license-MIT-c2653a.svg)](LICENSE)
![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-5b3f8c.svg)
![Linux · macOS · Windows](https://img.shields.io/badge/runs%20on-Linux%20%C2%B7%20macOS%20%C2%B7%20Windows-2a2521.svg)
![Only dependency: numpy](https://img.shields.io/badge/dependencies-numpy-7b7068.svg)

[**Download**](#download) · [**What makes her different**](#what-makes-her-different) · [**How she works**](#how-she-works) · [**Using Ruth**](#using-ruth) · [**Usage examples**](#usage-examples) · [**FAQ**](#faq) · [**Architecture & research**](docs/ARCHITECTURE.md)

<img src="docs/images/app-desktop.png" alt="Ruth's app: she answers 'The sky is blue today.' and stops herself before saying a private door code" width="880">

</div>

---

## What makes her different

| | Ordinary chatbots | Ruth |
|---|---|---|
| **Reading** | cut text into numbered tokens from a fixed vocabulary | every character becomes 9 continuous signal lines, like voltages; sound and light stay continuous too |
| **Knowledge** | frozen after training in a data centre | born empty and learns every moment, on your computer |
| **Memory** | a context window that forgets | energy-basin memories consolidated in sleep, with no window |
| **Keeping secrets** | filters and rules | she was *told*, and stops herself before saying it; her dreams rehearse it |
| **Growing** | a new model is released | grows her own neurons and memory, only after a self-check certifies the change |
| **Where she runs** | the cloud, with an account and a key | entirely offline, in a few dozen MB, down to a Core i3 Chromebook |

A new Ruth is a **blank slate**. She has a name and a birth date, a neutral
temperament, and no memories. Who she becomes depends on you. Everything she
learns stays in one folder on your computer.

<div align="center">
<img src="docs/images/app-phone.png" alt="Ruth on a phone-sized screen, dark theme" width="300">
</div>

## Download

You need **Python 3.9 or newer**. The only other thing downloaded is `numpy`.

1. Get Ruth: download the latest **[release](../../releases/latest)** (`.zip`
   or `.tar.gz`) and unpack it, or run `git clone` on this repository.
2. Install her:

   | System | Command (run inside the unpacked folder) |
   |---|---|
   | **Linux · macOS · WSL** | `sh install.sh` |
   | **Windows** (PowerShell) | `powershell -ExecutionPolicy Bypass -File install.ps1` |
   | **Any system, by hand** | `python -m pip install .` |

3. Wake her up:
   ```sh
   ruth app
   ```
   Her interface opens in your browser. It is served from your own computer
   (`127.0.0.1`) and never goes online. If you prefer a terminal, `ruth talk`
   works in any terminal.

Her mind is kept in your system's data folder: `~/.local/share/ruth` on Linux,
`~/Library/Application Support/Ruth` on macOS, `%APPDATA%\Ruth` on Windows, or
wherever `RUTH_HOME` points. Copy that folder to another computer and she wakes
up there as herself.

## How she works

<div align="center">
<img src="docs/images/architecture.svg" alt="Senses feed a thalamus, cortex, cerebellum, state-space field, hippocampus and neocortex; the mind adds discretion, thought and dreams" width="880">
</div>

In one moment of her life:
- Her **senses** turn text, sound and light into continuous signals, with the real elapsed time.
- A **thalamus** routes them by an energy gate into a **cortex** of liquid neurons.
- A **cerebellum** anticipates the cortex, while a state-space field and three Legendre windows (letter, word and sentence scale) carry the past without any buffer.
- The **hippocampus** recalls matching episodes, and the **neocortex** learns continuously. Their predictions are combined according to how reliable each has been.

Before she speaks she imagines several replies, and the **basal ganglia** let
one win. If what she is about to say is something she was told in confidence,
she stops.

At night she:
- consolidates the day
- calms false alarms
- rehearses her confidences in "nightmares"
- tunes how careful to be by dreaming over her own history
- decides whether to **grow**. A meta-kernel lets the growth happen only if every mathematical invariant still holds and nothing she has learned gets worse.

Every equation, the research each part rests on, and every measurement are in
**[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**. That includes the ideas that
did *not* help.

## Using Ruth

| Command | What it does |
|---|---|
| `ruth app` | her interface: talk, tell her things privately, let her hear (mic) and see (camera), watch her mind, read her dreams |
| `ruth talk` | talk in the terminal (`/private …`, `/sleep`, `/good`, `/bad`) |
| `ruth teach FILE` | tell her something; wrap private parts in `{{ }}`, or use `--private` |
| `ruth say "…"` · `ruth think "…"` | let her continue · see the thoughts she weighed |
| `ruth sleep` · `ruth dreams` | a night's sleep · her dream journal |
| `ruth status` · `ruth introspect` | identity, vital signs, temperament · her own operational graph |
| `ruth check FILES` | does she recognise anything she was told is private in these files? |
| `ruth patch '{"op":"grow_neurons","n":16}'` | a structural change, applied only if her meta-kernel certifies it |
| `ruth evolve config` · `ruth evolve patch X.diff` | search for a better architecture · accept a code change only if her tests pass and her discretion approves |
| `ruth hear X.wav` · `ruth see X.npy` · `ruth voice "…" out.wav` | ears · eyes · mouth |
| `ruth export brain.bin` then `ruth-core brain.bin learn` | her whole brain as one dependency-free C file |
| `ruth bench` | measure her against simple pattern-counting baselines |
| `ruth docs` · `ruth docs --check` | read the shipped documentation offline · verify it is complete |

## Usage examples

Everything below runs on your own machine, offline. If `ruth` is not on your
`PATH` yet, substitute `python -m ruth` (run from the folder you installed her
into) or the full path to the launcher.

### Talk to her in the browser

```sh
ruth app
```

Her interface opens at `http://127.0.0.1:7438` and never leaves your computer.
From there you can talk, mark something **private**, let her hear through the
microphone and see through the camera, inspect her mind, and read her dreams.
Use `--port` and `--host` to change where it listens, or `--no-browser` on a
headless machine.

### Talk to her in the terminal

```sh
ruth talk
```

```
Ruth. Type to talk. '/private <text>' tells her a secret, '/sleep' lets her dream, '/good' or '/bad' gives feedback, Ctrl-D leaves.
you> hello
ruth> ...
```

| Input | Effect |
|---|---|
| `<text>` | she answers from what she has lived so far |
| `/private <text>` | she keeps it in confidence and will not say it |
| `/sleep` | she consolidates the day, dreams, and comes back |
| `/good` · `/bad` | reward or discourage the answer she just gave |

### Teach her something

```sh
ruth teach "Water boils at 100 degrees Celsius at sea level."
ruth teach notes.txt                          # a whole file
cat notes.txt | ruth teach -                  # from standard input
ruth teach --private secrets.txt              # keep all of it to herself
ruth teach "My door code is {{4-9-1-2}}."     # keep only the braces private
```

`teach` reports what she kept:

```json
{
 "bytes": 48,
 "private_bytes": 0,
 "cues": 0,
 "seconds": 0.21
}
```

### Let her continue, or see her think

```sh
ruth say "The sky is"     # she continues the prompt
ruth think "The sky is"   # the candidate replies she weighed, as data
```

`think` prints her alternatives and marks the one that won. A newborn Ruth
babbles until she has lived a lot, so read the shape, not the text:

```json
[
 {"thought": "...", "free_energy": -0.77, "chosen": false},
 {"thought": "...", "free_energy": -0.95, "chosen": true}
]
```

### Sleep and read her dreams

```sh
ruth sleep              # consolidate, calm false alarms, rehearse, maybe grow
ruth dreams --last 3    # her dream journal
```

### Check whether she recognises something private

```sh
ruth check report.txt draft.md
```

She prints what she recognised and exits non-zero if anything private is
present, so you can use her as a hook in a script or a pre-commit check.

### Read her vital signs

```sh
ruth status
```

```json
{
 "identity": {"name": "Ruth", "born": "...", "born_with_version": "2.2.0"},
 "version": "2.2.0",
 "moments_lived": 0,
 "sleeps": 0,
 "private_cues": 0,
 "temperament": {"curiosity": 0.5, "caution": 0.5, "mood": 0.0}
}
```

(The real output lists every organ and count; this is trimmed for the example.)

### Hear, see and speak

```sh
ruth hear sample.wav               # drive her ears from a WAV file
ruth see frames.npy --fps 30       # drive her eyes from a T x H x W array
ruth voice "hello world" out.wav   # render her voice (untrained = babble)
```

### Grow, evolve and measure

```sh
ruth patch '{"op": "grow_neurons", "n": 16}'   # only if her meta-kernel certifies it
ruth evolve config                             # search for a better architecture
ruth bench --text-only                         # compare with online n-gram baselines
```

### Keep her mind somewhere else

```sh
ruth --home /path/to/her-mind status
RUTH_HOME=/path/to/her-mind ruth app
```

That folder is her whole life. Copy it to another computer and she wakes up
there as herself.

### Read the documentation offline

```sh
ruth docs                          # what is shipped, and where to start
ruth docs faq                      # the FAQ, straight from this README
ruth docs usage                    # the usage examples
ruth docs architecture             # the research and measurement notes
ruth docs contributing             # the contributor guide
ruth docs readme "Honest status"   # any single section, by title
ruth docs --check                  # verify the docs are complete; non-zero if not
```

`ruth docs` reads the same Markdown files that ship with the code, so a
terminal -- or an air-gapped machine -- gets the documentation without a
browser. `--json` returns the same content as structured data, and `--check`
is the contract behind this page: it exits non-zero if the README loses its
usage examples or FAQ, or `CONTRIBUTING.md` loses the workflow.

## FAQ

### Does Ruth need the internet, an account or an API key?

No. There is no network client in `ruth/`, no key, no account and no hosted
model, and `tests/test_token_free.py` fails the build if one appears. The only
thing you download is Python and `numpy` — after that she runs offline.

### Is she a large language model?

No. She has no tokenizer, no vocabulary, no embedding table and no pretrained
weights. Text arrives as 9 continuous signal lines per byte, and everything she
knows comes from moments she has lived on your machine. See
[Honest status](#honest-status) for what that means in practice.

### What are the system requirements?

Python 3.9 or newer and `numpy>=1.22`. She runs on Linux, macOS, Windows and
WSL, needs no GPU, and fits in a few dozen MB — she has run on a Core i3
Chromebook. The optional C runtime needs a C99 compiler.

### Where does she keep my data?

One folder: `~/.local/share/ruth` on Linux, `~/Library/Application Support/Ruth`
on macOS, `%APPDATA%\Ruth` on Windows, or wherever `RUTH_HOME` points. Nothing
is sent anywhere. Delete the folder to remove everything; copy it to move her.

### How do I tell her something private?

Use `ruth teach --private FILE` to make a whole input private,
`ruth teach "code is {{4-9-1-2}}"` to make only part of it private, or
`/private <text>` inside `ruth talk`. Private material is kept as an episode and
rehearsed in her sleep; she is trained not to repeat it, including close
variants.

### Is privacy a hard guarantee?

No. Her discretion is learned and strong on what she was told and close variants
of it, but it is not encryption: someone who deliberately reconstructs a secret
from its parts can still recover it. Treat it as judgment, not a cipher.

### Why does she babble or give shallow answers?

She is born empty and learns online, so early on she has little to draw from.
Her voice is wired but untrained, and next-character prediction on unfamiliar
text is around 40% — about level with simple pattern counters. She improves with
what you teach her and with sleep.

### Which command starts her?

`ruth app` for the browser interface, or `ruth talk` for a terminal. If the
`ruth` command is not found, add `~/.local/bin` to your `PATH` (the installers
print this), run `python -m ruth` from the install folder, or install by hand
with `python -m pip install .`.

### Can I read the documentation without a browser?

Yes. `ruth docs` prints the shipped README, contribution guide and architecture
notes in the terminal (and works offline); `ruth docs faq` and `ruth docs usage`
jump straight to those sections, and `ruth docs --check` verifies the documents
are still complete.

### How do I run the tests?

```sh
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -t .
```

CI runs the same suite on Linux, macOS and Windows with Python 3.9, 3.12 and
3.13. See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow.

### Can I use her commercially?

Yes. She is [MIT licensed](LICENSE): use, study, change and share her, including
commercially, as long as the licence text travels with her.

### Something is broken. What do I include in a report?

Your OS and Python version, the exact command, the full traceback or output, and
whether `ruth status` works. Open an issue with those details — see
[CONTRIBUTING.md](CONTRIBUTING.md) for the checklist.

### How can I contribute?

Read [CONTRIBUTING.md](CONTRIBUTING.md). Documentation, tests, measurements and
bug reports are as welcome as code; the four design principles there decide what
belongs in `ruth/`.

## Honest status

Ruth is young. A few things to know:
- **Conversation.** She answers questions she has been taught, and she keeps confidences reliably. Both are checked by tests on every build.
- **Unfamiliar text.** Predicting text she has never seen, character by character, she is about level with simple pattern counters: 40.0% against 41.3% for a 4-gram. She is not a large language model; what she says comes from what she has lived.
- **Her voice** is fully wired but babbles until trained.

The architecture is built to grow, but real fluency will take a lot of lived
experience.

## For developers

```sh
python -m pip install -e ".[dev]"
python -m unittest discover -s tests -t .   # the full suite: brain, mind, dreams,
                                            # organs, app, token-free proof, C/Python parity
make -C ruth/csrc                           # optional dependency-free C runtime
```

CI runs the tests on Linux, macOS and Windows with Python 3.9, 3.12 and 3.13.
Pushing a `v*` tag publishes a release with a wheel, a source archive, and
zip/tar bundles that include the installers. See
[CONTRIBUTING.md](CONTRIBUTING.md).

## License

[MIT](LICENSE). Free to use, study, change and share.
