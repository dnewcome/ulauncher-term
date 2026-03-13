# ulauncher-term

A [Ulauncher](https://ulauncher.io) extension for running shell commands and copying their output — without leaving the keyboard.

## Usage

Open Ulauncher and type `sh` followed by a command:

```
sh date
sh hostname
sh cat ~/.ssh/id_ed25519.pub
```

Press **Enter** to run. The output appears as a result item — the first line is shown as the title, remaining lines as the subtitle. Press **Enter** again to copy the full output to the clipboard.

If the command exits with a non-zero status, an `[exit N]` item appears above the output.

### Cancelling a hung command

If a command is taking too long, just type any character in the Ulauncher input. The running process is killed immediately and the UI resets.

## Installation

Clone or download this repo into your Ulauncher extensions directory:

```bash
git clone https://github.com/dnewcome/ulauncher-term \
    ~/.local/share/ulauncher/extensions/ulauncher-term
```

Then restart Ulauncher. The `sh` keyword will be available immediately.

During development you can symlink instead:

```bash
ln -s /path/to/ulauncher-term \
    ~/.local/share/ulauncher/extensions/ulauncher-term
```

## Multiline output (patched Ulauncher v6)

The standard Ulauncher result item shows output as a single-line title with remaining lines collapsed into the subtitle. A patched build of Ulauncher v6 adds a `multiline` flag that renders newlines in the description natively, preserving the full output structure.

When using the patched build, results are constructed like this:

```python
from ulauncher.internals.result import Result

Result(
    name="$ your-command",
    description="line one\nline two\nline three",
    multiline=True,
    icon="images/icon.png",
    on_enter=...,
)
```

This flag has no effect on stock Ulauncher — it is silently ignored — so the plugin remains compatible with unpatched installs.

## Notes

- `stderr` is merged with `stdout`, so error messages from failed commands are visible in the output.
- ANSI color codes are stripped from output before display.
- Commands run via `/bin/sh`, so shell built-ins, pipes, and semicolons all work: `sh echo hello; echo world`
