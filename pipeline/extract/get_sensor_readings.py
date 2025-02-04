"""This script will fetch data from the API to be studied"""
import json

from time import time
from requests import get

def main():
    """Main function to execute the script."""
    base_url = "https://data-eng-plants-api.herokuapp.com/"
    plant_data = retrieve_plant_data(base_url)
    save_data_to_json(plant_data)
    print(f"Data for {len(plant_data)} plants saved successfully.")


def get_max_plant_id(base_url: str) -> int:
    """Returns greatest ID predicted by max_plants_on_display."""
    response = get(base_url, timeout=10)
    data = response.json()
    if data and "plants_on_display" in data:
        return data["plants_on_display"]
    raise ValueError(f"Failed to fetch status information. Status code: {
                         response.status_code}")


def get_plant_data(base_url: str, plant_id: int) -> dict:
    """Returns data for a specific plant based on ID number."""
    url = f"{base_url}plants/{plant_id}"
    response = get(url, timeout=10)

    if response.status_code == 200:
        plant_data = response.json()
        print(f"Successfully fetched data for Plant ID {
              plant_id}")
        return plant_data
    raise ValueError(f"Failed to fetch data for plant ID {
                         plant_id}. Status code: {response.status_code}")


def save_data_to_json(data, filename="plant_data.json") -> None:
    """Saves fetched plant data into a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def retrieve_plant_data(base_url: str, max_runtime: int = 30) -> list[dict]:
    """Returns 5 minutes worth of plant data."""
    try:
        max_id = get_max_plant_id(base_url)
    except ValueError as e:
        print(f"Error: {e}")
        return []

    all_plants_data = []
    start_time = time()
    elapsed_time = 0

    while elapsed_time < max_runtime:
        for plant_id in range(1, max_id + 5):
            try:
                plant_data = get_plant_data(base_url, plant_id)
                if plant_data:
                    all_plants_data.append(plant_data)
            except ValueError as e:
                print(f"Error fetching data for plant ID {plant_id}: {e}")
                continue

        elapsed_time = time() - start_time

    return all_plants_data


if __name__ == "__main__":
    main()
