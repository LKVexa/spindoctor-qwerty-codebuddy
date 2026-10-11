# SpinDoctor Qwerty 1.1.0 - SpinDoctor Qwerty for CodeBuddy
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""Point this plugin at a different Python command, for Windows (or any system without `python3`).

The plugin starts Python as `python3` in .mcp.json and in the CLI fallback of the slash commands. On Windows the python.org installer provides `python` and `py`, not `python3`. Run this once in your clone,
BEFORE installing from it:

  python tools/set_python.py python        # or: py   |   python3   |   "C:/Path To/python.exe"

Then install from the clone (`codebuddy plugin marketplace add ./spindoctor-qwerty-codebuddy`, then
`codebuddy plugin install spindoctor-qwerty@spindoctor-qwerty-codebuddy`).
It edits only these files, prints what it changed, and running it again with `python3` restores the original.
Standard library only.
"""
import glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) != 2 or not sys.argv[1].strip():
        print(__doc__); return 2
    new = sys.argv[1].strip().replace("\\", "/")
    if any(c in new for c in '"\'`$;&|<>\n'): print("refusing: the command must be a plain program name or path"); return 2
    mcp_path = os.path.join(ROOT, ".mcp.json")
    mcp = json.load(open(mcp_path, encoding="utf-8"))
    srv = mcp["mcpServers"]["spindoctor-qwerty"]; old = srv["command"]
    srv["command"] = new
    open(mcp_path, "w", encoding="utf-8", newline="\n").write(json.dumps(mcp, indent=2) + "\n")
    print(".mcp.json: command %r -> %r" % (old, new))
    shown = ('"%s"' % new) if " " in new else new
    files = glob.glob(os.path.join(ROOT, "commands", "*.md")) + glob.glob(os.path.join(ROOT, "agents", "*.md"))
    pat = re.compile(r'(?:"[^"\n]*"|[^\s`(]+)(?= "?\$\{CODEBUDDY_PLUGIN_ROOT\}/skills/spindoctor-qwerty/scripts/spindoctor_cli\.py)')
    for f in sorted(files):
        t = open(f, encoding="utf-8").read(); n = len(pat.findall(t))
        if n:
            open(f, "w", encoding="utf-8", newline="\n").write(pat.sub(lambda m: shown, t))
            print("%s: %d command(s) -> %s" % (os.path.relpath(f, ROOT), n, shown))
    return 0


if __name__ == "__main__":
    sys.exit(main())
