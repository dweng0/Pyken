# Journal

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

## Day 2026-03-20 00:36 — fix value_regex processing in emit

Fixed two failing tests in `tests/test_value_regex.py`:
- `test_emit_value_regex_applies_a_substitution_pattern_to_the_original_token_value`
- `test_emit_value_regex_with_interpolation`

The bug was in `mapper/mapper.py` in the `apply_mapping` function. When processing emit rules, the code only checked for `'value'` in the emit dict, but when using `value_regex`, the structure is `{'value_regex': {...}, 'type': ...}`.

Added checks for `'value_regex'` before `'value'` in two places:
1. Single token emit processing (lines 457-480)
2. Multi-token emission in list emit (lines 425-442)

The fix ensures `apply_value_regex(emit, token)` is called with the entire emit dict when `value_regex` is present, rather than `emit['value']` which doesn't exist.

All 46 tests now pass.
