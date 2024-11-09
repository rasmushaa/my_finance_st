import pandas as pd
import chardet
import csv
from backend.google_cloud.api import GoogleCloudAPI

class FilesAPI(GoogleCloudAPI):
    def __init__(self):
        self.__client = GoogleCloudAPI()


    def open_binary_as_pandas(self, input_file) -> pd.DataFrame:
        encoding, separator = self.__autodetect_file_coding(input_file)
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        return df
    

    def add_filetype_to_databases(self, **kwargs) -> bool:
        kwargs['ColumnNameString'] = ','.join(kwargs['ColumnNameString'])
        self.__client.write_rows_to_table([kwargs], 'd_filetypes')

    
    def transform_input_file(self, df: pd.DataFrame):
        cols = df.columns.to_list()
        col_str = ','.join(cols)
        sql=f"""
        SELECT
            *
        FROM
            `{self.__client._dataset}.d_filetypes`
        WHERE
            ColumnNameString = '{col_str}'
        """
        filetype = self.__client.sql_to_pandas(sql).iloc[0].to_dict()

        df.rename(columns={filetype['DateColumn']: 'date', filetype['ReceiverColumn']: 'receiver', filetype['AmountColumn2']: 'amount'}, inplace=True)

        df['date'] = pd.to_datetime(df['date'], format=filetype['DateColumnFormat']).dt.date
        df['amount'] = df['amount'].str.replace(',', '.').astype(float) if df['amount'].str.contains(',').any() else df['amount'].astype(float) # Decimael ',' to '.' float
        df['category'] = 'NAN'

        df = df[['date', 'receiver', 'amount', 'category']].copy()
        df.sort_values(by='date', ascending=True, inplace=True)
        return df


    def filetype_is_in_database(self, df: pd.DataFrame) -> bool:
        cols = df.columns.to_list()
        col_str = ','.join(cols)
        sql = f"""
        SELECT
            COUNT(*) AS count
        FROM
            `{self.__client._dataset}.d_filetypes`
        WHERE
            ColumnNameString = '{col_str}'
        """
        df = self.__client.sql_to_pandas(sql)
        return df['count'].all() > 0


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
    
