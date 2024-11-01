import sys
import os
from dotenv import load_dotenv
from google.cloud import bigquery
from google.cloud.exceptions import Conflict

# How to run: python3 init_bigquery_database.py <name of the environment, dev, stg, prod, etc.>


def __create_table(dataset: bigquery.Table, table_name: str, schema: list, client: bigquery.Client) -> None:
    table = dataset.table(table_name)
    table = bigquery.Table(table, schema=schema)
    table = client.create_table(table)
    print(f'Created table: {table.project}.{table.dataset_id}.{table.table_id}')


def main():

    # 1. Verify User Inputs Env: Dev, Stg, Prod
    if len(sys.argv) != 2 or sys.argv[1] not in ['dev', 'stg', 'prod']:
        print("Usage: python init_bigquery_databse.py <dev, stg, prod>")
        sys.exit(1)

    print(f'\nConstructing BigQuery Database for {sys.argv[1]}-environment')



    # 2 Set build configuration
    dotenv_file = f".env"
    if os.path.exists(dotenv_file):
        load_dotenv(dotenv_file)
    else:
        raise ValueError(f'No path: {dotenv_file}')
    
    project_id = os.getenv('GCP_PROJECT_ID')
    dataset_id = f"st_workout_{sys.argv[1]}"
    location = 'europe-north1'
  

    # 3. Initializea BigQuery client object for Creating Non-Existant Databasets/Tables
    client = bigquery.Client()


    # 4. Construct a Dataset object to send to the API.
    dataset = bigquery.Dataset(f"{project_id}.{dataset_id}")
    dataset.location = location
    try:
        dataset = client.create_dataset(dataset, timeout=30)
        print(f"Created dataset: {project_id}.{dataset_id} at {location}")
    except Conflict as e:
        print(f"Warning: there already exists a '{dataset_id}' dataset in the '{project_id}' project\nAborting Initalization, Nothing was updated...\n")
        return bigquery.exceptions


    # 5. Create Credentials table
    schema = [
    bigquery.SchemaField('KeyUserId',       'INTEGER',  mode="REQUIRED"),
    bigquery.SchemaField('UserName',        'STRING',   mode="REQUIRED"),
    bigquery.SchemaField('Role',            'STRING',   mode="REQUIRED"),
    bigquery.SchemaField('PasswordHash',    'STRING',   mode="REQUIRED"),
    ]
    __create_table(dataset, 'd_credentials', schema, client)


    # 6. Create Excercise Names table
    schema = [
    bigquery.SchemaField('KeyWorkoutId',  'INTEGER',  mode="REQUIRED"),
    bigquery.SchemaField('WorkoutName',   'STRING',   mode="REQUIRED"),
    ]
    __create_table(dataset, 'd_workout', schema, client)



if __name__ == "__main__":
    main()