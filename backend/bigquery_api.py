import os
import json
import pandas as pd
import pandas_gbq
from google.cloud import bigquery
from google.oauth2 import service_account


class BigQueryAPI():
    def __init__(self):
        self.__project_id = 'rasmus-prod'
        self._dataset = f'st_workout_{os.getenv("STREAMLIT_ENV")}'
        self.__location = 'europe-north1'


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
        df = pandas_gbq.read_gbq(sql, 
                                 project_id=self.__project_id,
                                 location=self.__location, 
                                 credentials=service_account.Credentials.from_service_account_info(json.loads(os.getenv('GCP_SERVICE_ACCOUNT'))), 
                                 progress_bar_type=None)
        return df
    

    def write_pandas_to_table(self, df: pd.DataFrame, table: str):
        ''' Push a DataFrame to BigQuery.
        A new table will be create, if the destination does not exists.
        The mode is locked to Append only, to prevent accidental overwrites
        
        Inputs
        ------
        df : pd.DataFram
            A regular DataFrame
        table : str
            The name of destination Table, that is used together with initial project parameters
        '''
        pandas_gbq.to_gbq(df, 
                          destination_table=f'{self._dataset}.{table}',
                          project_id=self.__project_id, 
                          location=self.__location, 
                          if_exists='append')
    

    def write_rows_to_table(self, rows_to_insert: list, table: str) -> bool:
        ''' Write rows to an existing table
        
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
        client = bigquery.Client(credentials=service_account.Credentials.from_service_account_info(json.loads(os.getenv('GCP_SERVICE_ACCOUNT'))),
                                 location=self.__location)
        
        table_id = f'{self.__project_id }.{self._dataset}.{table}'

        errors = client.insert_rows_json(table_id, rows_to_insert)

        if len(errors) > 0:
            print(f'Writing rows to table failed: {errors}')
            return False
        else:
            return True
        
            
        