"""
Tests for Feature: Sequence matching
"""
import json
import os
import subprocess
import sys

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_a_sequence_of_tokens_is_matched_and_emitted_as_a_single_token():
    """Scenario: A sequence of tokens is matched and emitted as a single token"""
    # Create a temporary mapping file for sequence matching
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'not'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'in'}
                    ]
                },
                'emit': {'type': 'operator', 'value': '!contains'}
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "keyword", "value": "not"},
            {"type": "whitespace", "value": " "},
            {"type": "keyword", "value": "in"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "items"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Should have 3 tokens: !contains, space, items
        assert len(output_tokens) == 3
        assert output_tokens[0]['value'] == '!contains'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'items'
    finally:
        os.unlink(mapping_file)


def test_a_sequence_of_tokens_is_matched_and_discarded_entirely():
    """Scenario: A sequence of tokens is matched and discarded entirely"""
    # Create a temporary mapping file for sequence matching with discard
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'comment', 'value': '#'},
                        {'type': 'whitespace'},
                        {'type': 'comment', 'value': 'TODO'}
                    ]
                },
                'emit': 'discard'
            },
            {
                'match': {'type': 'comment'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "comment", "value": "#"},
            {"type": "whitespace", "value": " "},
            {"type": "comment", "value": "TODO"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "fix later"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Should have 3 tokens: only the ones after the sequence (space, identifier)
        assert len(output_tokens) == 2
        assert output_tokens[0]['value'] == ' '
        assert output_tokens[1]['value'] == 'fix later'
    finally:
        os.unlink(mapping_file)


def test_a_sequence_rule_takes_priority_over_a_single_token_rule_for_the_first_token_in_the_sequence():
    """Scenario: A sequence rule takes priority over a single-token rule for the first token in the sequence"""
    import tempfile
    import yaml
    
    # A sequence rule for "not in" and a single-token rule for "not" alone
    # When "not" appears as part of "not in", the sequence rule should win
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'not'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'in'}
                    ]
                },
                'emit': {'type': 'operator', 'value': '!contains'}
            },
            {
                'match': {'type': 'keyword', 'value': 'not'},
                'emit': {'type': 'operator', 'value': '!'}
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream with "not in" sequence
        tokens = [
            {"type": "keyword", "value": "not"},
            {"type": "whitespace", "value": " "},
            {"type": "keyword", "value": "in"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "x"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The sequence "not in" should be replaced by "!contains"
        # Plus the whitespace and identifier
        assert len(output_tokens) == 3
        assert output_tokens[0]['value'] == '!contains'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'x'
    finally:
        os.unlink(mapping_file)


def test_single_token_rule_applies_when_sequence_context_is_not_present():
    """Scenario: Single-token rule applies when sequence context is not present"""
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'not'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'in'}
                    ]
                },
                'emit': {'type': 'operator', 'value': '!contains'}
            },
            {
                'match': {'type': 'keyword', 'value': 'not'},
                'emit': {'type': 'operator', 'value': '!'}
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream with standalone "not" (not followed by " in")
        tokens = [
            {"type": "keyword", "value": "not"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "x"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The standalone "not" should be matched by the single-token rule
        assert output_tokens[0]['value'] == '!'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'x'
    finally:
        os.unlink(mapping_file)


def test_sequence_rule_does_not_match_when_the_stream_ends_before_the_sequence_is_complete():
    """Scenario: Sequence rule does not match when the stream ends before the sequence is complete"""
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'not'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'in'}
                    ]
                },
                'emit': {'type': 'operator', 'value': '!contains'}
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream ends with just "not" - the sequence is incomplete
        tokens = [
            {"type": "keyword", "value": "not"},
            {"type": "whitespace", "value": " "}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Since sequence didn't match, individual rules should apply
        assert len(output_tokens) == 2
        assert output_tokens[0]['value'] == 'not'
        assert output_tokens[1]['value'] == ' '
    finally:
        os.unlink(mapping_file)


def test_pass_through_on_a_sequence_rule_keeps_all_matched_tokens_and_injects_around_them():
    """Scenario: pass_through on a sequence rule keeps all matched tokens and injects around them"""
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'def'},
                        {'type': 'whitespace'},
                        {'type': 'identifier', 'value': 'foo'}
                    ]
                },
                'emit': 'pass'  # Keep all matched tokens
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'identifier'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream with "def foo" sequence
        tokens = [
            {"type": "keyword", "value": "def"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "foo"},
            {"type": "punctuation", "value": ":"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # All tokens should be preserved exactly as they were
        assert len(output_tokens) == 4
        assert output_tokens[0]['value'] == 'def'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'foo'
        assert output_tokens[3]['value'] == ':'
    finally:
        os.unlink(mapping_file)


def test_followed_by_on_a_sequence_rule_checks_the_token_after_the_last_element_of_the_sequence():
    """Scenario: followed_by on a sequence rule checks the token after the last element of the sequence"""
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'not'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'in'}
                    ],
                    'followed_by': {'type': 'whitespace', 'value': 'in'}
                },
                'emit': {'type': 'operator', 'value': '!contains'}
            },
            {
                'match': {'type': 'keyword', 'value': 'not'},
                'emit': {'type': 'operator', 'value': '!'}
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream where "not in" is followed by "in" keyword
        tokens = [
            {"type": "keyword", "value": "not"},
            {"type": "whitespace", "value": " "},
            {"type": "keyword", "value": "in"},
            {"type": "whitespace", "value": " "},
            {"type": "keyword", "value": "in"}  # This should satisfy followed_by
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The sequence with followed_by match should be replaced
        assert output_tokens[0]['value'] == '!contains'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'in'
    finally:
        os.unlink(mapping_file)


def test_emit_value_interpolates_a_specific_token_value_from_a_matched_sequence():
    """Scenario: Emit value interpolates a specific token's value from a matched sequence"""
    import tempfile
    import yaml
    
    mapping = {
        'rules': [
            {
                'match': {
                    'sequence': [
                        {'type': 'keyword', 'value': 'from'},
                        {'type': 'whitespace'},
                        {'type': 'identifier'},
                        {'type': 'whitespace'},
                        {'type': 'keyword', 'value': 'import'}
                    ]
                },
                'emit': [
                    {'type': 'keyword', 'value': 'import'},
                    {'type': 'whitespace', 'value': ' '},
                    {'type': 'identifier', 'value': '{{tokens[2].value}}'},
                    {'type': 'punctuation', 'value': '.'},
                    {'type': 'keyword', 'value': 'function'}
                ]
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'identifier'},
                'value': 'pass'
            },
            {
                'match': {'type': 'punctuation'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        # Token stream: "from os import path" -> should become "import os.function"
        tokens = [
            {"type": "keyword", "value": "from"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "os"},
            {"type": "whitespace", "value": " "},
            {"type": "keyword", "value": "import"},
            {"type": "identifier", "value": "path"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Should have: import, space, os, dot, function (then path passes through)
        assert len(output_tokens) == 6
        assert output_tokens[0]['value'] == 'import'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'os'  # {{tokens[2].value}} interpolated from sequence
        assert output_tokens[3]['value'] == '.'
        assert output_tokens[4]['value'] == 'function'
        assert output_tokens[5]['value'] == 'path'
    finally:
        os.unlink(mapping_file)