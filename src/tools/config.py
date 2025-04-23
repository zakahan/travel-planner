import os
import yaml
from pathlib import Path

def read_yaml_to_dict(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = yaml.safe_load(file)
            return data
    except FileNotFoundError:
        print(f"Error:File {file_path} doesn't exist.")
        return {}
    except yaml.YAMLError as e:
        print(f"Error:parsing YAML file: {e}")
        return {}

MODULE_DIR = Path(__file__).parent.resolve()
YAML_PATH = MODULE_DIR / "tools_config.yaml"

tools_cfg = read_yaml_to_dict(YAML_PATH)

# print(os.path.abspath(CONFIG_PATH))
# # print(retrieval_cfg)