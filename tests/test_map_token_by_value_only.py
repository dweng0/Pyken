"""
Test cases for mapping a token by value only regardless of type
"""
import subprocess
import tempfile
import json
import os


def test_map_a_token_by_value_only_regardless_of_type():
    """Scenario: Map a token by value only regardless of type
    Given a mapping file with a rule matching only value ";"
    When any token with value ";" is processed regardless of its type
    Then the rule is applied to that token
    """
    # Create a temporary mapping file with a value-only rule
    mapping_content = {
        'rules': [
            {
                'match': {'value': ';'},  # Match by value only, not type
                'emit': {'value': 'SEMICOLON'}
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
        # Create a token stream with a semicolon token of different types
        # Using type 'punctuation' for the semicolon but the rule should match by value only
        token_stream = [
            {'type': 'keyword', 'value': 'def'},
            {'type': 'identifier', 'value': 'my_func'},
            {'type': 'punctuation', 'value': ';'},  # This should be replaced regardless of its type
            {'type': 'whitespace', 'value': '\n'}
        ]
        
        # Run pyken 
        result = subprocess.run(
            ['python', 'pyken.py', mapping_file_path],
            input=json.dumps(token_stream),
            text=True,
            capture_output=True
        )
        
        # Check that exit code is zero
        assert result.returncode == 0, f"Expected exit code 0, got {result.returncode}. Error: {result.stderr}"
        
        # Verify that the semicolon was replaced regardless of its original type
        expected_output = "defmy_funcSEMICOLON\n"  # The ';' should be changed to 'SEMICOLON'
        assert result.stdout == expected_output
        
        # Also run with --tokens to verify the token transformation
        result_tokens = subprocess.run(
            ['python', 'pyken.py', '--tokens', mapping_file_path],
            input=json.dumps(token_stream),
            text=True,
            capture_output=True
        )
        
        assert result_tokens.returncode == 0, f"Expected exit code 0, got {result_tokens.returncode}. Error: {result_tokens.stderr}"
        
        # Parse the output as JSON to check the tokens
        output_tokens = json.loads(result_tokens.stdout)
        
        # Find the token that originally had value ';'
        semicolon_tokens = [token for token in output_tokens if token['value'] == 'SEMICOLON']
        assert len(semicolon_tokens) == 1, f"Expected exactly one token with value 'SEMICOLON', found {len(semicolon_tokens)}"
        
    finally:
        os.unlink(mapping_file_path)