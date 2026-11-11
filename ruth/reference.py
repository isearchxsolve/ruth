"""`ruth reference` -- the command surface, rendered from the parser itself.

Prose documentation drifts. The hand-written command table in ``README.md``
and the ``--help`` strings can silently disagree with the flags the CLI
actually accepts as the code moves, and nothing fails when they do. This
module renders the reference from the *live* argparse parser, so the published
surface is always exactly the surface that runs:

    ruth reference            # Markdown, for pasting into the README
    ruth reference --format json

``tests/test_docs.py`` pins the README's command table against this generator,
which is what keeps the two from separating again.

Pure standard library -- ``argparse`` and ``json`` only, no network, no new
runtime dependency.
"""
from __future__ import annotations

import argparse
import json

# Actions that consume no value; everything else with an option string does.
_VALUE_LESS = (
    argparse._StoreTrueAction,
    argparse._StoreFalseAction,
    argparse._StoreConstAction,
    argparse._CountAction,
    argparse._HelpAction,
    argparse._VersionAction,
)


def _subparsers(parser):
    """The subparser action of ``parser``, or ``None`` if it has none."""
    for action in parser._actions:
        if isinstance(action, argparse._SubParsersAction):
            return action
    return None


def _name(action):
    """A short, stable display name for a positional or option."""
    if action.option_strings:
        long = [f for f in action.option_strings if f.startswith("--")]
        return (long or action.option_strings)[0]
    return action.dest


def _describe_option(action):
    return {
        "flags": list(action.option_strings),
        "name": _name(action),
        "help": (action.help or "").strip(),
        "takes_value": not isinstance(action, _VALUE_LESS),
        "default": action.default,
        "choices": list(action.choices) if action.choices else None,
    }


def command_names(parser):
    """Sorted names of every subcommand the parser accepts."""
    subs = _subparsers(parser)
    return sorted(subs.choices) if subs else []


def describe(parser):
    """A JSON-serialisable description of the CLI, read from the parser.

    Nothing is hard-coded: ``global_options`` and each command's ``options``
    come from the actions the parser will actually accept, so a flag can only
    appear here if running it would work.
    """
    subs = _subparsers(parser)
    help_by_name = {}
    if subs is not None:
        for choice in subs._choices_actions:
            help_by_name[choice.dest] = (choice.help or "").strip()

    commands = []
    if subs is not None:
        for name in sorted(subs.choices):
            sp = subs.choices[name]
            options = [_describe_option(a) for a in sp._actions if a.option_strings]
            positionals = [
                {"name": a.dest, "nargs": a.nargs, "options": a.option_strings}
                for a in sp._actions if not a.option_strings
            ]
            commands.append({
                "command": name,
                "usage": f"{parser.prog} {name}",
                "help": help_by_name.get(name, ""),
                "positionals": positionals,
                "options": options,
            })

    global_options = [_describe_option(a) for a in parser._actions if a.option_strings]
    return {
        "prog": parser.prog,
        "description": (parser.description or "").strip(),
        "global_options": global_options,
        "commands": commands,
    }


def _option_table(options):
    rows = ["| Flag | Description |", "|---|---|"]
    for option in options:
        flags = ", ".join(f"`{f}`" for f in option["flags"])
        parts = []
        if option["help"]:
            parts.append(option["help"])
        if option["choices"]:
            parts.append("choices: " + ", ".join(f"`{c}`" for c in option["choices"]))
        if option["takes_value"] and option["default"] not in (None, ""):
            parts.append(f"default: `{option['default']}`")
        rows.append(f"| {flags} | {'; '.join(parts) or '—'} |")
    return rows


def render_markdown(ref):
    """Render ``describe()`` as Markdown for the README."""
    lines = [
        f"# `{ref['prog']}` command reference",
        "",
        "_Generated from the CLI parser by `ruth reference`. Do not edit by hand._",
        "",
        "## Global options",
        "",
    ]
    lines += _option_table(ref["global_options"])
    lines += ["", "## Commands", ""]
    for command in ref["commands"]:
        heading = f"### `{command['usage']}`"
        if command["help"]:
            heading += f" — {command['help']}"
        lines += [heading, ""]
        if command["options"]:
            lines += _option_table(command["options"])
        else:
            lines.append("_No options._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_json(ref):
    return json.dumps(ref, indent=2, ensure_ascii=False) + "\n"


def render(parser, fmt="markdown"):
    """Render the reference for ``parser`` in ``fmt`` ('markdown' or 'json')."""
    ref = describe(parser)
    if fmt == "json":
        return render_json(ref)
    return render_markdown(ref)
