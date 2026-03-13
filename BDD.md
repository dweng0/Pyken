---
language: python
framework: none
build_cmd: python3 -m py_compile pyken.py mapper/mapper.py
test_cmd: .venv/bin/pytest tests/ -v
lint_cmd: echo 'lint not configured'
fmt_cmd: echo 'format not configured'
birth_date: 2026-03-13
---

You must only write code and tests that meet the features and scenarios of this behaviour driven development document.

System: A token stream transformer that accepts a JSON array of typed tokens and applies a YAML mapping configuration to remap token values, enabling token-level transpilation between languages or dialects.

    Feature: Accept token stream input
        As a developer
        I want to pipe a JSON token stream into Pyken
        So that I can transform tokens without coupling to a specific tokenizer

        Scenario: Read JSON token stream from stdin
            Given a valid JSON token stream on stdin
            When I run pyken.py with a mapping file
            Then the tokens are read and processed successfully

        Scenario: Read JSON token stream from a file
            Given a valid JSON token stream saved to a file
            When I run pyken.py with --input pointing to that file
            Then the tokens are read and processed successfully

        Scenario: Invalid JSON input exits with a clear error
            Given stdin contains malformed JSON
            When I run pyken.py with a mapping file
            Then the exit code is non-zero
            And an error message describing the JSON parse failure is printed to stderr

    Feature: Apply token mapping
        As a developer
        I want tokens to be remapped according to a YAML mapping file
        So that I can transform source code from one language to another

        Scenario: Mapped token value is replaced
            Given a token stream containing a token with type "keyword" and value "def"
            And a mapping that maps "def" to "function"
            When I run pyken.py
            Then the output contains "function" where "def" appeared
            And the original "def" does not appear in the output

        Scenario: Mapped token type is replaced
            Given a token stream containing a token with type "keyword"
            And a mapping that remaps all tokens of type "keyword" to type "reserved"
            When I run pyken.py
            Then the output tokens have type "reserved" instead of "keyword"

        Scenario: Unmapped token passes through unchanged in non-strict mode
            Given a token stream containing a token with no matching mapping rule
            When I run pyken.py without --strict
            Then the token appears in the output unchanged
            And a warning is printed to stderr

        Scenario: Unmapped token causes failure in strict mode
            Given a token stream containing a token with no matching mapping rule
            When I run pyken.py with --strict
            Then the exit code is non-zero
            And an error message identifies the unmapped token

    Feature: Output modes
        As a developer
        I want to choose between source text and token stream output
        So that I can use Pyken both as an end-stage transpiler and as a pipeline step

        Scenario: Default output reconstructs source text
            Given a token stream
            And a mapping file
            When I run pyken.py without --tokens
            Then stdout contains the reconstructed source text
            And it is not JSON

        Scenario: --tokens flag outputs a JSON token stream
            Given a token stream
            And a mapping file
            When I run pyken.py with --tokens
            Then stdout is a valid JSON array of tokens
            And each token has a "type" and "value" field

    Feature: Mapping configuration
        As a developer
        I want to write YAML mapping files that define remapping rules
        So that I can configure Pyken for any language pair

        Scenario: Map a token by type and value
            Given a mapping file with a rule matching type "keyword" and value "def"
            When a token with type "keyword" and value "def" is processed
            Then the rule is applied to that token

        Scenario: Map a token by type only
            Given a mapping file with a rule matching only type "whitespace"
            When any token with type "whitespace" is processed regardless of value
            Then the rule is applied to that token

        Scenario: More specific rules take priority over general rules
            Given a mapping file with a rule for type "keyword" value "def" and a rule for type "keyword"
            When a token with type "keyword" and value "def" is processed
            Then the more specific rule (type + value) is applied

    Feature: Bundled mappings
        As a developer
        I want ready-made mapping files for common language pairs
        So that I can try Pyken immediately without writing configuration

        Scenario: Python-to-JavaScript mapping remaps def to function
            Given the bundled python-to-javascript.yaml mapping
            And a token stream containing Python keyword "def"
            When I run pyken.py with the bundled mapping
            Then the output contains "function" in place of "def"

        Scenario: JavaScript-to-TypeScript mapping passes through valid tokens
            Given the bundled javascript-to-typescript.yaml mapping
            And a token stream of basic JavaScript tokens
            When I run pyken.py with the bundled mapping
            Then the output is valid and all tokens are accounted for

        Scenario: Python-to-pseudocode mapping replaces keywords with plain English
            Given the bundled python-to-pseudocode.yaml mapping
            And a token stream containing Python keywords
            When I run pyken.py with the bundled mapping
            Then keywords are replaced with plain English equivalents

    Feature: Discard tokens
        As a developer
        I want to drop specific tokens from the output entirely
        So that I can remove source language constructs that have no equivalent in the target language

        Scenario: Discard emit removes the token from output
            Given a token stream containing a token with type "punctuation" and value ":"
            And a mapping rule that matches that token with emit: discard
            When I run pyken.py
            Then the output does not contain ":"
            And no warning is printed for the discarded token

        Scenario: Discarded token does not appear in token stream output
            Given a token stream containing a token with emit: discard in the mapping
            When I run pyken.py with --tokens
            Then the discarded token does not appear in the output JSON array

    Feature: Multi-token emission
        As a developer
        I want a single matched token to expand into multiple output tokens
        So that I can represent source constructs that require more tokens in the target language

        Scenario: A single matched token emits multiple tokens in token stream output
            Given a token stream containing a token with type "indent"
            And a mapping rule that emits two tokens: a punctuation "{" and a newline
            When I run pyken.py with --tokens
            Then the output JSON array contains two tokens where the original single token was

        Scenario: Multi-token emission appears correctly in reconstructed source text
            Given a single matched token that emits multiple tokens via a mapping rule
            When I run pyken.py without --tokens
            Then the reconstructed source text contains the values of all emitted tokens in order

    Feature: Context-aware matching
        As a developer
        I want to match tokens based on the token immediately before them
        So that I can apply different rules to the same token type and value depending on context

        Scenario: A token is matched by type, value, and preceding token type and value
            Given a token ":" of type "punctuation" immediately preceded by a ")" of type "punctuation"
            And a mapping rule that matches type "punctuation" value ":" with preceded_by type "punctuation" value ")"
            When I run pyken.py
            Then the context-aware rule is applied to that token

        Scenario: Context-aware rules take priority over context-free rules for the same token
            Given a mapping with a context-aware rule and a general rule both matching the same token type and value
            When the token appears in the context that satisfies the context-aware rule
            Then the context-aware rule is applied rather than the general rule

        Scenario: Context-free rule applies when context does not match
            Given a mapping with a context-aware rule for ":" preceded by ")" and a pass-through rule for ":"
            When ":" appears not preceded by ")"
            Then the pass-through rule is applied and the token is unchanged

    Feature: Sequence matching
        As a developer
        I want to match a run of consecutive tokens as a single pattern
        So that I can remap multi-token constructs that have no single-token equivalent in the target language

        Scenario: A sequence of tokens is matched and emitted as a single token
            Given a token stream containing "not" followed by whitespace followed by "in"
            And a mapping rule with a sequence match for those three tokens that emits a single operator token "not in"
            When I run pyken.py
            Then the output contains "not in" as a single unit
            And the original three tokens do not appear separately in the output

        Scenario: A sequence of tokens is matched and discarded entirely
            Given a token stream containing ":" followed by an identifier representing a type annotation
            And a mapping rule with a sequence match for those two tokens that emits discard
            When I run pyken.py
            Then neither token appears in the output
            And no warning is printed for the discarded sequence

        Scenario: A sequence rule takes priority over a single-token rule for the first token in the sequence
            Given a mapping with a sequence rule starting with "not" and a single-token rule also matching "not"
            When the token "not" appears followed by the rest of the sequence
            Then the sequence rule is applied rather than the single-token rule

        Scenario: Single-token rule applies when sequence context is not present
            Given a mapping with a sequence rule for "not" followed by "in" and a single-token rule for "not"
            When "not" appears without being followed by whitespace and "in"
            Then the single-token rule is applied

    Feature: Token injection
        As a developer
        I want to inject new tokens before or after a matched token while keeping the original
        So that I can add target-language constructs that have no source-language equivalent

        Scenario: Tokens are injected after a matched token without replacing it
            Given a token stream containing an identifier preceded by "("
            And a mapping rule that matches that identifier and injects ": any" tokens after it
            When I run pyken.py
            Then the output contains the original identifier immediately followed by the injected tokens

        Scenario: Tokens are injected before a matched token without replacing it
            Given a token stream containing a keyword
            And a mapping rule that injects tokens before that keyword
            When I run pyken.py
            Then the output contains the injected tokens immediately before the original keyword

        Scenario: Injection appears correctly in token stream output
            Given a mapping rule that injects tokens after a matched token
            When I run pyken.py with --tokens
            Then the output JSON array contains the injected tokens in the correct position relative to the original token

    Feature: Lookahead context matching
        As a developer
        I want to match a token based on the token that immediately follows it
        So that I can apply different rules to the same token depending on what comes after it

        Scenario: A token is matched by type, value, and following token type and value
            Given a token "{" of type "punctuator" immediately followed by a newline token
            And a mapping rule that matches type "punctuator" value "{" with followed_by type "newline"
            When I run pyken.py
            Then the followed_by rule is applied to that token

        Scenario: Lookahead rules take priority over context-free rules for the same token
            Given a mapping with a followed_by rule and a general rule both matching the same token
            When the token appears followed by the token specified in followed_by
            Then the followed_by rule is applied rather than the general rule

        Scenario: Context-free rule applies when lookahead context does not match
            Given a mapping with a followed_by rule for "{" followed by newline and a pass-through rule for "{"
            When "{" appears not followed by a newline
            Then the pass-through rule is applied and the token is unchanged

    Feature: CLI error handling
        As a developer
        I want clear error messages when I misuse Pyken
        So that I can quickly understand and fix the problem

        Scenario: Missing mapping file argument prints usage and exits non-zero
            Given I run pyken.py with no arguments
            Then the exit code is non-zero
            And a usage message is printed to stderr

        Scenario: Mapping file not found exits with a clear error
            Given I run pyken.py with a path to a mapping file that does not exist
            Then the exit code is non-zero
            And an error message mentioning the missing file is printed to stderr

        Scenario: Invalid YAML mapping file exits with a clear error
            Given I run pyken.py with a mapping file containing invalid YAML
            Then the exit code is non-zero
            And an error message describing the YAML parse failure is printed to stderr
