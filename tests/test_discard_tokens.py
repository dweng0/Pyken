"""
Test cases for discard token functionality
"""
import subprocess
import tempfile
import json
import os


def test_discarded_token_does_not_trigger_strict_mode_failure():
    """Scenario: Discarded token does not trigger strict mode failure
    Given a token stream containing a token that matches an emit: discard rule
    When I run pyken.py with --strict
    Then the exit code is zero
    And no error is printed for the discarded token
    """
    # Create a temporary mapping file with a discard rule and other rules for remaining tokens
    mapping_content = {
        'rules': [
            {
                'match': {'type': 'punctuation', 'value': ':'},
                'emit': 'discard'
            },
            {
                'match': {'type': 'keyword'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'identifier'},
                'emit': 'pass'
            },
            {
                'match': {'type': 'whitespace'},
                'emit': 'pass'
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    try:
        # Create a token stream with a token that will be discarded
        token_stream = [
            {'type': 'keyword', 'value': 'def'},
            {'type': 'identifier', 'value': 'my_func'},
            {'type': 'punctuation', 'value': ':'},  # This should be discarded
            {'type': 'whitespace', 'value': '\n'}
        ]
        
        # Run pyken with strict mode
        result = subprocess.run(
            ['python', 'pyken.py', '--strict', mapping_file_path],
            input=json.dumps(token_stream),
            text=True,
            capture_output=True
        )
        
        # Check that exit code is zero
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Error: {result.stderr}"
        
        # Check that no error is printed for the discarded token
        assert "No mapping rule for token:" not in result.stderr
        
        # Verify that the discarded token is not in the output
        expected_output = "defmy_func\n"  # The ':' should be removed
        assert result.stdout == expected_output
        
    finally:
        os.unlink(mapping_file_path)