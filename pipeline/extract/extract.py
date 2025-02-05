"""Production script to extract data from each plant of the 50.
data should be a list in dictionaries ready for transformation at the next stage"""

import logging
from requests import get, exceptions


logger = logging.getLogger(__name__)  # Create logger for this module
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
# (The basicConfig line is here for demonstration. In production it may be set elsewhere.)


def get_max_plant_id(base_url: str) -> int:
    """Returns greatest ID predicted by max_plants_on_display."""
    response = get(base_url, timeout=10)
    data = response.json()
    if data and "plants_on_display" in data:
        return data["plants_on_display"]
    raise ValueError("Failed to fetch status information. Status code: %s" %
                     response.status_code)

def extract_plant_batch() -> list[dict]:
    """Returns list of dictionaries for all successful plant get requests."""
    base_url = "https://data-eng-plants-api.herokuapp.com/"
    plant_data_list = []
    max_plant_id = get_max_plant_id(base_url)
    logger.info("Data for %d plants is available...", max_plant_id)
    max_plant_id += max_plant_id // 10  # Adds 10% leeway to account for missing plants

    for plant_id in range(1, max_plant_id + 1):
        try:
            plant_data = get_plant_data(base_url, plant_id)
            plant_data_list.append(plant_data)
        except ValueError as e:
            logger.error("Error fetching data for plant ID %d: %s", plant_id, e)

    logger.info("Retrieved data for %d plants.", len(plant_data_list))
    return plant_data_list


def get_plant_data(base_url: str, plant_id: int) -> dict:
    """
    Returns data for a specific plant based on its ID number.

    Raises:
        ValueError: If the data for the plant cannot be fetched.
    """
    url = f"{base_url}plants/{plant_id}"
    try:
        response = get(url, timeout=7)
    except exceptions.ReadTimeout as e:
        raise ValueError("Request timed out for plant ID %d: %s" % (plant_id, e)) from e

    if response.status_code == 200:
        plant_data = response.json()
        logger.info("Successfully fetched data for Plant ID %d", plant_id)
        return plant_data

    raise ValueError("Failed to fetch data for plant ID %d. Status code: %d" %
                     (plant_id, response.status_code))


if __name__ == "__main__":
    main_data = extract_plant_batch()
    logger.info("%s", main_data)
