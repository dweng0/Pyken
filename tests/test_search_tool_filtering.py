"""
Tests for Feature: Search tool filtering

These tests verify that the search_files tool in scripts/agent.py
excludes non-source directories like .git, node_modules, and __pycache__.
"""
import os
import sys
import tempfile

# Add scripts directory to path to import agent module
SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'scripts')
sys.path.insert(0, SCRIPTS_DIR)


def test_search_files_excludes_git_directory_from_results():
    """Scenario: search_files excludes .git directory from results"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create .git directory with a matching file
        git_dir = os.path.join(tmpdir, '.git')
        os.makedirs(git_dir)
        matching_file = os.path.join(git_dir, 'config')
        with open(matching_file, 'w') as f:
            f.write('search_pattern_test_value')
        
        # Create a regular file that also matches
        regular_file = os.path.join(tmpdir, 'source.py')
        with open(regular_file, 'w') as f:
            f.write('search_pattern_test_value')
        
        # Import and run the search_files tool from agent.py
        import agent
        input_data = {"pattern": "search_pattern_test_value", "path": tmpdir}
        result = agent.run_tool("search_files", input_data)
        
        # The result should not contain .git paths
        assert '.git' not in result, f"Expected .git to be excluded from search results but found: {result}"


def test_search_files_excludes_node_modules_and_pycache_from_results():
    """Scenario: search_files excludes node_modules and __pycache__ from results"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create node_modules directory with a matching file
        node_modules_dir = os.path.join(tmpdir, 'node_modules')
        os.makedirs(node_modules_dir)
        node_file = os.path.join(node_modules_dir, 'index.js')
        with open(node_file, 'w') as f:
            f.write('search_pattern_test_value')
        
        # Create __pycache__ directory with a matching file
        pycache_dir = os.path.join(tmpdir, '__pycache__')
        os.makedirs(pycache_dir)
        pycache_file = os.path.join(pycache_dir, 'module.pyc')
        with open(pycache_file, 'w') as f:
            f.write('search_pattern_test_value')
        
        # Create a regular file that also matches
        regular_file = os.path.join(tmpdir, 'source.py')
        with open(regular_file, 'w') as f:
            f.write('search_pattern_test_value')
        
        # Import and run the search_files tool from agent.py
        import agent
        input_data = {"pattern": "search_pattern_test_value", "path": tmpdir}
        result = agent.run_tool("search_files", input_data)
        
        # The result should not contain node_modules or __pycache__ paths
        assert 'node_modules' not in result, f"Expected node_modules to be excluded from search results but found: {result}"
        assert '__pycache__' not in result, f"Expected __pycache__ to be excluded from search results but found: {result}"
