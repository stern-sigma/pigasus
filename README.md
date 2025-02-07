# Liverpool Natural History Museum Pipeline & Dashboard

Deploys cloud resources, upload live plant data to a database and present the data on a dashboard.

## Getting Started 🔨
To start with, follow the instructions in the README in the `cloud resources`.

For the everything to work, the following must be set up:

- Create a file called '.env' to store database variables.
- Your .env should have the following format:
  ```
    DB_NAME = XXXXX
    DB_HOST = XXXXX
    DB_PASSWORD = XXXXX
    DB_USER = XXXXX
    DB_PORT = XXXXX
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
- To deploy the cloud services, run the following command:
  ```
    terraform init
    terraform apply
    yes
  ```

- To run the pipeline to insert plant health data into the database, run the following command:
 `python3 etl.py`
- The long_term.py storage script will delete plant data older than 24 hours from the database and store it in parquet files.
- The dashboard script can be run using the command:
`streamlit run dashboard.py`



