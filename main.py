import os
import re
import signal
import subprocess
import logging
import html

from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
try:
    from ulauncher.internals.result import Result
    ResultItem = Result
    HAS_MULTILINE = True
except ImportError:
    from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
    ResultItem = ExtensionResultItem
    HAS_MULTILINE = False
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.ExtensionCustomAction import ExtensionCustomAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from ulauncher.api.shared.action.DoNothingAction import DoNothingAction

logger = logging.getLogger(__name__)

_ANSI_RE = re.compile(r'\x1b\[[0-9;]*[mGKHF]')


def clean(text):
    """Strip ANSI escape codes and escape Pango markup characters."""
    return html.escape(_ANSI_RE.sub('', text))


class ShellRunExtension(Extension):
    def __init__(self):
        super().__init__()
        self._proc = None
        self.subscribe(KeywordQueryEvent, KeywordQueryEventListener())
        self.subscribe(ItemEnterEvent, ItemEnterEventListener())


class KeywordQueryEventListener(EventListener):
    def on_event(self, event, extension):
        # Kill any running process so the user can escape hung commands
        proc = extension._proc
        if proc is not None and proc.poll() is None:
            try:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except OSError:
                pass
            extension._proc = None

        query = event.get_argument()

        if not query:
            return RenderResultListAction([
                ResultItem(
                    icon='images/icon.png',
                    name='sh',
                    description='Type a command and press Enter',
                    on_enter=DoNothingAction(),
                )
            ])

        return RenderResultListAction([
            ResultItem(
                icon='images/icon.png',
                name=query,
                description='Press Enter to run',
                on_enter=ExtensionCustomAction({'cmd': query}, keep_app_open=True),
            )
        ])


class ItemEnterEventListener(EventListener):
    def on_event(self, event, extension):
        data = event.get_data()
        cmd = data['cmd']

        try:
            proc = subprocess.Popen(
                cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
            extension._proc = proc
            proc.wait()
            extension._proc = None
            output = proc.stdout.read().decode(errors='replace')
            returncode = proc.returncode
        except Exception as e:
            logger.exception('Failed to run command')
            return RenderResultListAction([
                ResultItem(
                    icon='images/icon.png',
                    name=clean(f'Error: {e}'),
                    on_enter=DoNothingAction(),
                )
            ])

        lines = output.splitlines()
        # Strip trailing blank lines
        while lines and not lines[-1].strip():
            lines.pop()

        items = []

        if returncode != 0:
            items.append(ResultItem(
                icon='images/icon.png',
                name=f'[exit {returncode}]',
                description='Command exited with non-zero status',
                on_enter=DoNothingAction(),
            ))

        if not lines:
            items.append(ResultItem(
                icon='images/icon.png',
                name='(no output)',
                on_enter=DoNothingAction(),
            ))
        else:
            if HAS_MULTILINE:
                items.append(ResultItem(
                    icon='images/icon.png',
                    name=f'$ {cmd}',
                    description='\n'.join(clean(l) for l in lines),
                    multiline=True,
                    on_enter=CopyToClipboardAction('\n'.join(lines)),
                ))
            else:
                name = clean(lines[0])
                description = clean('  '.join(lines[1:])) if len(lines) > 1 else 'Click to copy'
                items.append(ResultItem(
                    icon='images/icon.png',
                    name=name,
                    description=description,
                    on_enter=CopyToClipboardAction('\n'.join(lines)),
                ))

        return RenderResultListAction(items)


if __name__ == '__main__':
    ShellRunExtension().run()
