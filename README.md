Airflow API-to-MySQL Data Pipeline
This project uses Apache Airflow to create a DAG (Directed Acyclic Graph) that fetches financial data from the Marketstack API, cleans it, and stores it in a MySQL database.

Overview
The pipeline consists of three tasks:

Fetch Data from API: Retrieves stock market data from the Marketstack API.

Clean Data: Processes the raw data (removes unnecessary columns, handles missing values, renames columns).

Save to MySQL Database: Stores the cleaned data in a MySQL table.

Prerequisites
Python 3.8+

Apache Airflow 2.5+

MySQL Server

Required Python packages:

apache-airflow

pandas

requests

python-dotenv

sqlalchemy

pymysql

Setup
1. Install Dependencies
bash
Copy
pip install apache-airflow pandas requests python-dotenv sqlalchemy pymysql
2. Configure Environment Variables
Create a .env file in your project directory with the following variables:

env
Copy
MARKETSTACK_ACCESS_KEY=your_api_key_here  # Replace with your Marketstack API key
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/database_name  # Replace with your MySQL credentials
3. Initialize Airflow
bash
Copy
airflow db init
airflow webserver --port 8080
airflow scheduler
4. Configure Airflow
Place your DAG file (api_data_dag.py) in the Airflow dags folder (default: ~/airflow/dags).

Ensure MySQL is running and the database/schema specified in DATABASE_URL exists.

DAG Structure
Tasks
Task ID	Description
fetch_data_from_api	Fetches data from the Marketstack API.
clean_data	Cleans and transforms the raw data.
save_data_to_db	Saves the cleaned data to MySQL.
DAG Schedule
Runs every 1 minute (adjustable via schedule=timedelta(minutes=1)).

Start date: 2025-01-25 (modify as needed).

How to Run
Start the Airflow webserver and scheduler:

bash
Copy
airflow webserver --port 8080
airflow scheduler
Access the Airflow UI at http://localhost:8080.

Enable the api_data_dag DAG from the UI.

Monitor task execution in the Airflow dashboard.

Airflow UI Example

Code Structure
plaintext
Copy
your-project/
├── dags/
│   └── api_data_dag.py     # Airflow DAG file
├── .env                    # Environment variables
└── README.md               # Project documentation
Notes
API Key: Sign up for a free API key at Marketstack.

MySQL Setup: Ensure the database/schema specified in DATABASE_URL exists.

XCom: Data is passed between tasks using Airflow's XCom system.

DAG Start Date: Modify start_date=datetime(2025, 1, 25) to a valid past date for immediate testing.
