import pandas as pd
import json


def main():
    ...


def get_botanist_data(raw_data):
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
