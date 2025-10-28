"""
Configuration Manager
Handles loading and managing configuration from YAML files
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, ConfigDict


class TargetConfig(BaseModel):
    """Target website configuration"""
    url: str
    base_url: Optional[str] = None
    auth: Dict[str, Any] = Field(default_factory=dict)
    cookies: Dict[str, str] = Field(default_factory=dict)
    headers: Dict[str, str] = Field(default_factory=dict)


class CrawlerConfig(BaseModel):
    """Web crawler configuration"""
    enabled: bool = True
    max_depth: int = 5
    max_pages: int = 1000
    follow_external: bool = False
    respect_robots_txt: bool = True
    ignore_query_params: bool = False
    include_patterns: list = Field(default_factory=list)
    exclude_patterns: list = Field(default_factory=list)
    allowed_domains: list = Field(default_factory=list)
    crawl_delay: float = 0.5
    concurrent_requests: int = 10
    timeout: int = 30


class ModulesConfig(BaseModel):
    """Test modules configuration"""
    security: Dict[str, Any] = Field(default_factory=dict)
    performance: Dict[str, Any] = Field(default_factory=dict)
    functional: Dict[str, Any] = Field(default_factory=dict)
    api: Dict[str, Any] = Field(default_factory=dict)
    compatibility: Dict[str, Any] = Field(default_factory=dict)
    accessibility: Dict[str, Any] = Field(default_factory=dict)
    seo: Dict[str, Any] = Field(default_factory=dict)
    infrastructure: Dict[str, Any] = Field(default_factory=dict)
    visual: Dict[str, Any] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    business_logic: Dict[str, Any] = Field(default_factory=dict)


class ReportingConfig(BaseModel):
    """Reporting configuration"""
    output_dir: str = "reports/"
    formats: Dict[str, Any] = Field(default_factory=dict)
    severity_levels: Dict[str, bool] = Field(default_factory=dict)
    include_evidence: bool = True
    include_screenshots: bool = True
    include_recommendations: bool = True


class DatabaseConfig(BaseModel):
    """Database configuration"""
    type: str = "sqlite"
    path: str = "data/testool.db"
    host: str = "localhost"
    port: int = 5432
    username: str = ""
    password: str = ""
    database_name: str = "testool"


class DashboardConfig(BaseModel):
    """Dashboard configuration"""
    enabled: bool = True
    host: str = "127.0.0.1"
    port: int = 8080
    debug: bool = False
    real_time_updates: bool = True


class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"
    file: str = "logs/testool.log"
    console: bool = True
    max_size: str = "100MB"
    backup_count: int = 5


class AdvancedConfig(BaseModel):
    """Advanced configuration options"""
    parallel_execution: bool = True
    max_workers: int = 10
    retry_failed_tests: bool = True
    retry_count: int = 3
    random_user_agents: bool = True
    proxy: Dict[str, Any] = Field(default_factory=dict)
    rate_limiting: Dict[str, Any] = Field(default_factory=dict)
    screenshots_on_failure: bool = True
    video_recording: bool = False


class Config(BaseModel):
    """Main configuration model"""
    model_config = ConfigDict(extra='allow')

    target: TargetConfig
    crawler: CrawlerConfig = Field(default_factory=CrawlerConfig)
    modules: ModulesConfig = Field(default_factory=ModulesConfig)
    reporting: ReportingConfig = Field(default_factory=ReportingConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    dashboard: DashboardConfig = Field(default_factory=DashboardConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    advanced: AdvancedConfig = Field(default_factory=AdvancedConfig)
    notifications: Dict[str, Any] = Field(default_factory=dict)


class ConfigManager:
    """
    Configuration Manager
    Loads and manages configuration from YAML files
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager

        Args:
            config_path: Path to custom configuration file
        """
        self.config_path = config_path
        self.config: Optional[Config] = None
        self._load_config()

    def _load_config(self) -> None:
        """Load configuration from file"""
        # Load default configuration
        default_config_path = Path(__file__).parent.parent / "config" / "default_config.yaml"

        with open(default_config_path, 'r', encoding='utf-8') as f:
            default_config = yaml.safe_load(f)

        # Load custom configuration if provided
        if self.config_path:
            if not os.path.exists(self.config_path):
                raise FileNotFoundError(f"Configuration file not found: {self.config_path}")

            with open(self.config_path, 'r', encoding='utf-8') as f:
                custom_config = yaml.safe_load(f)

            # Merge configurations (custom overrides default)
            config_data = self._deep_merge(default_config, custom_config)
        else:
            config_data = default_config

        # Validate and create config object
        self.config = Config(**config_data)

    def _deep_merge(self, base: Dict, override: Dict) -> Dict:
        """
        Deep merge two dictionaries

        Args:
            base: Base dictionary
            override: Override dictionary

        Returns:
            Merged dictionary
        """
        result = base.copy()

        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation path

        Args:
            key_path: Dot-separated path (e.g., 'modules.security.enabled')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key_path.split('.')
        value = self.config.model_dump()

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set(self, key_path: str, value: Any) -> None:
        """
        Set configuration value by dot-notation path

        Args:
            key_path: Dot-separated path
            value: Value to set
        """
        keys = key_path.split('.')
        config_dict = self.config.model_dump()
        current = config_dict

        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            elif not isinstance(current[key], dict):
                # Convert non-dict values to dict if needed
                current[key] = {}
            current = current[key]

        current[keys[-1]] = value

        # Rebuild config object
        self.config = Config(**config_dict)

    def is_module_enabled(self, module_name: str) -> bool:
        """
        Check if a module is enabled

        Args:
            module_name: Name of the module

        Returns:
            True if enabled, False otherwise
        """
        return self.get(f'modules.{module_name}.enabled', False)

    def get_module_config(self, module_name: str) -> Dict[str, Any]:
        """
        Get configuration for a specific module

        Args:
            module_name: Name of the module

        Returns:
            Module configuration dictionary
        """
        return self.get(f'modules.{module_name}', {})

    def save(self, output_path: str) -> None:
        """
        Save current configuration to file

        Args:
            output_path: Output file path
        """
        config_dict = self.config.model_dump()

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_dict, f, default_flow_style=False, sort_keys=False)

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate configuration

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate target URL
        if not self.config.target.url:
            errors.append("Target URL is required")

        # Validate output directory
        if not self.config.reporting.output_dir:
            errors.append("Reporting output directory is required")

        # Validate at least one module is enabled
        modules_enabled = any([
            self.is_module_enabled(module)
            for module in ['security', 'performance', 'functional', 'api',
                           'compatibility', 'accessibility', 'seo', 'infrastructure']
        ])

        if not modules_enabled:
            errors.append("At least one test module must be enabled")

        return (len(errors) == 0, errors)

    def __repr__(self) -> str:
        """String representation"""
        return f"ConfigManager(target={self.config.target.url})"
