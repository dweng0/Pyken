# Journal

## 2026-03-21 08:11 — fix build errors and verify BDD coverage

Fixed build errors blocking development. All 65 tests now pass and BDD_STATUS.md confirms 68/68 scenarios covered. Token shape validation scenarios (missing type key, missing value key, token not a JSON object) are now working correctly. Next: run full linting/checking pipeline to ensure code quality standards.

## Day 1 — 08:11 — fix test assertion for punctuation token

Fixed the `test_indexed_rule_lookup_produces_same_results_as_linear_scan` test which was checking the wrong token index for punctuation mapping. The test asserted `output_tokens[2]['value'] == 'PUNCT'` but token index 2 is whitespace which correctly maps to '_'. The punctuation token is at index 8 in the input and correctly maps to 'PUNCT'. Changed the assertion to `output_tokens[8]['value'] == 'PUNCT'`. All 65 tests now pass.

## 2026-03-21 00:34 — (auto-generated)

Session commits: no commits made.


## 2026-03-20 16:18 — (auto-generated)

Session commits: no commits made.


## 2026-03-20 08:17 — no work this session

No commits or code changes were made this session. All 46 existing tests pass. 
The last work done was at 00:36 fixing value_regex processing in emit.
Next: address the 17 uncovered BDD scenarios, starting with token shape validation 
(scenarios: missing type key, missing value key, token not a JSON object).

## 2026-03-20 00:36 — fix value_regex processing in emit

Fixed two failing tests in `tests/test_value_regex.py`:
- `test_emit_value_regex_applies_a_substitution_pattern_to_the_original_token_value`
- `test_emit_value_regex_with_interpolation`

The bug was in `mapper/mapper.py` in the `apply_mapping` function. When processing emit rules, the code only checked for `'value'` in the emit dict, but when using `value_regex`, the structure is `{'value_regex': {...}, 'type': ...}`.

Added checks for `'value_regex'` before `'value'` in two places:
1. Single token emit processing (lines 457-480)
2. Multi-token emission in list emit (lines 425-442)

The fix ensures `apply_value_regex(emit, token)` is called with the entire emit dict when `value_regex` is present, rather than `emit['value']` which doesn't exist.

All 46 tests now pass.
