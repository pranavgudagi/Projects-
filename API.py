from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import os
import requests
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Load environment variables from a .env file (if exists)
load_dotenv()

# Function to fetch data from the API
def fetch_data_from_api(url, access_key, symbols, **kwargs):
    querystring = {
        "access_key": access_key,
        "symbols": symbols
    }
    try:
        response = requests.get(url, params=querystring)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        if response:
            print(f"Status Code: {response.status_code}, Response: {response.text}")
        return None

# Function to clean the data
def clean_data(data, **kwargs):
    if 'data' not in data:
        print("API response does not contain expected 'data' field.")
        return None

    user_info = data.get('data', [])
    if not user_info:
        print("No data available for the specified query.")
        return None

    # Convert the data into a pandas DataFrame
    df = pd.DataFrame(user_info)

    # Columns to drop
    columns_to_drop = [
        'exchange', 'adj_close', 'adj_high', 'adj_low',
        'adj_open', 'adj_volume', 'split_factor', 'dividend'
    ]
    df.drop(columns=columns_to_drop, inplace=True, errors='ignore')

    # Drop rows with any missing values
    df.dropna(inplace=True)

    # Convert 'date' column to datetime format
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df.dropna(subset=['date'], inplace=True)

    # Rename columns for better readability
    df.rename(columns={
        'open': 'Opening Price',
        'high': 'Highest Price',
        'low': 'Lowest Price',
        'close': 'Closing Price',
        'volume': 'Trading Volume'
    }, inplace=True)

    return df

# Function to save the cleaned data into MySQL database using SQLAlchemy
def save_data_to_db(df, db_url, table_name="new_table", **kwargs):
    engine = create_engine(db_url)
    try:
        # Use engine.connect() for proper connection handling
        with engine.connect() as connection:
            # Create the table in the database (if it doesn't exist)
            df.to_sql(table_name, con=connection, if_exists='replace', index=False)
            print(f"Data successfully saved to the table '{table_name}'.")
    except SQLAlchemyError as e:
        print(f"Error saving data to MySQL: {str(e)}")
    except ValueError as ve:
        print(f"ValueError while saving data: {str(ve)}")

# Define the DAG
dag = DAG(
    'api_data_dag',  # Name of the DAG
    description='A DAG that fetches data from an API and saves it to MySQL',
    schedule=timedelta(minutes=1),  # Runs every minute
    start_date=datetime(2025, 1, 25),  # Adjust the start date
    catchup=False,  # Do not backfill
)

# Define the tasks
url = "https://api.marketstack.com/v1/eod"
access_key = os.getenv('MARKETSTACK_ACCESS_KEY')  # Fetch API key from environment variables
symbols = "AAPL"  # Replace with desired symbols
db_url = os.getenv('DATABASE_URL', 'mysql+pymysql://your database name and pass @localhost:3306/sales_data')

# Task 1: Fetch data from API
fetch_data_task = PythonOperator(
    task_id='fetch_data_from_api',
    python_callable=fetch_data_from_api,
    op_args=[url, access_key, symbols],
    dag=dag,
)

# Task 2: Clean the fetched data
clean_data_task = PythonOperator(
    task_id='clean_data',
    python_callable=clean_data,
    op_args=['{{ task_instance.xcom_pull(task_ids="fetch_data_from_api") }}'],  # Pull data from the fetch_data task
    dag=dag,
)

# Task 3: Save data to the database
save_data_task = PythonOperator(
    task_id='save_data_to_db',
    python_callable=save_data_to_db,
    op_args=['{{ task_instance.xcom_pull(task_ids="clean_data") }}', db_url],  # Pull cleaned data from clean_data task
    dag=dag,
)

# Set task dependencies
fetch_data_task >> clean_data_task >> save_data_task
