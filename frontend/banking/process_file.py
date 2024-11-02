import streamlit as st
import pandas as pd
#from frontend.utils import sidebar
from backend.files_api import FilesAPI


@st.cache_data
def st_wrapper_filetype_in_database(df: pd.DataFrame):
    api = FilesAPI()
    return api.filetype_is_in_database(df)

#sidebar.init_to_user_access_level()

if 'input_file' not in st.session_state:
    st.session_state['input_file'] = None



def read_file():
    if st.session_state['input_file'] is None:
        uploaded_file = st.file_uploader('Choose a Banking CSV-file', type=['csv'])
        if uploaded_file is not None:
            st.session_state['input_file'] = FilesAPI().open_binary_as_pandas(uploaded_file) 
            st.rerun() # Hide the upload box
        else:
            st.session_state['input_file'] = None

def validate_filetype():
    if st.session_state['input_file'] is not None:
        if not st_wrapper_filetype_in_database(st.session_state['input_file']):

            st.warning('Unknown FileType, please add the required information:')

            cols = st.session_state['input_file'].columns.to_list()

            st_col1, st_col2 = st.columns(2)
            date_col = st_col1.selectbox('Date-Column', cols)
            date_for = st_col1.selectbox('Date-Format', ['%Y-%m-%d', '%d.%m.%Y', '%m/%d/%Y'])
            receiver_col = st_col2.selectbox('Receiver-Column', cols)
            amount_col = st_col2.selectbox('Amount-Column', cols)

            if st.button('Add the Filetype to the Database', use_container_width=True):
                FilesAPI().add_filetype_to_databases(cols, date_col, date_for, receiver_col, amount_col)
                st.rerun() # Hide the upload box

            st.subheader('Your Banking File')
            st.dataframe(st.session_state['input_file'])


def parse_file():
    st.success('Parced File!')



    

    

st.title('Banking File Processing')

read_file()
validate_filetype()
parse_file()
st.success('Procesing')

#st.session_state['input_file'] = None