import sys
import os
import json
import subprocess
import tempfile
import yaml

# Shared test utilities
PYKEN = os.path.join(os.path.dirname(__file__), 'pyken.py')


def run_pyken(*args, input_data=None):
    """Run pyken.py with given args and input data, return subprocess result."""
    cmd = [sys.executable, PYKEN] + list(args)
    return subprocess.run(cmd, input=input_data, capture_output=True, text=True)


def make_mapping_file(content):
    """Create a temporary mapping file with the given YAML content."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(yaml.safe_load(content), f)
        return f.name


def load_mapping_from_yaml(yaml_content):
    """Parse YAML content and return the mapping dict."""
    return yaml.safe_load(yaml_content)
