"""
Tests for Feature: Token injection
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


def test_tokens_are_injected_after_a_matched_token_without_replacing_it():
    """Scenario: Tokens are injected after a matched token without replacing it"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'def'},
                'emit': [
                    {'type': 'keyword', 'value': 'def'},
                    {'type': 'whitespace', 'value': ' '},
                    {'type': 'keyword', 'value': '_func'}
                ]
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
            {"type": "keyword", "value": "def"},
            {"type": "identifier", "value": "foo"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The "def" should trigger injection: def, space, _func, then identifier
        assert len(output_tokens) == 4
        assert output_tokens[0]['value'] == 'def'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['type'] == 'keyword'
        assert output_tokens[2]['value'] == '_func'
        assert output_tokens[3]['value'] == 'foo'
    finally:
        os.unlink(mapping_file)


def test_tokens_are_injected_before_a_matched_token_without_replacing_it():
    """Scenario: Tokens are injected before a matched token without replacing it"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'def'},
                'emit': [
                    {'type': 'keyword', 'value': 'function'},
                    {'type': 'whitespace', 'value': ' '},
                    {'type': 'keyword', 'value': 'def'}
                ]
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
            {"type": "keyword", "value": "def"},
            {"type": "identifier", "value": "foo"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Should have: function, space, def, identifier
        assert len(output_tokens) == 4
        assert output_tokens[0]['value'] == 'function'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'def'
        assert output_tokens[3]['value'] == 'foo'
    finally:
        os.unlink(mapping_file)


def test_injection_appears_correctly_in_token_stream_output():
    """Scenario: Injection appears correctly in token stream output"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'not'},
                'emit': [
                    {'type': 'operator', 'value': '!'}
                ]
            },
            {
                'match': {'type': 'keyword', 'value': 'in'},
                'emit': [
                    {'type': 'keyword', 'value': 'in'}
                ]
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
            {"type": "keyword", "value": "in"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # Should have: !, space, in
        assert len(output_tokens) == 3
        assert output_tokens[0]['value'] == '!'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'in'
    finally:
        os.unlink(mapping_file)


def test_injection_can_be_combined_with_token_value_replacement():
    """Scenario: Injection can be combined with token value replacement"""
    mapping = {
        'rules': [
            {
                'match': {'type': 'keyword', 'value': 'def'},
                'emit': [
                    {'type': 'keyword', 'value': 'function'},
                    {'type': 'whitespace', 'value': ' '},
                    {'type': 'identifier', 'value': '{{value}}'}  # Interpolated from matched token
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
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(mapping, f)
        mapping_file = f.name

    try:
        tokens = [
            {"type": "keyword", "value": "def"},
            {"type": "whitespace", "value": " "},
            {"type": "identifier", "value": "foo"}
        ]
        
        result = run_pyken(mapping_file, '--tokens', input_data=json.dumps(tokens))
        assert result.returncode == 0
        
        output_tokens = json.loads(result.stdout)
        # The 'def' token triggers emission of 3 tokens, then remaining tokens pass through
        # Should have: function, space, def, space, foo
        assert len(output_tokens) == 5
        assert output_tokens[0]['value'] == 'function'
        assert output_tokens[1]['value'] == ' '
        assert output_tokens[2]['value'] == 'def'  # {{value}} interpolated from matched token
        assert output_tokens[3]['value'] == ' '
        assert output_tokens[4]['value'] == 'foo'
    finally:
        os.unlink(mapping_file)
