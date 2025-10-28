"""
Module Loader - Dynamically loads and manages test modules
"""

import importlib
import inspect
import pkgutil
from pathlib import Path
from typing import Dict, List, Type
from loguru import logger

from .config import ConfigManager
from .models import Category


class BaseTestModule:
    """
    Base class for all test modules
    All test modules must inherit from this class
    """

    # Module metadata
    name: str = "base"
    description: str = "Base test module"
    category: Category = Category.SECURITY
    version: str = "1.0.0"

    def __init__(self, config: ConfigManager):
        """
        Initialize test module

        Args:
            config: Configuration manager
        """
        self.config = config
        self.enabled = self._is_enabled()

    def _is_enabled(self) -> bool:
        """Check if module is enabled in configuration"""
        return self.config.is_module_enabled(self.name)

    async def run(self, context):
        """
        Run the test module
        Must be implemented by subclasses

        Args:
            context: Test context with crawled data

        Returns:
            ModuleResult object
        """
        raise NotImplementedError("Subclasses must implement run() method")

    async def setup(self) -> None:
        """
        Setup method called before running tests
        Override in subclasses if needed
        """
        pass

    async def teardown(self) -> None:
        """
        Teardown method called after running tests
        Override in subclasses if needed
        """
        pass


class ModuleLoader:
    """
    Module Loader
    Discovers and loads test modules dynamically
    """

    def __init__(self, config: ConfigManager):
        """
        Initialize ModuleLoader

        Args:
            config: Configuration manager
        """
        self.config = config
        self.modules: Dict[str, Type[BaseTestModule]] = {}
        self.module_instances: Dict[str, BaseTestModule] = {}

    def discover_modules(self, modules_path: str = None) -> None:
        """
        Discover all test modules

        Args:
            modules_path: Path to modules directory
        """
        if modules_path is None:
            # Default to modules directory in project root
            modules_path = str(Path(__file__).parent.parent / "modules")

        logger.info(f"Discovering test modules in {modules_path}")

        # Add modules path to Python path
        import sys
        if modules_path not in sys.path:
            sys.path.insert(0, modules_path)

        # Discover all Python packages in modules directory
        modules_dir = Path(modules_path)
        if not modules_dir.exists():
            logger.warning(f"Modules directory not found: {modules_path}")
            return

        # Iterate through all subdirectories
        for subdir in modules_dir.iterdir():
            if subdir.is_dir() and not subdir.name.startswith('_'):
                # Try to import the module
                try:
                    module_name = subdir.name
                    self._load_module_package(module_name, str(subdir))
                except Exception as e:
                    logger.error(f"Error loading module {subdir.name}: {str(e)}")

        logger.info(f"Discovered {len(self.modules)} test modules")

    def _load_module_package(self, package_name: str, package_path: str) -> None:
        """
        Load a module package

        Args:
            package_name: Name of the package
            package_path: Path to the package
        """
        # Import the package
        try:
            package = importlib.import_module(package_name)

            # Look for BaseTestModule subclasses in the package
            for name, obj in inspect.getmembers(package):
                if (inspect.isclass(obj) and
                        issubclass(obj, BaseTestModule) and
                        obj != BaseTestModule):

                    module_name = getattr(obj, 'name', name.lower())
                    self.modules[module_name] = obj
                    logger.debug(f"Loaded module: {module_name} ({obj.__name__})")

            # Also check submodules
            for importer, modname, ispkg in pkgutil.iter_modules([package_path]):
                if not modname.startswith('_'):
                    full_module_name = f"{package_name}.{modname}"
                    try:
                        submodule = importlib.import_module(full_module_name)

                        for name, obj in inspect.getmembers(submodule):
                            if (inspect.isclass(obj) and
                                    issubclass(obj, BaseTestModule) and
                                    obj != BaseTestModule):

                                module_name = getattr(obj, 'name', name.lower())
                                self.modules[module_name] = obj
                                logger.debug(f"Loaded module: {module_name} ({obj.__name__})")

                    except Exception as e:
                        logger.error(f"Error loading submodule {full_module_name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error importing package {package_name}: {str(e)}")

    def get_module(self, module_name: str) -> BaseTestModule:
        """
        Get a module instance by name

        Args:
            module_name: Name of the module

        Returns:
            Module instance
        """
        if module_name not in self.module_instances:
            if module_name not in self.modules:
                raise ValueError(f"Module not found: {module_name}")

            # Create instance
            module_class = self.modules[module_name]
            self.module_instances[module_name] = module_class(self.config)

        return self.module_instances[module_name]

    def get_enabled_modules(self) -> List[BaseTestModule]:
        """
        Get all enabled module instances

        Returns:
            List of enabled module instances
        """
        enabled = []
        for module_name, module_class in self.modules.items():
            instance = self.get_module(module_name)
            if instance.enabled:
                enabled.append(instance)

        return enabled

    def get_modules_by_category(self, category: Category) -> List[BaseTestModule]:
        """
        Get all modules in a specific category

        Args:
            category: Test category

        Returns:
            List of module instances in the category
        """
        modules = []
        for module_name, module_class in self.modules.items():
            instance = self.get_module(module_name)
            if instance.category == category and instance.enabled:
                modules.append(instance)

        return modules

    def list_modules(self) -> Dict[str, Dict]:
        """
        List all discovered modules with their metadata

        Returns:
            Dictionary of module metadata
        """
        modules_info = {}
        for module_name, module_class in self.modules.items():
            modules_info[module_name] = {
                'name': getattr(module_class, 'name', module_name),
                'description': getattr(module_class, 'description', ''),
                'category': getattr(module_class, 'category', Category.SECURITY).value,
                'version': getattr(module_class, 'version', '1.0.0'),
                'enabled': self.config.is_module_enabled(module_name)
            }

        return modules_info
