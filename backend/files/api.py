import pandas as pd
import chardet
import csv
from backend.google_cloud.api import GoogleCloudAPI

class FilesAPI(GoogleCloudAPI):
    def __init__(self):
        self.__client = GoogleCloudAPI()


    def open_binary_as_pandas(self, input_file) -> pd.DataFrame:
        ''' Open provided unkown CSV safely.
        
        The text encoding, and seperator characters are unkown,
        and must be determined manaully using external libraries.

        Inputs
        ------
        input_file : Streamlit BytesIO
            User provided file, that is validate to be a csv
        '''
        encoding, separator = self.__autodetect_file_coding(input_file)
        df = pd.read_csv(input_file, encoding=encoding, sep=separator)
        return df
    

    def add_filetype_to_databases(self, **kwargs) -> bool:
        ''' Add a new supported filetype row to database.
        
        The ColumnNameString is a common string that contains all of the column names,
        that is used to identify different file.
        The table contains required information to select correct columns to run analysis.

        Inputs
        ------
        Keyvalue-pairs
            The key is going to be the column name, and value is the row value
        '''
        kwargs['ColumnNameString'] = ','.join(kwargs['ColumnNameString'])
        self.__client.write_rows_to_table([kwargs], 'd_filetypes')


    def add_transactions_to_database(self, df: pd.DataFrame, user_name: str) -> bool:
        ''' Push one Banking file to database.
        
        The table is created, if not already exist.
        Ether the whoele df is uploaded, or it fails completely.

        Inputs
        ------
        df: pd.DataFrame
            The Banking File
        user_name: str
            The current active user
        '''
        df['category'] = df['category'].fillna('N/A') # Different missing values can have multiple values: Nan, Empty, etc. Thus, 'N/A' is selected to handle this
        df['user'] = user_name
        df['commit_timestamp'] = pd.Timestamp('now', tz='Europe/Helsinki')
        df = df[['user', 'date', 'amount', 'receiver', 'category', 'commit_timestamp']]
        try:
            self.__client.write_pandas_to_table(df, 'f_transactions')
        except:
            return False
        return True


    def date_not_in_database(self, date, user_name: str):
        ''' Prevent from adding multiple same banking files to the database.
        The date validation is user specific.
        
        Inputs
        ------
        date: datetime
            The minimum date in the Banking File
        user_name: str
            The current active user
        '''
        sql = f'''
        SELECT
            MAX(date) AS date
        FROM
            {self.__client._dataset}.f_transactions
        WHERE
            user = '{user_name}'
        '''
        try:
            results = self.__client.sql_to_pandas(sql) # The Query Fails if the table does not exist -> return True instead
        except:
            return True
        return date > results['date'][0]

    
    def transform_input_file(self, df: pd.DataFrame):
        ''' The Raw CSV input file is transformed into the required format
        
        The file is assumed to be known in this part, and its recorded column
        format is quered to transform it into the expected format.
        Floats and Dates are also handled.

        Inputs
        ------
        df: pd.DataFrame
            The user input csv file 
        '''
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
        df['category'] = None

        df = df[['date', 'amount', 'receiver', 'category']].copy()
        df.sort_values(by='date', ascending=True, inplace=True)
        return df


    def filetype_is_in_database(self, df: pd.DataFrame) -> bool:
        ''' Checks whether the file type is known
        
        Inputs
        ------
        df: pd.DataFrame
            The user input csv file 
        '''
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
    
