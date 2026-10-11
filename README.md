# SpinDoctor Qwerty for CodeBuddy

**CodeBuddy Code / WorkBuddy plugin for the SpinDoctor 3.1.2 quantum-circuit simulator.** It adds a skill, four slash commands,
a helper agent and a local MCP server with six tools to [CodeBuddy Code](https://www.codebuddy.ai) (CLI and IDE) and WorkBuddy:
build and run `q.*` circuits (1-298 logical qubits), run the 241 built-in presets, process folders of command files with
`q.folder`, test theories from files, pasted text or the conversation itself, and get TXT, PDF, JSON and CSV reports. Everything
runs locally in a bundled, standard-library-only Python engine.

> **Honest limits:** SpinDoctor is a **classical** FP64 simulator running on your computer. It is not a quantum computer, does not
> connect to quantum hardware and gives no quantum speed-up or advantage. Registers hold 1-298 logical qubits, but one entangled
> group (factor) is limited to 59 qubits and dense factors to the memory budget (2^n x 16 bytes); registers wider than 29 qubits
> sample in basis Z only. Histograms come from seeded Born sampling. Requires **Python 3.8+** (no packages).

Version **1.1.0** (engine 1.1.0, "SpinDoctor 3.1.2 parity"). Author: RUSSELL PHILIP SMITHSON. License: GPL-3.0-or-later.

## What's in the plugin

| Part | File | What it does |
|---|---|---|
| Manifest | `.codebuddy-plugin/plugin.json` | Name, version, author, license (CodeBuddy also reads `.workbuddy-plugin/` and `.claude-plugin/`; one copy is enough) |
| Marketplace | `.codebuddy-plugin/marketplace.json` | Makes this repo a one-plugin marketplace (`spindoctor-qwerty-codebuddy`) |
| MCP server | `.mcp.json` | Starts `python3 ${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_mcp.py`; reports go to `${CODEBUDDY_PLUGIN_DATA}/workspace` |
| Skill | `skills/spindoctor-qwerty/` | Instructions, honesty rules, the engine and its CLI |
| Slash commands | `commands/*.md` | `/spindoctor-qwerty:qwerty-run`, `:qwerty-preset`, `:qwerty-functions`, `:qwerty-theory` |
| Agent | `agents/qwerty-helper.md` | `spindoctor-qwerty:qwerty-helper` runs scripts, presets, folders and theory tests and explains them |
| Windows helper | `tools/set_python.py` | Switches `python3` to `python`, `py` or a full path |

No hooks, no LSP server, no network access, no telemetry. Nothing runs until you use a command or the model calls a tool.

## Install (CodeBuddy Code CLI)

You need Python 3.8+ (as `python3` on macOS/Linux; see Windows below).

```sh
codebuddy plugin marketplace add LKVexa/spindoctor-qwerty-codebuddy
codebuddy plugin install spindoctor-qwerty@spindoctor-qwerty-codebuddy
```

Then run `/reload-plugins` in a session (or start a new one) and ask *"show the SpinDoctor functions"*. Check the install with
`codebuddy plugin list`. In a session, `/plugin` shows the plugin and its MCP server. To try it without installing:
`codebuddy --plugin-dir ./spindoctor-qwerty-codebuddy`.

Manage it with `codebuddy plugin disable|enable|update|uninstall spindoctor-qwerty@spindoctor-qwerty-codebuddy`.

**From a local clone:** `codebuddy plugin marketplace add ./spindoctor-qwerty-codebuddy`, then the same `install` line.

**WorkBuddy / CodeBuddy IDE:** add the marketplace `LKVexa/spindoctor-qwerty-codebuddy` in the plugin panel (or `/plugin` in a
chat) and install **spindoctor-qwerty**.

**Windows:** the python.org installer provides `python` and `py`, not `python3`. Clone the repo, run
`python tools/set_python.py python` (or `py`, or a full path to `python.exe`), then add the marketplace from that folder.
`python tools/set_python.py python3` restores the original files.

## Commands

| Command | What it does |
|---|---|
| `/spindoctor-qwerty:qwerty-run <q.* commands>` | Runs q.* commands and summarises probabilities, counts and report paths |
| `/spindoctor-qwerty:qwerty-preset <qc-NNN> [name=value ...]` | Runs one of the 241 presets |
| `/spindoctor-qwerty:qwerty-functions [section] [filter]` | Shows the function table |
| `/spindoctor-qwerty:qwerty-theory <file \| text \| "we discussed">` | Tests a theory and writes a theory test report |

Each command uses the `spindoctor_*` MCP tools. If the server is disabled, it falls back to the bundled CLI at
`${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py`.

## SpinDoctor Qwerty - plugin tools

| Function | What it does | Command to type |
|---|---|---|
| Function table (spindoctor_functions) | Show this table in chat | Ask: "show the SpinDoctor functions" or `/spindoctor-qwerty:qwerty-functions` |
| Run a script (spindoctor_run_script) | Run any q.* lines above; returns results + TXT/JSON/CSV/PDF report paths | Ask: "run q.circuit new bell 2 / q.circuit add h 0 / ..." |
| Run a preset (spindoctor_run_preset) | Run qc-001..qc-241 with overrides | Ask: "run preset qc-067 with shots=64" |
| List presets (spindoctor_list_presets) | Search the 241 presets | Ask: "list presets about Grover" |
| Read a report (spindoctor_report) | List/read TXT reports (PDF/JSON paths alongside) | Ask: "show the newest SpinDoctor report" |
| Test a theory from a file (spindoctor_test_theory source=file) | Read a .txt/.md/.pdf/.py/.json/.csv/.q attachment, then hypothesis -> prediction -> q.* script -> run -> verdict + TXT/PDF theory report | Ask: "test the theory in C:/notes/theory.md" (the host must pass the file path/content) |
| Test a theory from text (spindoctor_test_theory source=text) | Same pipeline for pasted text | Ask: "test this theory: a Hadamard on \|0> gives 50/50" |
| Test the theory we discussed (spindoctor_test_theory source=chat) | The AI summarises the theory from the conversation (claims, assumptions, variables, prediction), you confirm, then it is tested; quoted excerpts go in the report under 'Source: chat history'. An exported chat transcript (.txt/.md/.json/.html) also works | Ask: "test the theory we discussed" or "test the theory in my exported chat C:/chats/conversation.json" |

Every command family is listed with a runnable example in **[FUNCTIONS.md](FUNCTIONS.md)** (the exact table the tool shows):
circuits (`q.circuit`, including 298-qubit wide registers and the `mcx7` gate), queries (`q.query`), the tranche register
(`q.tranche`), the procedural grid, presets and sequences, resource planning, math calculators, physics models, lessons, noise, error
correction, compilation, algorithms, inputs/folders/history (`q.input`, `q.folder`, `q.history`) and the cartridge commands.

## Theory testing

`spindoctor_test_theory` turns a claim into a test: hypothesis -> measurable prediction -> `q.*` script -> run -> compare -> a TXT +
JSON + PDF **theory test report** with the hypothesis, script, raw results, verdict (*supported*, *not supported* or *inconclusive*)
and limits.

- **From a file:** .txt, .md, .pdf, .py, .json, .csv or .q. In CodeBuddy, @-mention the file or give its path on your computer.
- **From pasted text.**
- **From the chat history:** say *"test the theory we discussed"*. The model writes a short summary (claims, assumptions, variables,
  measurable prediction), shows it to you to confirm or correct, then passes it with optional quoted excerpts; the report records them
  under *Source: chat history*. Exported chat transcripts (.txt/.md/.json/.html from ChatGPT, Claude and others) also work.
- The plugin cannot read your conversation or attachments by itself: only the model sees them, and very long conversations may already
  be truncated by the context window.

Sample theory files and chat transcripts are in `skills/spindoctor-qwerty/examples/theory/`. The two sample
PDFs are stored as text; run `python3 skills/spindoctor-qwerty/examples/theory/make_sample_pdfs.py` to
recreate them.

## Folder ingestion (`q.folder`)

`q.folder run path="<folder>"` runs every supported file at the top level of a folder (.txt, .csv, .json, .qasm, .qasm2, .circuit,
.pdf) in ordinal name order: 1-128 supported files, at most 4 MiB per file, 1-128 commands per file and 4096 characters per command,
strict UTF-8. Other files (for example .md) are skipped and listed. The first failing file stops the job.

## Testing

| Test | Command | Result for 1.1.0 |
|---|---|---|
| Host check with the **real CodeBuddy Code CLI** | `CODEBUDDY=$(command -v codebuddy) python3 tests/codebuddy_host_check.py` | 16/16 checks, end-to-end 12/12 |
| Same without CodeBuddy | `python3 tests/codebuddy_host_check.py` | 10/10 checks, end-to-end 12/12 |

**Real host, tool calls host-simulated:** CodeBuddy Code 2.164.0 was installed from npm (`@tencent-ai/codebuddy-code`) on a Linux
test machine and used **without signing in** and without calling a model. It validated the marketplace and the plugin manifest,
added the marketplace, installed the plugin, listed it enabled at 1.1.0 with every component in its cache, disabled, re-enabled and
uninstalled it. Starting a CodeBuddy session needs a login, so `tests/e2e_mcp.py` drives the MCP server from CodeBuddy's installed
copy, launched exactly as `.mcp.json` declares. WorkBuddy and the IDE weren't tested. Details in [E2E_RESULTS.md](E2E_RESULTS.md).

## Author and license

Author: **RUSSELL PHILIP SMITHSON** <russellsmithson77@outlook.com>

Copyright (C) 2026 RUSSELL PHILIP SMITHSON. Licensed under the GNU General Public License v3.0 or later (`GPL-3.0-or-later`): see
[LICENSE](LICENSE), [NOTICE](NOTICE) and [COPYRIGHT](COPYRIGHT). `plugin.json` and `marketplace.json` carry the license and author.
CodeBuddy and WorkBuddy are trademarks of Tencent; this project is not affiliated with Tencent.
