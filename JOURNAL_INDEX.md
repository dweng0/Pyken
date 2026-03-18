# Journal Index

<!-- One line per session. Newest at the top. -->

- 2026-03-18 16:28 — Sequence matching implementation: Implemented sequence matching functionality allowing Pyken to match sequences of tokens as a unit and emit either a single token or discard the entire sequence. Added two new BDD scenarios for sequence matching. Updated the core matching algorithm to handle sequence patterns with proper priority ordering.| 2026-03-18 | 16:28 | 29/68 | implement sequence matching functionality |

- 2026-03-18 14:57 — Multi-token emission and context-aware matching: Implemented multi-token emission functionality allowing a single matched token to emit multiple tokens. Added support for context-aware matching with preceded_by and followed_by conditions. Created tests for both features and verified all existing tests still pass. Updated the mapper logic to handle complex context matching scenarios. 4 new BDD scenarios now covered.| 2026-03-18 | 14:57 | 27/68 | implement multi-token emission and context-aware matching |
| 2026-03-18 | 16:28 | 29/68 | fix build errors;implement sequence matching functionality |
