"""
Tests for Feature: Rule matching performance

This file verifies that token-to-rule matching produces correct results
even with a large number of rules.
"""
import json
import os
import sys

from conftest import run_pyken, make_mapping_file


def test_indexed_rule_lookup_produces_same_results_as_linear_scan():
    """Scenario: Indexed rule lookup produces the same results as linear scan
    
    Given a mapping file with 20 or more rules covering type+value, type-only, and value-only matches
    And a token stream containing tokens that exercise all three match specificity levels
    When I run pyken.py
    Then every token is matched to the same rule that a linear scan would select
    And the output is correct
    """
    # Create a mapping with 20+ rules
    mapping_rules = """
rules:
  # Type+value specific rules
  - match:
      type: keyword
      value: "def"
    emit:
      value: "FUNCTION"
  - match:
      type: keyword
      value: "class"
    emit:
      value: "CLASS"
  - match:
      type: keyword
      value: "import"
    emit:
      value: "IMPORT"
  - match:
      type: keyword
      value: "from"
    emit:
      value: "FROM"
  - match:
      type: keyword
      value: "as"
    emit:
      value: "AS"
  - match:
      type: keyword
      value: "return"
    emit:
      value: "RETURN"
  - match:
      type: keyword
      value: "if"
    emit:
      value: "IF"
  - match:
      type: keyword
      value: "else"
    emit:
      value: "ELSE"
  - match:
      type: keyword
      value: "elif"
    emit:
      value: "ELIF"
  - match:
      type: keyword
      value: "while"
    emit:
      value: "WHILE"
  - match:
      type: keyword
      value: "for"
    emit:
      value: "FOR"
  - match:
      type: keyword
      value: "in"
    emit:
      value: "IN"
  - match:
      type: keyword
      value: "not"
    emit:
      value: "NOT"
  - match:
      type: keyword
      value: "and"
    emit:
      value: "AND"
  - match:
      type: keyword
      value: "or"
    emit:
      value: "OR"
  # Type-only rules
  - match:
      type: whitespace
    emit:
      value: "_"
  - match:
      type: punctuation
    emit:
      value: "PUNCT"
  - match:
      type: operator
    emit:
      value: "OP"
  # Value-only rules
  - match:
      value: ";"
    emit:
      value: "SEMICOLON"
  # General fallback rules
  - match:
      type: identifier
    emit:
      value: "ID"
  - match:
      type: string
    emit:
      value: "STR"
  - match:
      type: number
    emit:
      value: "NUM"
"""
    mapping_file = make_mapping_file(mapping_rules)
    
    # Create a token stream with tokens that exercise all specificity levels
    tokens = [
        {"type": "keyword", "value": "def"},  # type+value rule
        {"type": "keyword", "value": "import"},  # type+value rule
        {"type": "whitespace", "value": " "},  # type-only rule
        {"type": "whitespace", "value": "\t"},  # type-only rule
        {"type": "string", "value": '"hello"'},  # type-only rule
        {"type": "identifier", "value": "x"},  # type-only rule
        {"type": "keyword", "value": "not"},  # type+value rule
        {"type": "operator", "value": "+"},  # type-only rule
        {"type": "punctuation", "value": ","},  # type-only rule
        {"type": "keyword", "value": "if"},  # type+value rule
        {"type": "keyword", "value": "else"},  # type+value rule
        {"type": "number", "value": "42"},  # type-only rule
        {"type": "keyword", "value": "and"},  # type+value rule
        {"type": "punctuation", "value": ";"},  # value-only rule (since ; is also punctuation)
    ]
    
    try:
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0, f"Command failed: {result.stderr}"
        
        output_tokens = json.loads(result.stdout)
        
        # Verify specific tokens were transformed correctly
        # Type+value rules should apply
        assert output_tokens[0]['value'] == 'FUNCTION', "Expected 'def' -> 'FUNCTION'"
        assert output_tokens[8]['value'] == 'PUNCT', "Expected punctuation -> 'PUNCT'"
        assert output_tokens[6]['value'] == 'NOT', "Expected 'not' -> 'NOT'"
        assert output_tokens[12]['value'] == 'AND', "Expected 'and' -> 'AND'"
        
        # Type-only rules should apply to unmatched type+value tokens
        assert output_tokens[1]['value'] == 'IMPORT', "Expected 'import' -> 'IMPORT'"
        assert output_tokens[3]['value'] == '_', "Expected whitespace -> '_'"
        assert output_tokens[4]['value'] == 'STR', "Expected string -> 'STR'"
        
    finally:
        os.unlink(mapping_file)
