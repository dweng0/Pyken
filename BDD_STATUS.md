# BDD Status

Checked 68 scenario(s) across 16 test file(s).


## Feature: Accept token stream input

- [x] Read JSON token stream from stdin
- [x] Read JSON token stream from a file
- [x] Invalid JSON input exits with a clear error
- [x] Input file not found exits with a clear error
- [x] Token stream that is valid JSON but not an array exits with a clear error
- [x] Empty token stream produces empty output

## Feature: Apply token mapping

- [x] Mapped token value is replaced
- [x] Mapped token type is replaced
- [x] Unmapped token passes through unchanged in non-strict mode
- [x] Unmapped token causes failure in strict mode
- [x] Discarded token does not trigger strict mode failure

## Feature: Output modes

- [x] Default output reconstructs source text
- [x] --tokens flag outputs a JSON token stream
- [x] Token stream output from one invocation is valid input to another

## Feature: Mapping configuration

- [x] Map a token by type and value
- [x] Map a token by type only
- [x] More specific rules take priority over general rules
- [x] Map a token by value only regardless of type

## Feature: Bundled mappings

- [x] Python-to-JavaScript mapping remaps def to function
- [x] JavaScript-to-TypeScript mapping passes through valid tokens
- [x] Python-to-pseudocode mapping replaces keywords with plain English

## Feature: Discard tokens

- [x] Discard emit removes the token from output
- [x] Discarded token does not appear in token stream output

## Feature: Multi-token emission

- [x] A single matched token emits multiple tokens in token stream output
- [x] Multi-token emission appears correctly in reconstructed source text

## Feature: Context-aware matching

- [x] A token is matched by type, value, and preceding token type and value
- [x] Context-aware rules take priority over context-free rules for the same token
- [x] Context-free rule applies when context does not match
- [x] preceded_by does not match when the token is first in the stream
- [x] preceded_by and followed_by can be combined in a single rule

## Feature: Sequence matching

- [x] A sequence of tokens is matched and emitted as a single token
- [x] A sequence of tokens is matched and discarded entirely
- [x] A sequence rule takes priority over a single-token rule for the first token in the sequence
- [x] Single-token rule applies when sequence context is not present
- [x] Sequence rule does not match when the stream ends before the sequence is complete
- [x] pass_through on a sequence rule keeps all matched tokens and injects around them
- [x] followed_by on a sequence rule checks the token after the last element of the sequence

## Feature: Token injection

- [x] Tokens are injected after a matched token without replacing it
- [x] Tokens are injected before a matched token without replacing it
- [x] Injection appears correctly in token stream output
- [x] Injection can be combined with token value replacement

## Feature: Lookahead context matching

- [x] A token is matched by type, value, and following token type and value
- [ ] UNCOVERED: Lookahead rules take priority over context-free rules for the same token
- [x] Context-free rule applies when lookahead context does not match

## Feature: Negative context matching

- [ ] UNCOVERED: not_followed_by prevents a rule matching when the excluded token follows
- [ ] UNCOVERED: not_followed_by rule matches when the excluded token is absent
- [ ] UNCOVERED: not_preceded_by prevents a rule matching when the excluded token precedes
- [ ] UNCOVERED: not_preceded_by and not_followed_by can be combined in a single rule

## Feature: Value transforms in emit

- [x] Emit value interpolates the matched token's original value
- [x] Emit value interpolates a specific token's value from a matched sequence
- [ ] UNCOVERED: Emit value_regex applies a substitution pattern to the original token value
- [ ] UNCOVERED: value_regex with no match leaves the token value unchanged

## Feature: Mapping file validation

- [ ] UNCOVERED: Rule with an unknown emit mode exits with a clear error
- [ ] UNCOVERED: Rule missing a match block is skipped with a warning
- [x] Mapping file with no rules key processes all tokens as unmapped

## Feature: Emit mode validation

- [ ] UNCOVERED: Unknown emit string is rejected with a clear error
- [ ] UNCOVERED: Valid emit string values are accepted
- [ ] UNCOVERED: Emit as a dict with unrecognised keys is rejected

## Feature: Token shape validation

- [ ] UNCOVERED: Token missing the value key exits with a clear error
- [ ] UNCOVERED: Token missing the type key exits with a clear error
- [ ] UNCOVERED: Token that is not a JSON object exits with a clear error

## Feature: Rule matching performance

- [ ] UNCOVERED: Indexed rule lookup produces the same results as linear scan

## Feature: Shared test utilities

- [ ] UNCOVERED: Tests import shared helpers instead of redefining them

## Feature: Search tool filtering

- [ ] UNCOVERED: search_files excludes .git directory from results
- [ ] UNCOVERED: search_files excludes node_modules and __pycache__ from results

## Feature: CLI error handling

- [x] Missing mapping file argument prints usage and exits non-zero
- [x] Mapping file not found exits with a clear error
- [x] Invalid YAML mapping file exits with a clear error

---
**49/68 scenarios covered.**

19 scenario(s) need tests:
- Lookahead rules take priority over context-free rules for the same token
- not_followed_by prevents a rule matching when the excluded token follows
- not_followed_by rule matches when the excluded token is absent
- not_preceded_by prevents a rule matching when the excluded token precedes
- not_preceded_by and not_followed_by can be combined in a single rule
- Emit value_regex applies a substitution pattern to the original token value
- value_regex with no match leaves the token value unchanged
- Rule with an unknown emit mode exits with a clear error
- Rule missing a match block is skipped with a warning
- Unknown emit string is rejected with a clear error
- Valid emit string values are accepted
- Emit as a dict with unrecognised keys is rejected
- Token missing the value key exits with a clear error
- Token missing the type key exits with a clear error
- Token that is not a JSON object exits with a clear error
- Indexed rule lookup produces the same results as linear scan
- Tests import shared helpers instead of redefining them
- search_files excludes .git directory from results
- search_files excludes node_modules and __pycache__ from results
