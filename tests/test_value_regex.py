"""
Tests for Feature: Value transforms in emit
"""
import json
import os
import subprocess
import sys
import tempfile
import yaml

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_emit_value_regex_applies_a_substitution_pattern_to_the_original_token_value():
    """Scenario: Emit value_regex applies a substitution pattern to the original token value"""
    import re
    
    mapping = {
        'rules': [
            {
                'match': {'type': 'string', 'value': "'hello'"},
                'emit': {
                    'type': 'string',
                    'value_regex': {
                        'pattern': "^'(.*?)'$",
                        'replacement': '"\\1"'
                    }
                }
            },
            {
                'match': {'type': 'string'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "string", "value": "'hello'"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The single quotes should be replaced with double quotes
        assert len(output_tokens) == 1
        assert output_tokens[0]['value'] == '"hello"'
    finally:
        os.unlink(mapping_file)


def test_value_regex_with_no_match_leaves_the_token_value_unchanged():
    """Scenario: value_regex with no match leaves the token value unchanged"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'foo'},
                'emit': {
                    'type': 'keyword',
                    'value_regex': {
                        'pattern': "^bar$",
                        'replacement': "baz"
                    }
                }
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "keyword", "value": "foo"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Since the regex didn't match, the value should be unchanged
        assert len(output_tokens) == 1
        assert output_tokens[0]['value'] == 'foo'
    finally:
        os.unlink(mapping_file)


def test_emit_value_regex_with_interpolation():
    """Scenario: value_regex with interpolation - use matched token value in regex pattern"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'foo'},
                'emit': {
                    'type': 'keyword',
                    'value_regex': {
                        'pattern': "^foo$",
                        'replacement': "{{value}}bar"
                    }
                }
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "keyword", "value": "foo"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Since the regex matches, should apply substitution: {{value}}bar
        assert len(output_tokens) == 1
        assert output_tokens[0]['value'] == 'foobar'
    finally:
        os.unlink(mapping_file)
