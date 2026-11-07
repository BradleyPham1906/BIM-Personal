"""kept_builds.py -- an older build of the app, read from git history.

Until 2026-11-07 every pre-phase build was kept as a file in Phase/. Those files were removed from
the working tree; the last commit that has them is KEEP_COMMIT, and git keeps them there.

    import kept_builds
    html = kept_builds.read('canvas_v10.html.bak_phase167_pre')   # str
"""
import pathlib, subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
KEEP_COMMIT = '9dc7b87'


def read_bytes(name):
    return subprocess.run(['git', 'show', '%s:Phase/%s' % (KEEP_COMMIT, name)], cwd=ROOT,
                          capture_output=True, check=True).stdout


def read(name):
    return read_bytes(name).decode('utf-8')
