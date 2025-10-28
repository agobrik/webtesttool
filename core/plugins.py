"""
Plugin system for extending WebTestool functionality
"""

import importlib
import inspect
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from pathlib import Path
from loguru import logger


class Plugin(ABC):
    """
    Base class for all plugins

    Example:
        class MyPlugin(Plugin):
            name = "my_plugin"
            version = "1.0.0"

            def initialize(self, config):
                # Setup plugin
                pass

            def execute(self, context):
                # Plugin logic
                return {"result": "success"}
    """

    name: str = "unknown"
    version: str = "0.0.1"
    description: str = ""
    author: str = ""

    @abstractmethod
    def initialize(self, config: Dict[str, Any]) -> bool:
        """
        Initialize plugin with configuration

        Args:
            config: Plugin configuration dictionary

        Returns:
            True if initialization successful
        """
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Any:
        """
        Execute plugin logic

        Args:
            context: Execution context with data

        Returns:
            Plugin execution result
        """
        pass

    def cleanup(self):
        """Cleanup plugin resources"""
        pass

    def get_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author
        }


class PreScanPlugin(Plugin):
    """Plugin that runs before scanning"""

    @abstractmethod
    def pre_scan(self, target_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute before scan starts

        Args:
            target_url: Target URL to scan
            config: Scan configuration

        Returns:
            Modified configuration or additional data
        """
        pass

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute plugin"""
        return self.pre_scan(
            context.get('target_url', ''),
            context.get('config', {})
        )


class PostScanPlugin(Plugin):
    """Plugin that runs after scanning"""

    @abstractmethod
    def post_scan(self, scan_result: Any) -> Any:
        """
        Execute after scan completes

        Args:
            scan_result: Scan result object

        Returns:
            Modified or additional results
        """
        pass

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute plugin"""
        return self.post_scan(context.get('scan_result'))


class ReportPlugin(Plugin):
    """Plugin for custom report generation"""

    @abstractmethod
    def generate_report(self, scan_result: Any, output_dir: str) -> str:
        """
        Generate custom report

        Args:
            scan_result: Scan result object
            output_dir: Output directory path

        Returns:
            Path to generated report
        """
        pass

    def execute(self, context: Dict[str, Any]) -> Any:
        """Execute plugin"""
        return self.generate_report(
            context.get('scan_result'),
            context.get('output_dir', 'reports')
        )


class TestModulePlugin(Plugin):
    """Plugin for custom test modules"""

    @abstractmethod
    async def run_tests(self, target_url: str, config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run custom tests

        Args:
            target_url: Target URL
            config: Test configuration

        Returns:
            List of test results
        """
        pass

    async def execute(self, context: Dict[str, Any]) -> Any:
        """Execute plugin"""
        return await self.run_tests(
            context.get('target_url', ''),
            context.get('config', {})
        )


class PluginManager:
    """
    Manage plugin lifecycle

    Example:
        manager = PluginManager()
        manager.register_plugin(MyPlugin())
        manager.initialize_all(config)

        results = manager.execute_plugins('pre_scan', context={
            'target_url': 'https://example.com',
            'config': {}
        })
    """

    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_types: Dict[str, List[str]] = {
            'pre_scan': [],
            'post_scan': [],
            'report': [],
            'test_module': []
        }

    def register_plugin(self, plugin: Plugin) -> bool:
        """
        Register a plugin

        Args:
            plugin: Plugin instance

        Returns:
            True if registration successful
        """
        if not isinstance(plugin, Plugin):
            logger.error(f"Invalid plugin: {plugin}")
            return False

        plugin_name = plugin.name

        if plugin_name in self.plugins:
            logger.warning(f"Plugin '{plugin_name}' already registered")
            return False

        self.plugins[plugin_name] = plugin

        # Categorize plugin
        if isinstance(plugin, PreScanPlugin):
            self.plugin_types['pre_scan'].append(plugin_name)
        if isinstance(plugin, PostScanPlugin):
            self.plugin_types['post_scan'].append(plugin_name)
        if isinstance(plugin, ReportPlugin):
            self.plugin_types['report'].append(plugin_name)
        if isinstance(plugin, TestModulePlugin):
            self.plugin_types['test_module'].append(plugin_name)

        logger.info(f"Plugin '{plugin_name}' v{plugin.version} registered")
        return True

    def unregister_plugin(self, plugin_name: str) -> bool:
        """Unregister a plugin"""
        if plugin_name not in self.plugins:
            return False

        plugin = self.plugins.pop(plugin_name)
        plugin.cleanup()

        # Remove from types
        for plugin_list in self.plugin_types.values():
            if plugin_name in plugin_list:
                plugin_list.remove(plugin_name)

        logger.info(f"Plugin '{plugin_name}' unregistered")
        return True

    def get_plugin(self, plugin_name: str) -> Optional[Plugin]:
        """Get plugin by name"""
        return self.plugins.get(plugin_name)

    def get_plugins_by_type(self, plugin_type: str) -> List[Plugin]:
        """Get all plugins of specific type"""
        plugin_names = self.plugin_types.get(plugin_type, [])
        return [self.plugins[name] for name in plugin_names if name in self.plugins]

    def initialize_all(self, config: Dict[str, Any]) -> Dict[str, bool]:
        """Initialize all plugins"""
        results = {}
        for name, plugin in self.plugins.items():
            try:
                plugin_config = config.get('plugins', {}).get(name, {})
                success = plugin.initialize(plugin_config)
                results[name] = success
                if success:
                    logger.info(f"Plugin '{name}' initialized")
                else:
                    logger.error(f"Plugin '{name}' initialization failed")
            except Exception as e:
                logger.error(f"Error initializing plugin '{name}': {e}")
                results[name] = False

        return results

    def execute_plugins(self, plugin_type: str, context: Dict[str, Any]) -> List[Any]:
        """Execute all plugins of specific type"""
        plugins = self.get_plugins_by_type(plugin_type)
        results = []

        for plugin in plugins:
            try:
                result = plugin.execute(context)
                results.append({
                    'plugin': plugin.name,
                    'success': True,
                    'result': result
                })
            except Exception as e:
                logger.error(f"Error executing plugin '{plugin.name}': {e}")
                results.append({
                    'plugin': plugin.name,
                    'success': False,
                    'error': str(e)
                })

        return results

    def load_plugins_from_directory(self, directory: str) -> int:
        """
        Load plugins from directory

        Args:
            directory: Path to plugins directory

        Returns:
            Number of plugins loaded
        """
        plugin_dir = Path(directory)
        if not plugin_dir.exists():
            logger.warning(f"Plugin directory not found: {directory}")
            return 0

        loaded_count = 0

        for file in plugin_dir.glob("*.py"):
            if file.name.startswith("_"):
                continue

            try:
                # Import module
                module_name = file.stem
                spec = importlib.util.spec_from_file_location(module_name, file)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)

                # Find Plugin classes
                for name, obj in inspect.getmembers(module, inspect.isclass):
                    if issubclass(obj, Plugin) and obj != Plugin:
                        plugin_instance = obj()
                        if self.register_plugin(plugin_instance):
                            loaded_count += 1

            except Exception as e:
                logger.error(f"Failed to load plugin from {file}: {e}")

        logger.info(f"Loaded {loaded_count} plugins from {directory}")
        return loaded_count

    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]

    def cleanup_all(self):
        """Cleanup all plugins"""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                logger.error(f"Error cleaning up plugin '{plugin.name}': {e}")


# Global plugin manager
_plugin_manager = None


def get_plugin_manager() -> PluginManager:
    """Get global plugin manager"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


# Example plugin implementations
class ExamplePreScanPlugin(PreScanPlugin):
    """Example pre-scan plugin"""

    name = "example_pre_scan"
    version = "1.0.0"
    description = "Example plugin that runs before scan"

    def initialize(self, config: Dict[str, Any]) -> bool:
        logger.info(f"Initializing {self.name}")
        return True

    def pre_scan(self, target_url: str, config: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Pre-scan check for {target_url}")
        return {'pre_scan_complete': True}


class ExamplePostScanPlugin(PostScanPlugin):
    """Example post-scan plugin"""

    name = "example_post_scan"
    version = "1.0.0"
    description = "Example plugin that runs after scan"

    def initialize(self, config: Dict[str, Any]) -> bool:
        logger.info(f"Initializing {self.name}")
        return True

    def post_scan(self, scan_result: Any) -> Any:
        logger.info("Post-scan processing")
        return {'post_scan_complete': True}
