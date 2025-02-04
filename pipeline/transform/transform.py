"""This script will transform the data into a usable format for the DB."""
import pandas as pd


def main():
    """Runs main function for the script."""
    raw_data = [
        {'botanist': {'email': 'john.doe@example.com',
        'name': 'John Doe', 'phone': '123456789'},
         'last_watered': '2025-02-01', 'name': 'Plant 1',
         'origin_location': 'Location 1', 'plant_id': 1,
         'recording_taken': '2025-02-01', 'soil_moisture': 0.3, 'temperature': 22},
        {'last_watered': '2025-02-02', 'name': 'Plant 2',
        'origin_location': 'Location 2', 'plant_id': 2,
         'recording_taken': '2025-02-02', 'soil_moisture': 0.4, 'temperature': 21},
        {'botanist': {'email': 'jane.doe@example.com',
        'name': 'Jane Doe', 'phone': '987654321'},
         'last_watered': '2025-02-03', 'name': 'Plant 3',
         'origin_location': 'Location 3', 'plant_id': 3,
         'recording_taken': '2025-02-03', 'soil_moisture': 0.5, 'temperature': 23}
    ]

    get_botanist_data(raw_data)

def get_botanist_data(raw_data:list[dict]):
    """Returns the botanist data into separated columns in a DataFrame."""
    df = pd.DataFrame(raw_data)

    if "botanist" not in df.columns:
        raise KeyError("Botanist was not found!")

    df['botanist_email'] = df['botanist'].apply(
        lambda x: x['email'] if isinstance(
            x, dict) and 'email' in x else None if x is not None else None
    )
    df['botanist_name'] = df['botanist'].apply(
        lambda x: x['name'] if isinstance(
            x, dict) and 'name' in x else None if x is not None else None
    )
    df['botanist_phone'] = df['botanist'].apply(
        lambda x: x['phone'] if isinstance(
            x, dict) and 'phone' in x else None if x is not None else None
    )
    df = df.drop(columns=['botanist'])
    # pylint: disable=E1136
    df = df[[
        'botanist_email',
        'botanist_name',
        'botanist_phone',
        'last_watered',
        'name',
        'origin_location',
        'plant_id',
        'recording_taken',
        'soil_moisture',
        'temperature'
    ]] 
    return df
if __name__ == "__main__":
    main()
