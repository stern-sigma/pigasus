# Liverpool Natural History Museum Pipeline 

Pipeline to store the plant health data for the Liverpool Natural History Museum (LMNH) botanical wing.

## Getting Started 🔨

For the pipeline script to work, the following must be set up:

- An SQL Server database.

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

- To run the pipeline to insert plant health data into the database, run the following command:
 `python3 etl.py`

