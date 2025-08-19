import yaml
import os

def get_config(path = "config.yaml", env = "development"):
    # Get the project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(project_root, path)
    
    with open(config_path, "r") as f:
        full_yaml_config = yaml.safe_load(f)
    config = full_yaml_config[env]
    return config