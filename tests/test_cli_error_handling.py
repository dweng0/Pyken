"""
Tests for Feature: CLI error handling
"""
import os
import subprocess
import sys
import tempfile

PYKEN = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'pyken.py')


def run_pyken(*args, input_data=None):
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def test_missing_mapping_file_argument_prints_usage_and_exits_non_zero():
    """Scenario: Missing mapping file argument prints usage and exits non-zero"""
    result = run_pyken()
    assert result.returncode != 0
    assert "usage" in result.stderr.lower() or "error" in result.stderr.lower()


def test_mapping_file_not_found_exits_with_a_clear_error():
    """Scenario: Mapping file not found exits with a clear error"""
    result = run_pyken('/nonexistent/path/mapping.yaml', input_data='[]')
    assert result.returncode != 0
    assert "mapping" in result.stderr.lower() or "not found" in result.stderr.lower() or "nonexistent" in result.stderr


def test_invalid_yaml_mapping_file_exits_with_a_clear_error():
    """Scenario: Invalid YAML mapping file exits with a clear error"""
    bad_yaml = "rules: [\nnot: valid: yaml: {{{"
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        f.write(bad_yaml)
        tmp_path = f.name
    try:
        result = run_pyken(tmp_path, input_data='[]')
        assert result.returncode != 0
        assert "yaml" in result.stderr.lower() or "YAML" in result.stderr
    finally:
        os.unlink(tmp_path)
