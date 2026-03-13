# BDD Status

Checked 35 scenario(s) across 7 test file(s).


## Feature: Accept token stream input

- [x] Read JSON token stream from stdin
- [x] Read JSON token stream from a file
- [x] Invalid JSON input exits with a clear error

## Feature: Apply token mapping

- [x] Mapped token value is replaced
- [x] Mapped token type is replaced
- [x] Unmapped token passes through unchanged in non-strict mode
- [x] Unmapped token causes failure in strict mode

## Feature: Output modes

- [x] Default output reconstructs source text
- [x] --tokens flag outputs a JSON token stream

## Feature: Mapping configuration

- [x] Map a token by type and value
- [x] Map a token by type only
- [x] More specific rules take priority over general rules

## Feature: Bundled mappings

- [x] Python-to-JavaScript mapping remaps def to function
- [x] JavaScript-to-TypeScript mapping passes through valid tokens
- [x] Python-to-pseudocode mapping replaces keywords with plain English

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

## Feature: Sequence matching

- [ ] UNCOVERED: A sequence of tokens is matched and emitted as a single token
- [ ] UNCOVERED: A sequence of tokens is matched and discarded entirely
- [ ] UNCOVERED: A sequence rule takes priority over a single-token rule for the first token in the sequence
- [ ] UNCOVERED: Single-token rule applies when sequence context is not present

## Feature: Token injection

- [ ] UNCOVERED: Tokens are injected after a matched token without replacing it
- [ ] UNCOVERED: Tokens are injected before a matched token without replacing it
- [ ] UNCOVERED: Injection appears correctly in token stream output

## Feature: Lookahead context matching

- [ ] UNCOVERED: A token is matched by type, value, and following token type and value
- [ ] UNCOVERED: Lookahead rules take priority over context-free rules for the same token
- [ ] UNCOVERED: Context-free rule applies when lookahead context does not match

## Feature: CLI error handling

- [x] Missing mapping file argument prints usage and exits non-zero
- [x] Mapping file not found exits with a clear error
- [x] Invalid YAML mapping file exits with a clear error

---
**18/35 scenarios covered.**

17 scenario(s) need tests:
- Discard emit removes the token from output
- Discarded token does not appear in token stream output
- A single matched token emits multiple tokens in token stream output
- Multi-token emission appears correctly in reconstructed source text
- A token is matched by type, value, and preceding token type and value
- Context-aware rules take priority over context-free rules for the same token
- Context-free rule applies when context does not match
- A sequence of tokens is matched and emitted as a single token
- A sequence of tokens is matched and discarded entirely
- A sequence rule takes priority over a single-token rule for the first token in the sequence
- Single-token rule applies when sequence context is not present
- Tokens are injected after a matched token without replacing it
- Tokens are injected before a matched token without replacing it
- Injection appears correctly in token stream output
- A token is matched by type, value, and following token type and value
- Lookahead rules take priority over context-free rules for the same token
- Context-free rule applies when lookahead context does not match
