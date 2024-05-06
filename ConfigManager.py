import json
from typing import List, Dict, Any


class ConfigManager:
    def __init__(self, filename: str) -> None:
        self.filename: str = filename
        self.config: Dict[str, Any] = {
            "USERNAME": "",
            "API_KEY": "",
            "SECRET": "",
            "SHARE_CODES": [],
            "ITEMS": {
                "example": {"intensity": 10, "duration": 1},
                "example2": {"intensity": 10, "duration": 1},
            },
        }

    def load_config(self) -> None:
        try:
            with open(self.filename, "r") as file:
                self.config = json.load(file)
        except FileNotFoundError:
            print("Config file not found. Creating a new one.")
            self.save_config()

    def save_config(self):
        with open(self.filename, "w") as file:
            json.dump(self.config, file, indent=4)

    def get_secret(self) -> str:
        return self.config["SECRET"]

    def get_share_codes(self) -> List[str]:
        return self.config["SHARE_CODES"]

    def get_items(self) -> List[Dict[str, Any]]:
        return self.config["ITEMS"]

    def get_username(self) -> str:
        return self.config["USERNAME"]

    def get_api_key(self) -> str:
        return self.config["API_KEY"]
