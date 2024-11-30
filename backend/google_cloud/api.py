import os
import pandas as pd
import pandas_gbq
from google.cloud import bigquery
from google.cloud import storage

DEBUG = False


class GoogleCloudAPI():
    def __init__(self):
        self.__project_id = os.getenv('GCP_PROJECT_ID')
        self._dataset = os.getenv('GCP_BQ_DATASET') + '_' +  os.getenv('STREAMLIT_ENV')
        self.__location = os.getenv('GCP_LOCATION')
        self.__bucket_name = os.getenv('GCP_CGS_BUCKET')
        self.__bucket_dir = os.getenv('GCP_CGS_BUCKET_DIR')


    def sql_to_pandas(self, sql: str) -> pd.DataFrame:
        ''' Run a regular SQL query 
        and return a pandas DataFrame.
        
        Inputs
        ------
        sql : string
            A regular SQL query

        Returns
        -------
        df : DataFrame
        '''
        self.__debug(sql=sql)
        df = pandas_gbq.read_gbq(sql, 
                                 project_id=self.__project_id,
                                 location=self.__location, 
                                 progress_bar_type=None) # Use default Account/Cloud Run SA
        return df
    

    def write_pandas_to_table(self, df: pd.DataFrame, table: str):
        ''' Push a DataFrame to BigQuery.

        A new table will be create, if the destination does not exists,
        however, pyarrows has a bug and it fails for datetime columns,
        thus the schema must be constructed manually from pandas to GBQ format.
        The mode is locked to Append only, to prevent accidental overwrites
        
        Inputs
        ------
        df : pd.DataFram
            A regular DataFrame
        table : str
            The name of destination Table, that is used together with initial project parameters
        '''
        table_schema = [] # [{'name': 'col1', 'type': 'STRING'},...]
        for col in df.columns:
            if 'date' in col.lower():
                 table_schema.append({'name': col, 'type': 'DATE'})
            elif 'object' in str(df[col].dtype):
                 table_schema.append({'name': col, 'type': 'STRING'})
            elif 'float' in str(df[col].dtype):
                table_schema.append({'name': col, 'type': 'FLOAT64'})
            elif 'datetime' in str(df[col].dtype):
                table_schema.append({'name': col, 'type': 'TIMESTAMP'})

        pandas_gbq.to_gbq(df, 
                          destination_table=f'{self._dataset}.{table}',
                          project_id=self.__project_id, 
                          location=self.__location, 
                          table_schema=table_schema,
                          if_exists='append',
                          ) # Use default Account/Cloud Run SA
    

    def write_rows_to_table(self, rows_to_insert: list, table: str) -> bool:
        ''' Write rows to an existing table.

        Note, writing one row from the list may fail, but others are completed successfully.
        
        Inputs
        ------
        rows_to_insert : list[dict]
            A DataBase row in a dict format
        table: str
            The name of the destination Table, that is used together with initial project parameters

        Returns
        -------
        success: bool
            If the insert operation results any errors, those a printed and False is returned
        '''
        self.__debug(rows=rows_to_insert, table=table)
        client = bigquery.Client(location=self.__location) # Use default Account/Cloud Run SA
        
        table_id = f'{self.__project_id }.{self._dataset}.{table}'

        errors = client.insert_rows_json(table_id, rows_to_insert)

        if len(errors) > 0:
            print(f'Writing rows to table failed: {errors}')
            return False
        else:
            return True
        
    
    def upload_file_to_gcs(self, local_file_path: str):
        ''' Upload Local File to GCS
        
        The Bucker and folder are project specific,
        and only the <local_file_path> is required

        Inputs
        ------
        local_file_path : str
            Name/Dir of the file to be uploaded with the same dir
        '''
        gcs_path = os.path.join(self.__bucket_dir, local_file_path)

        client = storage.Client() # Use default Account/Cloud Run SA
        bucket = client.get_bucket(self.__bucket_name)
        blob = bucket.blob(gcs_path)
        blob.upload_from_filename(local_file_path) 

    
    def download_file_from_gcs(self, local_file_path: str):
        ''' Download a file from GCS to local filesystem.

        The direcotry is the same on the both platforms
        
        Inputs
        ------
        local_file_path : str
            Name/Dir of the file to be downloaded with the same dir
        '''
        gcs_path = os.path.join(self.__bucket_dir, local_file_path)

        client = storage.Client() # Use default Account/Cloud Run SA
        bucket = client.get_bucket(self.__bucket_name)
        blob = bucket.blob(gcs_path)
        blob.download_to_filename(local_file_path)
        

    def __debug(self, **kwargs):
        if DEBUG:
            print(f'\nGoogleCloudAPI:')
            for key, value in kwargs.items():
                print(f'{key}:\n{value}')
            print('\n')
        
            
        