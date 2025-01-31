# single_file_dev01/tests/test_basic.py

import unittest
from pathlib import Path
from single_file.singlefile import CodebaseAnalyzer
from single_file.core import BaseArguments
import shutil
import os


class TestBasicFunctionality(unittest.TestCase):
    def setUp(self):
        # Setup with default arguments
        args = BaseArguments()
        args.paths = [Path('.')]
        args.output_file = 'test_output/default'
        args.formats = 'default,json,markdown'
        args.ignore_errors = True
        args.depth = 2
        args.absolute_paths = False
        args.extensions = ['py', 'js', 'css']
        args.exclude_extensions = ['txt']
        args.exclude_dirs = [r'^\.git$', r'^node_modules$']
        args.exclude_files = [r'.*\.log$']
        args.include_dirs = [r'^src$', r'^lib$']
        args.include_files = [r'.*\.py$', r'.*\.js$']
        args.show_guide = False
        args.replace_invalid_chars = True
        self.analyzer = CodebaseAnalyzer(args)

        # Ensure test_output directory exists and is clean
        os.makedirs('test_output', exist_ok=True)
        for f in Path('test_output').glob('*'):
            if f.is_file():
                f.unlink()

    def tearDown(self):
        # Clean up test_output directory after tests
        shutil.rmtree('test_output', ignore_errors=True)

    def test_plugin_loading(self):
        # Test that plugins are loaded correctly
        expected_plugins = {'default', 'json', 'markdown'}
        loaded_plugins = set(self.analyzer.plugins.keys())
        self.assertTrue(expected_plugins.issubset(loaded_plugins),
                        f"Loaded plugins {loaded_plugins} do not include expected {expected_plugins}")

    def test_file_analysis(self):
        # Test analyzing a known file
        test_file = Path('tests') / 'sample_test_file.py'
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("# Sample test file\nprint('Hello, World!')\n")

        try:
            file_info = self.analyzer.analyze_file(test_file)
            self.assertIsNotNone(file_info, "File info should not be None")
            self.assertEqual(file_info['path'], test_file.resolve())
            self.assertFalse(file_info['is_binary'], "Sample test file should not be binary")
            self.assertEqual(file_info['extension'], 'py')
            self.assertEqual(file_info['size'], test_file.stat().st_size)
        finally:
            test_file.unlink()
            test_file.parent.rmdir()

    def test_generate_outputs(self):
        # Test output generation
        self.analyzer.generate_outputs()
        # Check if output files are created
        for fmt in ['default', 'json', 'markdown']:
            output_file = Path('test_output') / f"codebase.{fmt}"
            self.assertTrue(output_file.exists(), f"Output file {output_file} does not exist")

    def test_plugin_disabling(self):
        # Disable the JSON plugin and verify it's not loaded
        args = BaseArguments()
        args.paths = [Path('.')]
        args.output_file = 'test_output/default'
        args.formats = 'default,json,markdown'
        args.ignore_errors = True
        args.depth = 2
        args.absolute_paths = False
        args.extensions = ['py', 'js', 'css']
        args.exclude_extensions = ['txt']
        args.exclude_dirs = [r'^\.git$', r'^node_modules$']
        args.exclude_files = [r'.*\.log$']
        args.include_dirs = [r'^src$', r'^lib$']
        args.include_files = [r'.*\.py$', r'.*\.js$']
        args.show_guide = False
        args.replace_invalid_chars = True
        self.analyzer = CodebaseAnalyzer(args)

        # Disable 'json' plugin
        if 'json' in self.analyzer.plugins:
            del self.analyzer.plugins['json']

        # Verify 'json' plugin is disabled
        self.assertNotIn('json', self.analyzer.plugins, "JSON plugin should be disabled")

        # Generate outputs and ensure JSON output is not created
        self.analyzer.generate_outputs()
        json_output = Path('test_output') / 'codebase.json'
        self.assertFalse(json_output.exists(), "JSON output file should not exist when plugin is disabled")


if __name__ == '__main__':
    unittest.main()
