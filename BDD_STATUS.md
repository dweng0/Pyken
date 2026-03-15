# BDD Status

Checked 58 scenario(s) across 7 test file(s).


## Feature: Accept token stream input

- [x] Read JSON token stream from stdin
- [x] Read JSON token stream from a file
- [x] Invalid JSON input exits with a clear error
- [x] Input file not found exits with a clear error
- [x] Token stream that is valid JSON but not an array exits with a clear error
- [ ] UNCOVERED: Empty token stream produces empty output

## Feature: Apply token mapping

- [x] Mapped token value is replaced
- [x] Mapped token type is replaced
- [x] Unmapped token passes through unchanged in non-strict mode
- [x] Unmapped token causes failure in strict mode
- [ ] UNCOVERED: Discarded token does not trigger strict mode failure

## Feature: Output modes

- [x] Default output reconstructs source text
- [x] --tokens flag outputs a JSON token stream
- [x] Token stream output from one invocation is valid input to another

## Feature: Mapping configuration

- [x] Map a token by type and value
- [x] Map a token by type only
- [x] More specific rules take priority over general rules
- [ ] UNCOVERED: Map a token by value only regardless of type

## Feature: Bundled mappings

- [ ] UNCOVERED: Python-to-JavaScript mapping remaps def to function
- [ ] UNCOVERED: JavaScript-to-TypeScript mapping passes through valid tokens
- [ ] UNCOVERED: Python-to-pseudocode mapping replaces keywords with plain English

## Feature: Discard tokens

- [ ] UNCOVERED: Discard emit removes the token from output
- [ ] UNCOVERED: Discarded token does not appear in token stream output

## Feature: Multi-token emission

- [ ] UNCOVERED: A single matched token emits multiple tokens in token stream output
- [ ] UNCOVERED: Multi-token emission appears correctly in reconstructed source text

## Feature: Context-aware matching

- [ ] UNCOVERED: A token is matched by type, value, and preceding token type and value
- [ ] UNCOVERED: Context-aware rules take priority over context-free rules for the same token
- [ ] UNCOVERED: Context-free rule applies when context does not match
- [ ] UNCOVERED: preceded_by does not match when the token is first in the stream
- [ ] UNCOVERED: preceded_by and followed_by can be combined in a single rule

## Feature: Sequence matching

- [ ] UNCOVERED: A sequence of tokens is matched and emitted as a single token
- [ ] UNCOVERED: A sequence of tokens is matched and discarded entirely
- [ ] UNCOVERED: A sequence rule takes priority over a single-token rule for the first token in the sequence
- [ ] UNCOVERED: Single-token rule applies when sequence context is not present
- [ ] UNCOVERED: Sequence rule does not match when the stream ends before the sequence is complete
- [ ] UNCOVERED: pass_through on a sequence rule keeps all matched tokens and injects around them
- [ ] UNCOVERED: followed_by on a sequence rule checks the token after the last element of the sequence

## Feature: Token injection

- [ ] UNCOVERED: Tokens are injected after a matched token without replacing it
- [ ] UNCOVERED: Tokens are injected before a matched token without replacing it
- [ ] UNCOVERED: Injection appears correctly in token stream output
- [ ] UNCOVERED: Injection can be combined with token value replacement

## Feature: Lookahead context matching

- [ ] UNCOVERED: A token is matched by type, value, and following token type and value
- [ ] UNCOVERED: Lookahead rules take priority over context-free rules for the same token
- [ ] UNCOVERED: Context-free rule applies when lookahead context does not match

## Feature: Negative context matching

- [ ] UNCOVERED: not_followed_by prevents a rule matching when the excluded token follows
- [ ] UNCOVERED: not_followed_by rule matches when the excluded token is absent
- [ ] UNCOVERED: not_preceded_by prevents a rule matching when the excluded token precedes
- [ ] UNCOVERED: not_preceded_by and not_followed_by can be combined in a single rule

## Feature: Value transforms in emit

- [ ] UNCOVERED: Emit value interpolates the matched token's original value
- [ ] UNCOVERED: Emit value interpolates a specific token's value from a matched sequence
- [ ] UNCOVERED: Emit value_regex applies a substitution pattern to the original token value
- [ ] UNCOVERED: value_regex with no match leaves the token value unchanged

## Feature: Mapping file validation

- [ ] UNCOVERED: Rule with an unknown emit mode exits with a clear error
- [ ] UNCOVERED: Rule missing a match block is skipped with a warning
- [x] Mapping file with no rules key processes all tokens as unmapped

## Feature: CLI error handling

- [x] Missing mapping file argument prints usage and exits non-zero
- [x] Mapping file not found exits with a clear error
- [x] Invalid YAML mapping file exits with a clear error

---
**19/58 scenarios covered.**

39 scenario(s) need tests:
- Empty token stream produces empty output
- Discarded token does not trigger strict mode failure
- Map a token by value only regardless of type
- Python-to-JavaScript mapping remaps def to function
- JavaScript-to-TypeScript mapping passes through valid tokens
- Python-to-pseudocode mapping replaces keywords with plain English
- Discard emit removes the token from output
- Discarded token does not appear in token stream output
- A single matched token emits multiple tokens in token stream output
- Multi-token emission appears correctly in reconstructed source text
- A token is matched by type, value, and preceding token type and value
- Context-aware rules take priority over context-free rules for the same token
- Context-free rule applies when context does not match
- preceded_by does not match when the token is first in the stream
- preceded_by and followed_by can be combined in a single rule
- A sequence of tokens is matched and emitted as a single token
- A sequence of tokens is matched and discarded entirely
- A sequence rule takes priority over a single-token rule for the first token in the sequence
- Single-token rule applies when sequence context is not present
- Sequence rule does not match when the stream ends before the sequence is complete
- pass_through on a sequence rule keeps all matched tokens and injects around them
- followed_by on a sequence rule checks the token after the last element of the sequence
- Tokens are injected after a matched token without replacing it
- Tokens are injected before a matched token without replacing it
- Injection appears correctly in token stream output
- Injection can be combined with token value replacement
- A token is matched by type, value, and following token type and value
- Lookahead rules take priority over context-free rules for the same token
- Context-free rule applies when lookahead context does not match
- not_followed_by prevents a rule matching when the excluded token follows
- not_followed_by rule matches when the excluded token is absent
- not_preceded_by prevents a rule matching when the excluded token precedes
- not_preceded_by and not_followed_by can be combined in a single rule
- Emit value interpolates the matched token's original value
- Emit value interpolates a specific token's value from a matched sequence
- Emit value_regex applies a substitution pattern to the original token value
- value_regex with no match leaves the token value unchanged
- Rule with an unknown emit mode exits with a clear error
- Rule missing a match block is skipped with a warning
