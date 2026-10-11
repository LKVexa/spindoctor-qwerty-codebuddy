---
description: Show every SpinDoctor function as a table (Function | What it does | Command to type)
argument-hint: "[commands|gates|tools|presets|all] [filter]"
---

Call the `spindoctor_functions` tool (section and filter from: $ARGUMENTS; default section commands) and show the returned
Markdown table to the user verbatim.

If those tools are not available (for example when the MCP server is disabled), follow the spindoctor-qwerty skill and run its CLI: `python3 ${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py` (CodeBuddy fills in the path; on Windows use `python`).
