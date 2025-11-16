"""
Test suite for Configuration as Code feature.
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path
from accudoc.config import (
    ConfigManager, AccuDocConfig, ScanConfig,
    GenerateConfig, OutputConfig, FeaturesConfig
)


class TestConfigManager(unittest.TestCase):
    """Test configuration management functionality."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.test_path = Path(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_default_config(self):
        """Test creating default configuration."""
        config = AccuDocConfig()
        
        self.assertEqual(config.version, '1.0')
        self.assertIsNone(config.repository)
        self.assertIsInstance(config.scan, ScanConfig)
        self.assertIsInstance(config.generate, GenerateConfig)
        self.assertIsInstance(config.output, OutputConfig)
        self.assertIsInstance(config.features, FeaturesConfig)
    
    def test_scan_config_defaults(self):
        """Test scan configuration defaults."""
        scan = ScanConfig()
        
        self.assertIn('.git', scan.exclude_patterns)
        self.assertIn('__pycache__', scan.exclude_patterns)
        self.assertFalse(scan.include_hidden)
        self.assertTrue(scan.use_cache)
        self.assertIn('.py', scan.extensions)
    
    def test_generate_config_defaults(self):
        """Test generate configuration defaults."""
        gen = GenerateConfig()
        
        self.assertEqual(gen.template, 'default')
        self.assertEqual(gen.format, 'markdown')
        self.assertEqual(gen.theme, 'default')
        self.assertTrue(gen.include_toc)
        self.assertTrue(gen.include_badges)
        self.assertTrue(gen.include_stats)
    
    def test_save_and_load_json(self):
        """Test saving and loading JSON config."""
        manager = ConfigManager()
        
        # Create config
        config = AccuDocConfig(
            version='1.0',
            repository='/path/to/repo',
            scan=ScanConfig(exclude_patterns=['.git', 'node_modules']),
            generate=GenerateConfig(template='minimal', format='html')
        )
        
        # Save
        json_path = self.test_path / 'config.json'
        saved_path = manager.save_config(config, str(json_path), format='json')
        
        self.assertTrue(saved_path.exists())
        
        # Load
        loaded_config = manager.load_config(str(saved_path))
        
        self.assertEqual(loaded_config.version, config.version)
        self.assertEqual(loaded_config.repository, config.repository)
        self.assertEqual(loaded_config.generate.template, 'minimal')
        self.assertEqual(loaded_config.generate.format, 'html')
    
    def test_save_and_load_yaml(self):
        """Test saving and loading YAML config."""
        manager = ConfigManager()
        
        # Create config
        config = AccuDocConfig(
            version='1.0',
            repository='/path/to/repo',
            generate=GenerateConfig(title='Test Project')
        )
        
        # Save
        yaml_path = self.test_path / 'config.yml'
        saved_path = manager.save_config(config, str(yaml_path), format='yaml')
        
        self.assertTrue(saved_path.exists())
        
        # Load
        loaded_config = manager.load_config(str(saved_path))
        
        self.assertEqual(loaded_config.version, config.version)
        self.assertEqual(loaded_config.repository, config.repository)
        self.assertEqual(loaded_config.generate.title, 'Test Project')
    
    def test_load_nonexistent_config(self):
        """Test loading when config file doesn't exist."""
        manager = ConfigManager()
        
        # Should return default config without error
        config = manager.load_config('/nonexistent/config.yml')
        
        self.assertIsInstance(config, AccuDocConfig)
        self.assertEqual(config.version, '1.0')
    
    def test_features_config(self):
        """Test features configuration."""
        features = FeaturesConfig(
            enable_dataflow=True,
            enable_spellcheck=True,
            enable_complexity=True
        )
        
        self.assertTrue(features.enable_dataflow)
        self.assertTrue(features.enable_spellcheck)
        self.assertTrue(features.enable_complexity)
        self.assertFalse(features.enable_coverage)
    
    def test_output_config(self):
        """Test output configuration."""
        output = OutputConfig(
            output_file='docs/README.md',
            output_dir='docs',
            create_index=True,
            separate_files=False
        )
        
        self.assertEqual(output.output_file, 'docs/README.md')
        self.assertEqual(output.output_dir, 'docs')
        self.assertTrue(output.create_index)
        self.assertFalse(output.separate_files)
    
    def test_metadata_in_config(self):
        """Test metadata field in config."""
        config = AccuDocConfig(
            metadata={
                'author': 'Test Author',
                'license': 'MIT',
                'version': '2.0'
            }
        )
        
        self.assertEqual(config.metadata['author'], 'Test Author')
        self.assertEqual(config.metadata['license'], 'MIT')
        self.assertEqual(config.metadata['version'], '2.0')
    
    def test_config_to_dict_conversion(self):
        """Test converting config to dictionary."""
        manager = ConfigManager()
        
        config = AccuDocConfig(
            version='1.0',
            repository='.',
            generate=GenerateConfig(template='api')
        )
        
        data = manager._config_to_dict(config)
        
        self.assertEqual(data['version'], '1.0')
        self.assertEqual(data['repository'], '.')
        self.assertEqual(data['generate']['template'], 'api')
        self.assertIn('scan', data)
        self.assertIn('output', data)
        self.assertIn('features', data)
    
    def test_dict_to_config_conversion(self):
        """Test converting dictionary to config."""
        manager = ConfigManager()
        
        data = {
            'version': '1.0',
            'repository': '/test/repo',
            'scan': {
                'exclude_patterns': ['.git'],
                'use_cache': False
            },
            'generate': {
                'template': 'detailed',
                'theme': 'dark'
            }
        }
        
        config = manager._dict_to_config(data)
        
        self.assertEqual(config.version, '1.0')
        self.assertEqual(config.repository, '/test/repo')
        self.assertFalse(config.scan.use_cache)
        self.assertEqual(config.generate.template, 'detailed')
        self.assertEqual(config.generate.theme, 'dark')
    
    def test_generate_example_config_yaml(self):
        """Test generating example YAML config."""
        manager = ConfigManager()
        
        yaml_content = manager.generate_example_config(format='yaml')
        
        self.assertIn('version:', yaml_content)
        self.assertIn('repository:', yaml_content)
        self.assertIn('scan:', yaml_content)
        self.assertIn('generate:', yaml_content)
        self.assertIn('# AccuDoc Configuration File', yaml_content)
    
    def test_generate_example_config_json(self):
        """Test generating example JSON config."""
        manager = ConfigManager()
        
        json_content = manager.generate_example_config(format='json')
        
        # Should be valid JSON
        data = json.loads(json_content)
        
        self.assertEqual(data['version'], '1.0')
        self.assertIn('scan', data)
        self.assertIn('generate', data)
        self.assertIn('output', data)
        self.assertIn('features', data)
    
    def test_find_config_file(self):
        """Test finding config file in directory."""
        # Create a config file
        config_file = self.test_path / 'accudoc.yml'
        config_file.write_text('version: "1.0"\n')
        
        # Change to test directory
        import os
        old_cwd = os.getcwd()
        try:
            os.chdir(self.test_path)
            
            manager = ConfigManager()
            found = manager._find_config_file()
            
            self.assertIsNotNone(found)
            self.assertEqual(found.name, 'accudoc.yml')
        finally:
            os.chdir(old_cwd)
    
    def test_complex_config(self):
        """Test complex configuration with all fields."""
        config = AccuDocConfig(
            version='2.0',
            repository='/complex/repo',
            scan=ScanConfig(
                exclude_patterns=['.git', 'node_modules', 'venv'],
                include_hidden=True,
                use_cache=False,
                extensions=['.py', '.js', '.ts']
            ),
            generate=GenerateConfig(
                template='detailed',
                format='html',
                theme='dark',
                title='Complex Project',
                include_toc=True,
                include_badges=False,
                include_stats=True
            ),
            output=OutputConfig(
                output_file='output.html',
                output_dir='generated',
                create_index=True,
                separate_files=True
            ),
            features=FeaturesConfig(
                enable_dataflow=True,
                enable_call_graph=True,
                enable_complexity=True,
                enable_coverage=True,
                enable_spellcheck=True,
                enable_readability=True,
                enable_breaking_changes=True
            ),
            metadata={
                'author': 'Complex Author',
                'license': 'Apache-2.0',
                'custom_field': 'custom_value'
            }
        )
        
        manager = ConfigManager()
        
        # Save and load
        config_path = self.test_path / 'complex.json'
        manager.save_config(config, str(config_path), format='json')
        loaded = manager.load_config(str(config_path))
        
        # Verify all fields
        self.assertEqual(loaded.version, '2.0')
        self.assertEqual(loaded.repository, '/complex/repo')
        self.assertTrue(loaded.scan.include_hidden)
        self.assertFalse(loaded.scan.use_cache)
        self.assertEqual(loaded.generate.template, 'detailed')
        self.assertEqual(loaded.generate.theme, 'dark')
        self.assertTrue(loaded.output.separate_files)
        self.assertTrue(loaded.features.enable_dataflow)
        self.assertTrue(loaded.features.enable_coverage)
        self.assertEqual(loaded.metadata['author'], 'Complex Author')


def run_tests():
    """Run all tests."""
    print("=" * 60)
    print("Configuration as Code Test Suite")
    print("=" * 60)
    print()
    
    # Create test suite
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print()
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print()
    
    if result.wasSuccessful():
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed")
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
