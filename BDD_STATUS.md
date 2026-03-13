# BDD Status

Checked 18 scenario(s) across 7 test file(s).


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

## Feature: CLI error handling

- [x] Missing mapping file argument prints usage and exits non-zero
- [x] Mapping file not found exits with a clear error
- [x] Invalid YAML mapping file exits with a clear error

---
**18/18 scenarios covered.**
