## 2026-03-20 00:36 — journal entry
Session started. Read IDENTITY.md, BDD.md, BDD_STATUS.md, JOURNAL_INDEX.md, ISSUES_TODAY.md.

BDD_STATUS.md shows 38/68 scenarios covered, 30 uncovered. No failing tests. No open issues.

Prioritized uncovered scenarios:
1. Sequence matching (5 scenarios): sequence priority, context presence, incomplete stream, pass_through, followed_by
2. Token injection (4 scenarios): after, before, in token stream, with replacement
3. Negative context (4 scenarios): not_followed_by, not_preceded_by, combined
4. Value transforms (4 scenarios): interpolation, sequence value, regex, no-match
5. Mapping validation (3 scenarios): unknown emit mode, missing match block
6. Emit mode validation (3 scenarios): unknown strings, dict keys
7. Token shape validation (3 scenarios): missing value, missing type, not object
8. Performance (1), Shared utilities (1), Search filtering (2)

No existing tests fail. The highest priority work is to implement coverage for the uncovered BDD scenarios.
