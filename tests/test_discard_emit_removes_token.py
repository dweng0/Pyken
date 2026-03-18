"""
Test cases for discard emit functionality - removing tokens from output
"""
import subprocess
import tempfile
import json
import os


def test_discard_emit_removes_the_token_from_output():
    """Scenario: Discard emit removes the token from output
    Given a token stream containing a token with type "punctuation" and value ":"
    And a mapping rule that matches that token with emit: discard
    When I run pyken.py
    Then the output does not contain ":"
    And no warning is printed for the discarded token
    """
    # Create a temporary mapping file with a discard rule
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
        
        # Run pyken without strict mode
        result = subprocess.run(
            ['python', 'pyken.py', mapping_file_path],
            input=json.dumps(token_stream),
            text=True,
            capture_output=True
        )
        
        # Check that exit code is zero
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Error: {result.stderr}"
        
        # Check that no warning is printed for the discarded token
        assert "No mapping rule for token:" not in result.stderr
        
        # Verify that the discarded token is not in the output
        expected_output = "defmy_func\n"  # The ':' should be removed
        assert result.stdout == expected_output
        
        # Verify that ':' does not appear in the output
        assert ':' not in result.stdout
        
    finally:
        os.unlink(mapping_file_path)