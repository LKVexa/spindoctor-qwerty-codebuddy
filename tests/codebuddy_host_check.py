# SpinDoctor Qwerty 1.1.0 - CodeBuddy host check
# Copyright (C) 2026 RUSSELL PHILIP SMITHSON <russellsmithson77@outlook.com>
# SPDX-License-Identifier: GPL-3.0-or-later
# This program is free software: you can redistribute it and/or modify it under the terms of the GNU General
# Public License as published by the Free Software Foundation, either version 3 of the License, or (at your
# option) any later version. It is distributed WITHOUT ANY WARRANTY; see the LICENSE file for details.
"""CodeBuddy host check. Standard library only (Python 3.8+); no CodeBuddy account, no sign-in, no model calls.

1. Static checks from the CodeBuddy plugin reference (https://www.workbuddy.ai/docs/zh/cli/plugins-reference) and marketplace
   guide: .codebuddy-plugin/plugin.json (kebab-case name, version, description, author, license, homepage/repository),
   .codebuddy-plugin/marketplace.json (name, owner, one entry with source "./"), .mcp.json (stdio, a plugin file under
   ${CODEBUDDY_PLUGIN_ROOT}, workspace under ${CODEBUDDY_PLUGIN_DATA}), skill/command/agent front matter, command CLI fallbacks
   under ${CODEBUDDY_PLUGIN_ROOT}, no hooks, no binaries, tools/set_python.py round trip.
2. With the REAL CodeBuddy Code CLI (CODEBUDDY=/path/to/codebuddy, or `codebuddy` on PATH) in a throw-away HOME:
   `codebuddy plugin validate` (marketplace + plugin manifest), `plugin marketplace add <repo>`, `plugin install
   spindoctor-qwerty@spindoctor-qwerty-codebuddy`, `plugin list --json` (1.1.0, enabled, cached copy has every component),
   `plugin disable` / `enable`, and finally `plugin uninstall`.
3. End-to-end: tests/e2e_mcp.py through the server declared in .mcp.json, resolved as the reference documents
   (${CODEBUDDY_PLUGIN_ROOT}/${CODEBUDDY_PLUGIN_DATA} substituted in command/args/env and exported, plus the CLAUDE_* aliases),
   started from the copy CodeBuddy installed (or the repo without CodeBuddy). Starting a CodeBuddy session needs a login
   (ACP `session/new` answers "Authentication required"), so the tool calls are host-simulated.

usage: python3 tests/codebuddy_host_check.py [REPO_DIR]"""
import json, os, re, shutil, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN_ID = "spindoctor-qwerty@spindoctor-qwerty-codebuddy"
TEXT = (".py", ".md", ".json", ".txt", ".csv", ".html", ".q", "")
CLI = "${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py"


def frontmatter(path):
    m = re.match(r"^---\n(.*?)\n---\n", open(path, encoding="utf-8").read(), re.S)
    return dict(re.findall(r"^([A-Za-z_-]+):\s*(.+)$", m.group(1), re.M)) if m else None


def snapshot(root):
    out = {}
    for r, ds, fs in os.walk(root):
        ds[:] = [d for d in ds if d not in (".git", "__pycache__")]
        for f in fs: out[os.path.relpath(os.path.join(r, f), root)] = open(os.path.join(r, f), "rb").read()
    return out


def main():
    os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
    repo = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
    ok = True; mode = "host-simulated"

    def T(name, cond, detail=""):
        nonlocal ok
        ok = ok and bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else "  -- " + str(detail)[:700])); sys.stdout.flush()

    load = lambda *p: json.load(open(os.path.join(*p), encoding="utf-8"))
    pj = load(repo, ".codebuddy-plugin", "plugin.json"); mk = load(repo, ".codebuddy-plugin", "marketplace.json"); mj = load(repo, ".mcp.json")
    name = pj.get("name", "")
    T("plugin.json: kebab-case name, version 1.1.0, description, author (name/email/url), GPL-3.0-or-later, https homepage/repository, no hooks/custom paths",
      re.match(r"^[a-z0-9]+(-[a-z0-9]+)*$", name) and pj.get("version") == "1.1.0" and pj.get("description") and pj["author"].get("name") == "RUSSELL PHILIP SMITHSON"
      and pj["author"].get("email") and pj.get("license") == "GPL-3.0-or-later" and pj["homepage"].startswith("https://") and pj["repository"].startswith("https://")
      and not set(pj) & {"hooks", "commands", "agents", "skills", "mcpServers", "lspServers"}, pj)
    e = (mk.get("plugins") or [{}])[0]
    T("marketplace.json: kebab-case name, owner.name, one entry for the plugin at the repo root (source \"./\"), same version and license",
      mk.get("name") == "spindoctor-qwerty-codebuddy" and mk.get("owner", {}).get("name") and len(mk["plugins"]) == 1 and e.get("name") == name
      and e.get("source") == "./" and e.get("version") == pj["version"] and e.get("license") == pj["license"], mk)
    s = mj["mcpServers"]["spindoctor-qwerty"]
    T(".mcp.json: stdio server running a plugin file; workspace under ${CODEBUDDY_PLUGIN_DATA}",
      s.get("type") == "stdio" and s["command"] == "python3" and len(s["args"]) == 1 and s["args"][0].startswith("${CODEBUDDY_PLUGIN_ROOT}/")
      and os.path.isfile(s["args"][0].replace("${CODEBUDDY_PLUGIN_ROOT}", repo)) and s["env"]["SPINDOCTOR_WORKSPACE"] == "${CODEBUDDY_PLUGIN_DATA}/workspace", s)
    md = [os.path.join(repo, "skills", "spindoctor-qwerty", "SKILL.md")] + [os.path.join(repo, d, f) for d in ("commands", "agents") for f in sorted(os.listdir(os.path.join(repo, d)))]
    fms = {os.path.relpath(p, repo): frontmatter(p) for p in md}
    T("skill, 4 commands, 1 agent: front matter parses; skill name = folder; agent has a name; descriptions are single text values",
      len(md) == 6 and all(f and f.get("description") and not f["description"].startswith(("[", "-")) for f in fms.values())
      and fms["skills/spindoctor-qwerty/SKILL.md"].get("name") == "spindoctor-qwerty" and fms["agents/qwerty-helper.md"].get("name") == "qwerty-helper", fms)
    cmds = {f: open(os.path.join(repo, "commands", f), encoding="utf-8").read() for f in os.listdir(os.path.join(repo, "commands"))}
    T("commands: $ARGUMENTS used, CLI fallback is %s (exists), no other host's variables" % CLI,
      all("$ARGUMENTS" in t and CLI in t and "CLAUDE_" not in t for t in cmds.values()) and os.path.isfile(CLI.replace("${CODEBUDDY_PLUGIN_ROOT}", repo)), list(cmds))
    allmd = "".join(open(p, encoding="utf-8").read() for p in md)
    T("honest limits in skill/agent (classical, not a quantum computer, 298/59 qubits); chat-theory confirmation step",
      "not a quantum computer" in allmd.replace("\n", " ") and "298" in allmd and "59" in allmd and "confirm" in allmd)
    T("no hooks (no hooks/ folder, no hooks in manifests), no .lsp.json, no top-level bin/",
      not os.path.exists(os.path.join(repo, "hooks")) and not os.path.exists(os.path.join(repo, ".lsp.json")) and not os.path.exists(os.path.join(repo, "bin")))
    bad = [os.path.relpath(os.path.join(r, f), repo) for r, ds, fs in os.walk(repo) if ".git" not in r.split(os.sep) and "__pycache__" not in r
           for f in fs if os.path.splitext(f)[1].lower() not in TEXT and not (f.endswith(".pdf") and r.endswith(os.path.join("examples", "theory")))]
    T("only text files (sample PDFs are generated by make_sample_pdfs.py and git-ignored)", not bad, bad)
    tmp = tempfile.mkdtemp(prefix="sdq_setpy_"); cp = os.path.join(tmp, "r"); shutil.copytree(repo, cp, ignore=shutil.ignore_patterns(".git", "__pycache__"))
    before = snapshot(cp); sp = os.path.join(cp, "tools", "set_python.py")
    r1 = subprocess.run([sys.executable, sp, "python"], stdout=subprocess.PIPE, text=True)
    mid = load(cp, ".mcp.json")["mcpServers"]["spindoctor-qwerty"]["command"]
    nmid = sum(open(os.path.join(cp, "commands", f), encoding="utf-8").read().count("`python " + CLI) for f in cmds)
    r2 = subprocess.run([sys.executable, sp, "python3"], stdout=subprocess.PIPE, text=True)
    r3 = subprocess.run([sys.executable, sp, "python; rm -rf /"], stdout=subprocess.PIPE, text=True)
    T("tools/set_python.py: 'python' rewrites .mcp.json + 4 command fallbacks, 'python3' restores byte-for-byte, shell metacharacters refused",
      r1.returncode == 0 and mid == "python" and nmid == 4 and r2.returncode == 0 and snapshot(cp) == before and r3.returncode == 2, (r1.stdout, nmid, r3.stdout))

    root = repo
    cb = os.environ.get("CODEBUDDY") or shutil.which("codebuddy")
    if cb:
        mode = "real CodeBuddy Code CLI (tool calls host-simulated)"
        home = tempfile.mkdtemp(prefix="sdq_cb_home_"); env = dict(os.environ, HOME=home)
        run = lambda *a: subprocess.run([cb] + list(a), env=env, cwd=home, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=300)
        v = run("--version").stdout.strip().splitlines()[-1]
        rs = [run("plugin", "validate", p) for p in (repo, os.path.join(repo, ".codebuddy-plugin", "plugin.json"))]
        T("CodeBuddy Code %s: codebuddy plugin validate passes for the marketplace and the plugin manifest" % v,
          all(r.returncode == 0 and '"valid": true' in r.stdout for r in rs) and '"type": "marketplace"' in rs[0].stdout and '"type": "plugin"' in rs[1].stdout, [r.stdout[-400:] for r in rs])
        r = run("plugin", "marketplace", "add", repo)
        T("codebuddy plugin marketplace add <repo>", r.returncode == 0 and "spindoctor-qwerty-codebuddy" in r.stdout, r.stdout)
        r = run("plugin", "install", PLUGIN_ID)
        T("codebuddy plugin install %s" % PLUGIN_ID, r.returncode == 0 and "Successfully installed" in r.stdout, r.stdout)
        r = run("plugin", "list", "--json")
        try: lst = json.loads(r.stdout[r.stdout.index("["):])
        except Exception: lst = []
        it = next((x for x in lst if x.get("id") == PLUGIN_ID), {})
        ip = it.get("installPath") or ""
        comp = all(os.path.exists(os.path.join(ip, c)) for c in (".codebuddy-plugin/plugin.json", ".mcp.json", "skills/spindoctor-qwerty/SKILL.md", "agents/qwerty-helper.md",
                                                                  "skills/spindoctor-qwerty/spindoctor/terminal.py", "commands/qwerty-theory.md"))
        T("codebuddy plugin list --json: 1.1.0, enabled, cached copy holds manifest, MCP config, skill + engine, 4 commands, agent",
          it.get("version") == "1.1.0" and it.get("enabled") is True and comp and len(os.listdir(os.path.join(ip, "commands"))) == 4, (it, r.stdout[-300:]))
        rd = run("plugin", "disable", PLUGIN_ID); l1 = run("plugin", "list", "--json").stdout
        re_ = run("plugin", "enable", PLUGIN_ID); l2 = run("plugin", "list", "--json").stdout
        T("codebuddy plugin disable / enable", rd.returncode == 0 and re_.returncode == 0 and '"enabled": false' in l1 and '"enabled": true' in l2, (rd.stdout[-200:], re_.stdout[-200:]))
        if ip and os.path.isdir(ip):
            root = tempfile.mkdtemp(prefix="sdq_cb_installed_"); root = os.path.join(root, "spindoctor-qwerty"); shutil.copytree(ip, root)
        r = run("plugin", "uninstall", PLUGIN_ID)
        T("codebuddy plugin uninstall", r.returncode == 0 and PLUGIN_ID not in run("plugin", "list", "--json").stdout, r.stdout[-300:])
    else:
        print("SKIP real CodeBuddy CLI not found (set CODEBUDDY=/path/to/codebuddy)")
    data = tempfile.mkdtemp(prefix="sdq_plugin_data_")
    sub = lambda x: x.replace("${CODEBUDDY_PLUGIN_ROOT}", root).replace("${CODEBUDDY_PLUGIN_DATA}", data)
    cmd = [os.environ.get("SPINDOCTOR_PYTHON") or sub(s["command"])] + [sub(a) for a in s["args"]]
    env2 = dict(os.environ, **{k: sub(v) for k, v in s.get("env", {}).items()})
    env2.update(CODEBUDDY_PLUGIN_ROOT=root, CODEBUDDY_PLUGIN_DATA=data, CLAUDE_PLUGIN_ROOT=root, CLAUDE_PLUGIN_DATA=data)
    ex = os.path.join(root, "skills", "spindoctor-qwerty", "examples", "theory")
    r = subprocess.run([sys.executable, os.path.join(HERE, "e2e_mcp.py"), "--server"] + cmd + ["--examples", ex, "--out", os.path.join(data, "e2e_results.json")], env=env2)
    T("end-to-end through the server declared in .mcp.json (plugin root: %s)" % ("CodeBuddy's installed copy" if root != repo else "repo"), r.returncode == 0)
    print("HOST-CHECK (%s)" % mode, "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
