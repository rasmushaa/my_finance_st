import pandas as pd
import chardet
import csv
from backend.google_cloud.api import GoogleCloudAPI


class FileParser:
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

        df.rename(columns={filetype['DateColumn']: 'KeyDate', filetype['ReceiverColumn']: 'Receiver', filetype['AmountColumn']: 'Amount'}, inplace=True)

        df['KeyDate'] = pd.to_datetime(df['KeyDate'], format=filetype['DateColumnFormat']).dt.date
        df['Amount'] = df['Amount'].str.replace(',', '.').astype(float) if df['Amount'].str.contains(',').any() else df['Amount'].astype(float) # Decimael ',' to '.' float
        df['Category'] = None

        df = df[['KeyDate', 'Amount', 'Receiver', 'Category']].copy()
        df.sort_values(by='KeyDate', ascending=True, inplace=True)
        return df
    

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