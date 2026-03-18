import subprocess
import json
import tempfile
import os


def test_single_matched_token_emits_multiple_tokens_in_token_stream_output():
    """Scenario: A single matched token emits multiple tokens in token stream output
    Given a token stream containing a token with type "indent"
    And a mapping rule that matches that token with emit: ["{", "}"]
    When I run pyken.py with --tokens
    Then the output JSON array contains two tokens where the original single token was
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {'type': 'indent'},
                'emit': [{'type': 'punctuation', 'value': '{'}, {'type': 'punctuation', 'value': '}'}]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream
    input_tokens = [{'type': 'indent', 'value': '    '}]
    
    try:
        # Run pyken with --tokens flag
        result = subprocess.run(
            ['python3', 'pyken.py', '--tokens', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # Parse the output JSON
        output_tokens = json.loads(result.stdout)
        
        # Check that we have exactly 2 tokens in output (where originally there was 1)
        assert len(output_tokens) == 2
        
        # Check that the tokens are as expected
        assert output_tokens[0]['type'] == 'punctuation'
        assert output_tokens[0]['value'] == '{'
        assert output_tokens[1]['type'] == 'punctuation'
        assert output_tokens[1]['value'] == '}'
        
    finally:
        os.unlink(mapping_file_path)


def test_multi_token_emission_appears_correctly_in_reconstructed_source_text():
    """Scenario: Multi-token emission appears correctly in reconstructed source text
    Given a single matched token that emits multiple tokens via a mapping rule
    When I run pyken.py without --tokens
    Then the reconstructed source text contains the values of all emitted tokens in order
    """
    
    # Create a temporary mapping file
    mapping_content = {
        'rules': [
            {
                'match': {'type': 'indent'},
                'emit': [{'type': 'punctuation', 'value': '{'}, {'type': 'punctuation', 'value': '}'}]
            }
        ]
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as mapping_file:
        json.dump(mapping_content, mapping_file)
        mapping_file_path = mapping_file.name
    
    # Create input token stream
    input_tokens = [{'type': 'indent', 'value': '    '}, {'type': 'keyword', 'value': 'pass'}]
    
    try:
        # Run pyken without --tokens flag (default text output)
        result = subprocess.run(
            ['python3', 'pyken.py', mapping_file_path],
            input=json.dumps(input_tokens),
            text=True,
            capture_output=True
        )
        
        assert result.returncode == 0, f"Process failed with stderr: {result.stderr}"
        
        # Check that the output contains both emitted token values in order
        assert result.stdout == '{}pass'  # indent -> '{' + '}' and 'pass' remains
        
    finally:
        os.unlink(mapping_file_path)