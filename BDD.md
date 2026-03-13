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
