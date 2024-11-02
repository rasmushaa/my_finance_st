import pandas as pd
import chardet
import csv
from .bigquery_api import BigQueryAPI

class FilesAPI(BigQueryAPI):
    def __init__(self):
        self.__client = BigQueryAPI()


    def open_binary_as_pandas(self, input_file) -> pd.DataFrame:
        encoding, separator = self.__autodetect_file_coding(input_file)
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        return df
    

    def add_filetype_to_databases(self, input_file, **kwargs):
        print('Addde file type\n')



    def filetype_is_in_database(self, df: pd.DataFrame):
        columns_names = df.columns.to_list()
        print(columns_names)
        return False
        sql = f"""
        SELECT
            COUNT(*) AS count
        FROM
            {self.__client._dataset}.d_file_types
            """


    def __autodetect_file_coding(self, file_binary) -> str:
        ''' 
        Auto detects used encoding and separator in csv file.

        If file parameters are unkwown, it has to be first opened in binary
        to avoid any parsing errors.

        Parameters
        ----------
        file_binary : A subclass of BytesIO
            The raw input file from Streamlit File Uploader

        Returns
        -------
        encoding : str
            Detected encoding. Note, chardet works well, but its not perfect!
        separator : str
            Detected separator in [',', ';', '', '\t', '|']
        '''
        encoding_dict = chardet.detect(file_binary.getvalue())
        encoding = encoding_dict['encoding']

        dialect = csv.Sniffer().sniff(file_binary.getvalue().decode(encoding), delimiters=[',', ';', '', '\t', '|'])
        separator = dialect.delimiter

        return encoding, separator
    
