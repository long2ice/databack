import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCHEDULER_SLEEP_SECONDS = 60
MASK_KEYS = [
    "password",
    "old_password",
    "new_password",
]
