---
description: Run a SpinDoctor preset (qc-001..qc-241)
argument-hint: <preset-id> [name=value ...]
---

Run SpinDoctor preset $ARGUMENTS with the `spindoctor_run_preset` tool (preset id plus optional name=value overrides; use
`spindoctor_list_presets` to find one). Summarise each step and give the TXT/PDF report paths. Classical simulation only.

If those tools are not available (for example when the MCP server is disabled), follow the spindoctor-qwerty skill and run its CLI: `python3 ${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py` (CodeBuddy fills in the path; on Windows use `python`).
