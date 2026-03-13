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

        Scenario: Input file not found exits with a clear error
            Given I run pyken.py with --input pointing to a file that does not exist
            Then the exit code is non-zero
            And an error message mentioning the missing input file is printed to stderr

        Scenario: Token stream that is valid JSON but not an array exits with a clear error
            Given stdin contains valid JSON that is not an array
            When I run pyken.py with a mapping file
            Then the exit code is non-zero
            And an error message stating that the token stream must be a JSON array is printed to stderr

        Scenario: Empty token stream produces empty output
            Given stdin contains an empty JSON array
            When I run pyken.py with a mapping file
            Then the exit code is zero
            And stdout is empty

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

        Scenario: Discarded token does not trigger strict mode failure
            Given a token stream containing a token that matches an emit: discard rule
            When I run pyken.py with --strict
            Then the exit code is zero
            And no error is printed for the discarded token

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

        Scenario: Token stream output from one invocation is valid input to another
            Given a token stream and a mapping file
            When I run pyken.py with --tokens and pipe the output into a second pyken.py invocation with another mapping file
            Then the final output reflects both mappings applied in sequence

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

        Scenario: Map a token by value only regardless of type
            Given a mapping file with a rule matching only value ";"
            When any token with value ";" is processed regardless of its type
            Then the rule is applied to that token

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

        Scenario: preceded_by does not match when the token is first in the stream
            Given a token stream where the first token would match a preceded_by rule if it had a predecessor
            When I run pyken.py
            Then the preceded_by rule is not applied to the first token
            And the next applicable rule is used instead

        Scenario: preceded_by and followed_by can be combined in a single rule
            Given a mapping rule with both preceded_by and followed_by conditions
            When a token matches both the preceding and following token conditions
            Then that rule is applied
            And the rule is not applied when only one condition is satisfied

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

        Scenario: Sequence rule does not match when the stream ends before the sequence is complete
            Given a token stream that ends with the first token of a sequence pattern
            And a mapping with a sequence rule for that pattern and a single-token rule for the first token
            When I run pyken.py
            Then the single-token rule is applied to the trailing token

        Scenario: pass_through on a sequence rule keeps all matched tokens and injects around them
            Given a mapping rule that matches a sequence of tokens with pass_through true and injects tokens before the sequence
            When I run pyken.py
            Then the output contains the injected tokens followed by all original sequence tokens unchanged

        Scenario: followed_by on a sequence rule checks the token after the last element of the sequence
            Given a mapping rule with a sequence and a followed_by condition
            When the sequence is present and the token immediately after the last sequence element matches the followed_by condition
            Then the sequence rule is applied
            And the rule is not applied when the token after the last sequence element does not match

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

        Scenario: Injection can be combined with token value replacement
            Given a mapping rule that replaces the matched token's value and also injects tokens before it
            When I run pyken.py
            Then the output contains the injected tokens followed by the replaced token value

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

    Feature: Negative context matching
        As a developer
        I want to match a token only when it is NOT preceded or followed by a specific token
        So that I can distinguish tokens that look identical but mean different things in context

        Scenario: not_followed_by prevents a rule matching when the excluded token follows
            Given a mapping rule for operator "=" with not_followed_by operator "="
            And a token stream containing "==" as two separate "=" tokens
            When I run pyken.py
            Then the rule is not applied to either "=" token in the "==" pair

        Scenario: not_followed_by rule matches when the excluded token is absent
            Given a mapping rule for operator "=" with not_followed_by operator "="
            And a token stream containing a standalone "=" assignment operator
            When I run pyken.py
            Then the rule is applied to the "=" token

        Scenario: not_preceded_by prevents a rule matching when the excluded token precedes
            Given a mapping rule for a token with not_preceded_by specifying a token type and value
            When that token appears immediately after the excluded token
            Then the rule is not applied

        Scenario: not_preceded_by and not_followed_by can be combined in a single rule
            Given a mapping rule with both not_preceded_by and not_followed_by conditions
            When a token satisfies neither exclusion condition
            Then the rule is applied
            And the rule is not applied when either exclusion condition is triggered

    Feature: Value transforms in emit
        As a developer
        I want to derive the emitted token's value from the matched token's original value
        So that I can perform structural transforms like import-to-include without hardcoding every possible value

        Scenario: Emit value interpolates the matched token's original value
            Given a mapping rule whose emit value contains the placeholder {{value}}
            And a token with value "os"
            When I run pyken.py
            Then the output contains the emitted value with {{value}} replaced by "os"

        Scenario: Emit value interpolates a specific token's value from a matched sequence
            Given a mapping rule that matches a sequence and whose emit value references {{tokens[2].value}}
            And a token stream where the third token in the sequence has value "stdio"
            When I run pyken.py
            Then the output contains the emitted value with {{tokens[2].value}} replaced by "stdio"

        Scenario: Emit value_regex applies a substitution pattern to the original token value
            Given a mapping rule with a value_regex pattern that matches leading single-quotes and replaces them with double-quotes
            And a token with value "'hello'"
            When I run pyken.py
            Then the output token value is "\"hello\""

        Scenario: value_regex with no match leaves the token value unchanged
            Given a mapping rule with a value_regex pattern
            And a token whose value does not match the regex pattern
            When I run pyken.py
            Then the token value is passed through unchanged

    Feature: Mapping file validation
        As a developer
        I want clear errors when my mapping file has structural problems
        So that I can fix authoring mistakes quickly instead of getting silent misbehaviour

        Scenario: Rule with an unknown emit mode exits with a clear error
            Given a mapping file containing a rule with an unrecognised emit mode
            When I run pyken.py with that mapping file
            Then the exit code is non-zero
            And an error message identifying the invalid emit mode is printed to stderr

        Scenario: Rule missing a match block is skipped with a warning
            Given a mapping file containing a rule with no match block
            When I run pyken.py with that mapping file
            Then pyken continues processing
            And a warning identifying the malformed rule is printed to stderr

        Scenario: Mapping file with no rules key processes all tokens as unmapped
            Given a mapping file that contains valid YAML but no rules key
            When I run pyken.py without --strict
            Then all tokens pass through unchanged
            And a warning is printed for each token

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
