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