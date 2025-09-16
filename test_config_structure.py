import sys
sys.path.append('/Users/guidoespinoza/Desktop/Guido/Proyectos/crypto-trading-analyzer')

from src.config.config_manager import ConfigManager

config_manager = ConfigManager()
config = config_manager.get_consolidated_config()

print("=== CONFIG STRUCTURE ===")
for key in config.keys():
    print(f"Key: {key}")
    if isinstance(config[key], dict):
        print(f"  Type: dict with keys: {list(config[key].keys())}")
    else:
        print(f"  Type: {type(config[key])}, Value: {config[key]}")
    print()
