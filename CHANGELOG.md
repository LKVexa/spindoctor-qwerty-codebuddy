# Changelog

## 1.1.0 - 2026-10-10

- Engine 1.1.0 at parity with the updated SpinDoctor 3.1.2: 1-298 logical qubits (59 per entangled factor), the `mcx7` gate,
  wide-register Born-Z sampling, `q.folder` with 3.1.2 semantics (.qasm2/.circuit, skipped-file listing, compact status, 128 files /
  4 MiB / 128 commands / 4096 characters), CSV report copies and measurement-CSV fitting equations. All 241 presets replayed.
- New tools `spindoctor_functions` (in-chat function table) and `spindoctor_test_theory` (theory testing from a file, pasted text or
  the chat history, with TXT+JSON+PDF theory reports).
- The repo root is now the plugin and a one-plugin marketplace (`.codebuddy-plugin/marketplace.json`), so
  `codebuddy plugin marketplace add LKVexa/spindoctor-qwerty-codebuddy` works.
- One manifest (`.codebuddy-plugin/plugin.json`) instead of two identical copies (the `.workbuddy-plugin/` duplicate is dropped;
  CodeBuddy reads either). Author, homepage, repository and license added.
- `.mcp.json` keeps reports in `${CODEBUDDY_PLUGIN_DATA}/workspace` (kept across plugin updates) and sets UTF-8 and no-bytecode.
- The empty `hooks/hooks.json` is removed: the plugin has no hooks.
- Commands, skill and agent updated for 3.1.2 (298-qubit limit, q.folder, theory testing with user confirmation). Command CLI
  fallbacks use `${CODEBUDDY_PLUGIN_ROOT}`.
- New `tools/set_python.py` for Windows (`python` / `py` / full path) with a byte-for-byte restore.
- Tests: real CodeBuddy Code CLI validate/marketplace/install/list/disable/enable/uninstall plus the full end-to-end suite.
- License changed from MIT to GPL-3.0-or-later. Author RUSSELL PHILIP SMITHSON. README, NOTICE, COPYRIGHT and SPDX headers added.

## 1.0.0

- First release: `spindoctor-qwerty/` folder with CodeBuddy and WorkBuddy manifests, skill, 4 commands, agent, empty hooks file and `.mcp.json`.
