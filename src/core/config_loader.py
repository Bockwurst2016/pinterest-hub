import yaml
from pathlib import Path
from typing import Dict

def load_config(config_path: str = "config/config.yaml") -> Dict:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Configuration file not found at {config_path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Global config instance
CONFIG = load_config()
