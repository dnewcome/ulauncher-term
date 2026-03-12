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

## Notes

- `stderr` is merged with `stdout`, so error messages from failed commands are visible in the output.
- ANSI color codes are stripped from output before display.
- Commands run via `/bin/sh`, so shell built-ins, pipes, and semicolons all work: `sh echo hello; echo world`
