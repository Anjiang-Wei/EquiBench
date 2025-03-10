# huggingface-cli login
# huggingface-cli whoami

from pathlib import Path
from steps.data import EquiBenchDatasets

def main():
    datasets = EquiBenchDatasets()

    # Check Hugging Face CLI login status
    datasets.check_huggingface_login()
    
    # Load dataset configuration names
    config_names = datasets.config_names
    
    # Load and save each dataset configuration
    datasets_path = Path("data")
    for config_name in config_names:
        dataset = datasets.load(config_name=config_name)
        datasets.save(dataset=dataset, config_name=config_name, save_path=datasets_path / config_name)

if __name__ == "__main__":
    main()
