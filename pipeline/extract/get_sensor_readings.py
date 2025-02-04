import csv
from requests import get
from time import time
import json


def get_max_plant_id(base_url: str) -> int:
    """Gets the ID from max plants on display from the API's base URL."""
    response = get(base_url)
    data = response.json()

    if data and "plants_on_display" in data:
        return data["plants_on_display"]
    else:
        print("Failed to fetch status information.")
        return None


def get_plant_data(base_url: str, plant_id: int):
    """Fetch plant data for a given plant ID."""
    url = f"{base_url}plants/{plant_id}"
    response = get(url)

    if response.status_code == 200:
        plant_data = response.json()
        print(f"Successfully fetched data for Plant ID {
              plant_id}")  # Print the plant data
        return plant_data
    else:
        print(f"Failed to fetch data for plant ID {
              plant_id}. Status code: {response.status_code}")
        return None


def save_data_to_json(data, filename="plant_data.json"):
    """Save fetched plant data into a JSON file."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)


def retrieve_plant_data(base_url: str, max_runtime: int = 300):
    """Retrieve plant data for 5 minutes, repeating the process if max ID is reached."""
    max_id = get_max_plant_id(base_url)
    if max_id is None:
        return []

    all_plants_data = []
    start_time = time()
    elapsed_time = 0

    # Run the loop for the specified maximum runtime (5 minutes)
    while elapsed_time < max_runtime:
        for plant_id in range(1, max_id + 1):
            # Fetch data for each plant
            plant_data = get_plant_data(base_url, plant_id)
            if plant_data:
                all_plants_data.append(plant_data)

        # Update elapsed time
        elapsed_time = time() - start_time

    return all_plants_data



if __name__ == "__main__":
    # API Endpoint
    BASE_URL = "https://data-eng-plants-api.herokuapp.com/"
    plant_data = retrieve_plant_data(BASE_URL)
    save_data_to_json(plant_data)
    print(f"Data for {len(plant_data)} plants saved successfully.")
