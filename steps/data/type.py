import os
from pathlib import Path
from typing import cast

from datasets import DatasetDict, Dataset, load_dataset, get_dataset_config_names

class EquiBenchDatasets:
    def __init__(self):
        self.hf_path = "anjiangwei/EquiBench-Datasets"

    @staticmethod
    def check_huggingface_login():
        """Check Hugging Face CLI login status"""
        print("Check Hugging Face CLI login status:")
        if os.system("huggingface-cli whoami") != 0:
            raise RuntimeError("Please log in to Hugging Face using 'huggingface-cli login'.")

    @property
    def config_names(self) -> list[str]:
        """Retrieves the configuration names for the dataset.

            list[str]: A list of configuration names for the dataset.
        """
        config_names = get_dataset_config_names(self.hf_path)
        print(f"{self.hf_path} Dataset configurations: {config_names}")
        return config_names

    def load(self, config_name: str) -> Dataset:
        """Load and save a specific configuration of the EquiBench dataset"""
        dataset_dict = cast(DatasetDict, load_dataset(self.hf_path, name=config_name))
        print(f"{self.hf_path} Loading configuration: {config_name}")
        assert dataset_dict.keys() == {"train"}
        dataset = dataset_dict["train"]
        print(dataset)
        return dataset

    def save(self, config_name: str, dataset: Dataset, data_path: Path):
        """Save the loaded dataset to disk in JSON format with indent=4"""
        json_path = data_path / config_name / f"pairs.json"
        dataset.to_json(json_path, orient="records", lines=False, indent=4)
        print(f"Saved {config_name} to {json_path}")
