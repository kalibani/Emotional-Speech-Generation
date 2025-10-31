"""Logging configuration and utilities."""

import logging
import logging.config
from pathlib import Path
import yaml


def setup_logging(config_path: str = "config/logging.yaml", default_level: int = logging.INFO) -> None:
    """Setup logging configuration.
    
    Args:
        config_path: Path to logging configuration file
        default_level: Default logging level if config not found
    """
    path = Path(config_path)
    
    if path.exists():
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f)
            
            # Ensure log directories exist
            for handler in config.get('handlers', {}).values():
                if 'filename' in handler:
                    log_file = Path(handler['filename'])
                    log_file.parent.mkdir(parents=True, exist_ok=True)
            
            logging.config.dictConfig(config)
        except Exception as e:
            logging.basicConfig(level=default_level)
            logging.error(f"Failed to load logging config: {e}")
    else:
        logging.basicConfig(level=default_level)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)

