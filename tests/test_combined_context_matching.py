import subprocess
import json
import tempfile
import os


def test_preceded_by_and_followed_by_can_be_combined_in_a_single_rule():
    """Scenario: preceded_by and followed_by can be combined in a single rule
    Given a mapping rule with both preceded_by and followed_by conditions
    When a token matches both the preceding and following token conditions
    Then that rule is applied
    And the rule is not applied when only one condition is satisfied
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {
                    'type': 'operator',
                    'value': '=',
                    'preceded_by': {
                        'type': 'identifier',
                        'value': 'x'
                    },
                    'followed_by': {
                        'type': 'identifier',
                        'value': 'y'
                    }
                },
                'emit': {'type': 'operator', 'value': 'ASSIGN_X_TO_Y'}
            },
            # Fallback rule for '='
            {
                'match': {
                    'type': 'operator',
                    'value': '='
                },
                'emit': {'type': 'operator', 'value': 'GENERIC_EQUALS'}
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    try:
        # Test 1: Both preceded_by and followed_by conditions are met - should match context-aware rule
        input_tokens_both_match = [
            {'type': 'identifier', 'value': 'x'},
            {'type': 'operator', 'value': '='},
            {'type': 'identifier', 'value': 'y'}
        ]
        
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens_both_match),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        # The '=' should be converted to 'ASSIGN_X_TO_Y' because it's preceded by 'x' and followed by 'y'
        assert result.stdout == 'xASSIGN_X_TO_Yy'
        
        # Test 2: Only preceded_by condition is met - should not match context-aware rule
        input_tokens_preceded_only = [
            {'type': 'identifier', 'value': 'x'},
            {'type': 'operator', 'value': '='},
            {'type': 'identifier', 'value': 'z'}  # Not 'y', so followed_by condition fails
        ]
        
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens_preceded_only),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        # The '=' should be converted to 'GENERIC_EQUALS' because followed_by condition fails
        assert result.stdout == 'xGENERIC_EQUALSz'
        
        # Test 3: Only followed_by condition is met - should not match context-aware rule
        input_tokens_followed_only = [
            {'type': 'identifier', 'value': 'w'},  # Not 'x', so preceded_by condition fails
            {'type': 'operator', 'value': '='},
            {'type': 'identifier', 'value': 'y'}
        ]
        
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens_followed_only),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        # The '=' should be converted to 'GENERIC_EQUALS' because preceded_by condition fails
        assert result.stdout == 'wGENERIC_EQUALSy'
        
        # Test 4: Neither condition is met - should not match context-aware rule
        input_tokens_neither = [
            {'type': 'identifier', 'value': 'w'},
            {'type': 'operator', 'value': '='},
            {'type': 'identifier', 'value': 'z'}
        ]
        
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens_neither),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        # The '=' should be converted to 'GENERIC_EQUALS' because neither condition is met
        assert result.stdout == 'wGENERIC_EQUALSz'
        
    finally:
        os.unlink(mapping_file_path)