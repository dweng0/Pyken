import subprocess
import json
import tempfile
import os


def test_a_token_is_matched_by_type_value_and_preceding_token_type_and_value():
    """Scenario: A token is matched by type, value, and preceding token type and value
    Given a token ":" of type "punctuation" immediately preceded by a ")" of type "punctuation"
    And a mapping rule that matches type "punctuation" value ":" with preceded_by type "punctuation" value ")"
    When I run pyken.py
    Then the context-aware rule is applied to that token
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':',
                    'preceded_by': {
                        'type': 'punctuation',
                        'value': ')'
                    }
                },
                'emit': {'type': 'punctuation', 'value': ';'}
            },
            # General fallback rule for ':' that should not be applied in this context
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':'
                },
                'emit': {'type': 'punctuation', 'value': 'COLON'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream: ")" followed by ":"
    input_tokens = [
        {'type': 'punctuation', 'value': '('},
        {'type': 'punctuation', 'value': ')'}, 
        {'type': 'punctuation', 'value': ':'}
    ]
    
    try:
        # Run pyken without --tokens flag (default text output)
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # The ":" should be converted to ";" because it was preceded by ")"
        # Expected output: "();"
        assert result.stdout == '();'
        
    finally:
        os.unlink(mapping_file_path)


def test_context_aware_rules_take_priority_over_context_free_rules_for_the_same_token():
    """Scenario: Context-aware rules take priority over context-free rules for the same token
    Given a mapping with a context-aware rule and a general rule both matching the same token type and value
    When the token appears in the context that satisfies the context-aware rule
    Then the context-aware rule is applied rather than the general rule
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':',
                    'preceded_by': {
                        'type': 'punctuation',
                        'value': ')'
                    }
                },
                'emit': {'type': 'punctuation', 'value': 'CONTEXT_COLON'}
            },
            # General fallback rule for ':' 
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':'
                },
                'emit': {'type': 'punctuation', 'value': 'GENERAL_COLON'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream: ")" followed by ":"
    input_tokens = [
        {'type': 'punctuation', 'value': ')'}, 
        {'type': 'punctuation', 'value': ':'}
    ]
    
    try:
        # Run pyken without --tokens flag (default text output)
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # The ":" should be converted to "CONTEXT_COLON" because context-aware rule has priority
        assert result.stdout == ')CONTEXT_COLON'
        
    finally:
        os.unlink(mapping_file_path)


def test_context_free_rule_applies_when_context_does_not_match():
    """Scenario: Context-free rule applies when context does not match
    Given a mapping with a context-aware rule for ":" preceded by ")" and a pass-through rule for ":"
    When ":" appears not preceded by ")"
    Then the pass-through rule is applied and the token is unchanged
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':',
                    'preceded_by': {
                        'type': 'punctuation',
                        'value': ')'
                    }
                },
                'emit': {'type': 'punctuation', 'value': 'CONTEXT_COLON'}
            },
            # General fallback rule for ':' 
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':'
                },
                'emit': {'type': 'punctuation', 'value': 'GENERAL_COLON'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream: "(" followed by ":" (so context doesn't match)
    input_tokens = [
        {'type': 'punctuation', 'value': '('}, 
        {'type': 'punctuation', 'value': ':'}
    ]
    
    try:
        # Run pyken without --tokens flag (default text output)
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # The ":" should be converted to "GENERAL_COLON" because context doesn't match
        assert result.stdout == '(GENERAL_COLON'
        
    finally:
        os.unlink(mapping_file_path)


def test_preceded_by_does_not_match_when_the_token_is_first_in_the_stream():
    """Scenario: preceded_by does not match when the token is first in the stream
    Given a token stream where the first token would match a preceded_by rule if it had a predecessor
    When I run pyken.py
    Then the preceded_by rule is not applied to the first token
    And the next applicable rule is used instead
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':',
                    'preceded_by': {
                        'type': 'punctuation',
                        'value': ')'
                    }
                },
                'emit': {'type': 'punctuation', 'value': 'CONTEXT_COLON'}
            },
            # General fallback rule for ':' 
            {
                'match': {
                    'type': 'punctuation',
                    'value': ':'
                },
                'emit': {'type': 'punctuation', 'value': 'GENERAL_COLON'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream: just ":" as the first token (no predecessor)
    input_tokens = [
        {'type': 'punctuation', 'value': ':'}
    ]
    
    try:
        # Run pyken without --tokens flag (default text output)
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # The ":" should be converted to "GENERAL_COLON" because there's no preceding token
        assert result.stdout == 'GENERAL_COLON'
        
    finally:
        os.unlink(mapping_file_path)