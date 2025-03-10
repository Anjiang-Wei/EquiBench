# huggingface-cli login
# huggingface-cli whoami
import argparse
import logging

from pathlib import Path
from steps.data import EquiBenchDatasets

from utils import prepare_environment, parse_log_level

def main():
    eval_step = DataStep(**vars(parse_args()))
    eval_step()

def parse_args():
    parser = argparse.ArgumentParser(description="Prepare Datasets.")
    parser.add_argument("data_path"      , type=Path           ,                                                                           help="The file path of datasets. (output)")
    parser.add_argument("--log_level"    , type=parse_log_level, required=False, default="INFO"                                          , help="Set logging level.", choices=["DEBUG", "INFO", "WARNING", "ERROR"])

    return parser.parse_args()

class DataStep:
    def __init__(self, data_path: Path, log_level: str):
        prepare_environment(log_level=log_level)   
        self.define_paths(data_path=data_path)     

        logging.info(f"DataStep(data_path={data_path})")
    
    def define_paths(self, data_path: Path):
        # input paths
        
        # output paths
        self.data_path = data_path
    
    def __call__(self):
        self.data_path.mkdir(parents=True, exist_ok=True)

        datasets = EquiBenchDatasets()

        # Check Hugging Face CLI login status
        datasets.check_huggingface_login()
        
        # Load dataset configuration names
        config_names = datasets.config_names
        
        # Load and save each dataset configuration
        for config_name in config_names:
            dataset = datasets.load(config_name=config_name)
            datasets.save(dataset=dataset, config_name=config_name, data_path=self.data_path)

if __name__ == "__main__":
    main()
