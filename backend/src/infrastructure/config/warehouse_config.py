import os
from typing import Optional


class WarehouseConfig:
    """Configuration for warehouse functionality."""
    
    def __init__(self):
        self.enabled = self._get_bool_env('WAREHOUSE_ENABLED', True)
        # Use absolute path to avoid issues with relative paths
        # Go up from backend/src/infrastructure/config/ to project root, then to database
        default_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'database', 'warehouse', 'warehouse.sqlite'))
        self.db_path = os.getenv('WAREHOUSE_DB_PATH', default_path)
    
    def _get_bool_env(self, key: str, default: bool) -> bool:
        """Get boolean value from environment variable."""
        value = os.getenv(key, '').lower()
        if value in ('true', '1', 'yes', 'on'):
            return True
        elif value in ('false', '0', 'no', 'off'):
            return False
        return default
    
    def is_enabled(self) -> bool:
        """Check if warehouse is enabled."""
        return self.enabled
    
    def get_db_path(self) -> str:
        """Get the database file path."""
        return self.db_path
