# LMNH Plant Dashboard
Dashboard for the LMNH staff and management.

## Getting Started 🔨

To run the dashboard, ensure you have completed the following steps:
- Create a file called `.env` to store database variables.
- Your .env should have the following format:
  ```
  DB_NAME=XXXX
  DB_PORT=XXXX
  DB_USER=XXXX
  DB_HOST=XXXX
  DB_PASSWORD=XXXX
  ```


## Dependencies 🛠️

To install dependencies, run the following in your terminal:
  
  ```
  python3 venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

- This creates a virtual environment that will allow you to install the required python packages.

## Usage 🫡
- To run, use the following command in your terminal:
 
  `streamlit run dashboard.py`

## Additional Information ❓
- The following terms have been decided by the described metrics.
- The ideal temperature range for photosynthesis and respiration is **between 15-30°C**. 
  - **Above Ideal Temperature**: > 32°C
  - **Below Ideal Temperature**: < 13°C
  
- The ideal soil moisture levels for plants is **between 21-40%**.
  - **Above Ideal Soil Moisture**: > 60%
  - **Below Ideal Soil Moisture**: < 18%

- Ideally, plants should be watered every **4-5 days**.
  - **Needs Watering**: Plant has not been watered in >= 6 days
  - **Watered Recently**: Plant has been watered in last 5 days

- A plant is **healthy** if it is within the stated metrics, and **unhealthy** otherwise.

