"""
Test cases for discarded token not appearing in token stream output
"""
import subprocess
import tempfile
import json
import os


def test_discarded_token_does_not_appear_in_token_stream_output():
    """Scenario: Discarded token does not appear in token stream output
    Given a token stream containing a token with emit: discard in the mapping
    When I run pyken.py with --tokens
    Then the discarded token does not appear in the output JSON array
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
        
        # Run pyken with --tokens flag
        result = subprocess.run(
            ['python', 'pyken.py', '--tokens', mapping_file_path],
            input=json.dumps(token_stream),
            text=True,
            capture_output=True
        )
        
        # Check that exit code is zero
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Error: {result.stderr}"
        
        # Parse the output as JSON to check the tokens
        output_tokens = json.loads(result.stdout)
        
        # Verify that the discarded token is not in the output
        discarded_values = [token['value'] for token in output_tokens if token['value'] == ':']
        assert len(discarded_values) == 0, f"Found discarded token ':' in output: {output_tokens}"
        
        # Verify that the other tokens are present
        output_values = [token['value'] for token in output_tokens]
        assert 'def' in output_values
        assert 'my_func' in output_values
        assert '\n' in output_values
        
    finally:
        os.unlink(mapping_file_path)