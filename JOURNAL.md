# Journal

<!-- Agent writes entries here, newest at the top. Never delete entries. -->
<!-- Format: ## Day N — HH:MM — [short title] -->

## 2026-03-18 16:28 — Sequence matching implementation
Implemented sequence matching functionality allowing Pyken to match sequences of tokens as a unit and emit either a single token or discard the entire sequence. Added two new BDD scenarios: "A sequence of tokens is matched and emitted as a single token" and "A sequence of tokens is matched and discarded entirely". Both tests pass and the mapper now supports sequence-based transformations. Updated the core matching algorithm to handle sequence patterns with proper priority ordering.

## 2026-03-18 14:57 — Multi-token emission and context-aware matching
Implemented multi-token emission functionality allowing a single matched token to emit multiple tokens. Added support for context-aware matching with preceded_by and followed_by conditions. Created tests for both features and verified all existing tests still pass. Updated the mapper logic to handle complex context matching scenarios. 4 new BDD scenarios now covered.
