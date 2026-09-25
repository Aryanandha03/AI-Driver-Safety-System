import json
import os


DATABASE_PATH = os.path.join(
    os.path.dirname(__file__),
    "database",
    "drivers.json"
)


def load_drivers():
    with open(DATABASE_PATH, "r", encoding="utf-8") as file:
        return json.load(file)


def get_driver(drivers, driver_id):
    return drivers.get(driver_id)