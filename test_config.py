"""Simple verification that config.py values load correctly."""
from src import config


def print_config():
    values = config.as_dict()
    for key, value in values.items():
        print(f"{key}: {value}")
    print("All configuration values loaded successfully from config.py")


if __name__ == "__main__":
    print_config()
