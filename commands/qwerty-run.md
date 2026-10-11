---
description: Run SpinDoctor q.* commands with the bundled classical simulator
argument-hint: <q.* commands separated by newlines>
---

Run these SpinDoctor q.* commands with the `spindoctor_run_script` tool (one command per line), then summarise the results,
the exact probabilities next to the sampled counts, and the TXT/PDF report paths:

$ARGUMENTS

If those tools are not available (for example when the MCP server is disabled), follow the spindoctor-qwerty skill and run its CLI: `python3 ${CODEBUDDY_PLUGIN_ROOT}/skills/spindoctor-qwerty/scripts/spindoctor_cli.py` (CodeBuddy fills in the path; on Windows use `python`).

Remind the user that this is a classical FP64 simulation on their computer, not quantum hardware. Registers wider than
29 qubits (up to 298) sample in basis z only.
