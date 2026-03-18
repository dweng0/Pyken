# Journal

<!-- Agent writes entries here, newest at the top. Never delete entries. -->
<!-- Format: ## Day N — HH:MM — [short title] -->

## 2026-03-18 08:20 — Implement discard and value-only matching
Implemented three uncovered BDD scenarios: "Discarded token does not trigger strict mode failure", "Discard emit removes the token from output", and "Map a token by value only regardless of type". Updated mapper.py to handle emit: 'discard' functionality and added support for matching tokens by value only (regardless of type). All new tests pass and existing functionality remains intact. Coverage increased from 20/68 to 24/68 scenarios. Next: work on multi-token emission scenarios.
