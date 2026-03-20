import subprocess
import json
import tempfile
import os


def test_not_followed_by_prevents_matching_when_excluded_token_follows():
    """Scenario: not_followed_by prevents a rule matching when the excluded token follows
    
    Given a mapping rule for operator "=" with not_followed_by operator "="
    When "=" is followed by "=" 
    Then the rule should not match
    """
    
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'operator',
                    'value': '=',
                    'not_followed_by': {
                        'type': 'operator',
                        'value': '='
                    }
                },
                'emit': {'type': 'operator', 'value': 'EQ_NOT_ASSIGN'}
            },
            {
                'match': {
                    'type': 'operator',
                    'value': '='
                },
                'emit': {'type': 'operator', 'value': 'GENERIC_EQ'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    input_tokens = [
        {'type': 'operator', 'value': '='},
        {'type': 'operator', 'value': '='}
    ]
    
    try:
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        # First '=' is followed by '=', so GENERIC_EQ
        # Second '=' has no next token, so EQ_NOT_NOT_ASSIGN (not preceded by '!')
        assert result.stdout == 'GENERIC_EQEQ_NOT_ASSIGN'
        
    finally:
        os.unlink(mapping_file_path)


def test_not_followed_by_rule_matches_when_excluded_token_is_absent():
    """Scenario: not_followed_by rule matches when the excluded token is absent
    
    Given a mapping rule for operator "=" with not_followed_by operator "="
    When "=" is NOT followed by "=" 
    Then the rule should match
    """
    
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'operator',
                    'value': '=',
                    'not_followed_by': {
                        'type': 'operator',
                        'value': '='
                    }
                },
                'emit': {'type': 'operator', 'value': 'EQ_NOT_ASSIGN'}
            },
            {
                'match': {
                    'type': 'operator',
                    'value': '='
                },
                'emit': {'type': 'operator', 'value': 'GENERIC_EQ'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    input_tokens = [
        {'type': 'operator', 'value': '='},
        {'type': 'identifier', 'value': 'x'}
    ]
    
    try:
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        assert result.stdout == 'EQ_NOT_ASSIGNx'
        
    finally:
        os.unlink(mapping_file_path)


def test_not_preceded_by_prevents_matching_when_excluded_token_precedes():
    """Scenario: not_preceded_by prevents a rule matching when the excluded token precedes
    
    Given a mapping rule for operator "=" with not_preceded_by operator "!"
    When "=" is preceded by "!"
    Then the rule should not match
    """
    
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'operator',
                    'value': '=',
                    'not_preceded_by': {
                        'type': 'operator',
                        'value': '!'
                    }
                },
                'emit': {'type': 'operator', 'value': 'EQ_NOT_NOT'}
            },
            {
                'match': {
                    'type': 'operator',
                    'value': '='
                },
                'emit': {'type': 'operator', 'value': 'GENERIC_EQ'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    input_tokens = [
        {'type': 'operator', 'value': '!'},
        {'type': 'operator', 'value': '='}
    ]
    
    try:
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        assert result.stdout == '!GENERIC_EQ'
        
    finally:
        os.unlink(mapping_file_path)


def test_not_preceded_by_and_not_followed_by_can_be_combined():
    """Scenario: not_preceded_by and not_followed_by can be combined in a single rule
    
    Given a mapping rule with both not_preceded_by and not_followed_by conditions
    When the token satisfies both conditions (not preceded by "!" and not followed by "=")
    Then that rule is applied
    """
    
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'operator',
                    'value': '=',
                    'not_preceded_by': {
                        'type': 'operator',
                        'value': '!'
                    },
                    'not_followed_by': {
                        'type': 'operator',
                        'value': '='
                    }
                },
                'emit': {'type': 'operator', 'value': 'EQ_NOT_NOT_ASSIGN'}
            },
            {
                'match': {
                    'type': 'operator',
                    'value': '='
                },
                'emit': {'type': 'operator', 'value': 'GENERIC_EQ'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Test 1: Both conditions met
    input_tokens1 = [
        {'type': 'identifier', 'value': 'x'},
        {'type': 'operator', 'value': '='},
        {'type': 'identifier', 'value': 'y'}
    ]
    
    try:
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens1),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        assert result.stdout == 'xEQ_NOT_NOT_ASSIGNy'
        
    finally:
        os.unlink(mapping_file_path)


def test_lookahead_rules_take_priority_over_context_free_rules():
    """Scenario: Lookahead rules take priority over context-free rules for the same token
    
    Given a mapping with a followed_by rule and a general rule both matching the same token
    When the token appears followed by the token specified in followed_by
    Then the followed_by rule is applied rather than the general rule
    """
    
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'punctuator',
                    'value': '{',
                    'followed_by': {
                        'type': 'whitespace',
                        'value': '\n'
                    }
                },
                'emit': {'type': 'punctuator', 'value': 'BRACE_NEWLINE'}
            },
            {
                'match': {
                    'type': 'punctuator',
                    'value': '{'
                },
                'emit': {'type': 'punctuator', 'value': 'GENERAL_BRACE'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    input_tokens = [
        {'type': 'punctuator', 'value': '{'},
        {'type': 'whitespace', 'value': '\n'}
    ]
    
    try:
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        assert result.stdout == 'BRACE_NEWLINE\n'
        
    finally:
        os.unlink(mapping_file_path)
