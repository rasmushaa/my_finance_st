import streamlit as st
import time
from frontend.utils import valid_user_state

valid_user_state()


# Utility functions
@st.cache_data(show_spinner='Validating File entry...')
def st_wrapper_filetype_in_database(df):
    return st.session_state['api']['files'].filetype_is_in_database(df)

@st.cache_data(show_spinner='Transforming the File...')
def st_wrapper_transform_input_file(df):
    return st.session_state['api']['files'].transform_input_file(df)


# Dymaic Visualization Funcs
def load_file():
    if st.session_state['input_file'] is not None:
        st.session_state['banking_file'] = st.session_state['api']['files'].open_binary_as_pandas(st.session_state['input_file'])

def validate_filetype() -> bool:
    if st_wrapper_filetype_in_database(st.session_state['banking_file']):
        st.success('Provided File OK')
        time.sleep(0.5)
        return True

    else:
        st.warning('Unknown FileType, please add the required information:')

        cols = st.session_state['banking_file'].columns.to_list()

        # user inputs
        file_name = st.text_input(label='Give a FileType Name')
        st_col1, st_col2 = st.columns(2)
        date_col = st_col1.selectbox('Date-Column', cols)
        date_for = st_col1.selectbox('Date-Format', ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y'])
        receiver_col = st_col2.selectbox('Receiver-Column', cols)
        amount_col = st_col2.selectbox('Amount-Column', cols)

        if st.button('Add the Filetype to the Database', use_container_width=True):
            st.session_state['api']['files'].add_filetype_to_databases(
                                                    KeyFileName=file_name, 
                                                    DateColumn=date_col, 
                                                    DateColumnFormat=date_for, 
                                                    AmountColumn=amount_col, 
                                                    ReceiverColumn=receiver_col, 
                                                    ColumnNameString=cols)
            
            st_wrapper_filetype_in_database.clear(st.session_state['banking_file']) # Clear for rerunning
            return True

        st.subheader('Your Banking File')
        st.dataframe(st.session_state['banking_file'])
        return False


def parse_file():
    if st_wrapper_filetype_in_database(st.session_state['banking_file']):
        st.session_state['banking_file'] = st_wrapper_transform_input_file(st.session_state['banking_file'])
        st.switch_page('frontend/banking/file_parsing.py')



    
# The Page 
st.title('Banking File Processing')
st.file_uploader('Choose a Banking CSV-file', type=['csv'], key='input_file', on_change=load_file)
if st.session_state['input_file'] is not None:
    if validate_filetype():
        parse_file()

