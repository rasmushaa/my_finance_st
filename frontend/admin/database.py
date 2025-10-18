import streamlit as st
import time
import pandas as pd
from frontend.utils import valid_user_state

valid_user_state()

# Utlity function to run deletion
@st.cache_data()
def st_wrapper_get_all_push_insertions():
    return st.session_state.backend.filesystem.database.get_all_push_insertions()

def run_deletion(to_delete: pd.DataFrame):
    for _, row in to_delete.iterrows():
        st.session_state.backend.filesystem.database.delete_push_insertion(
            user_name=row['KeyUser'],
            commit_timestamp=row['CommitTimestamp'],
            table=row['TableName']
        )
    st_wrapper_get_all_push_insertions.clear()


st.set_page_config(layout="wide")
_, col, _ = st.columns([1,2,1])

col.title('Transaction Insertations Log')
col.header('Select insertation batch to be deleted')

df = st_wrapper_get_all_push_insertions()
df['selection'] = False

df['CommitTimestamp'] = pd.to_datetime(df['CommitTimestamp'], format='%Y-%m-%d %H:%M:%S')
df = df.sort_values(by=['KeyUser', 'TableName', 'CommitTimestamp']).reset_index(drop=True)

edited_df = col.data_editor(
    df,
    column_config={
        'KeyUser': st.column_config.Column(
            'Username',
            disabled=True
        ),
        'CommitTimestamp': st.column_config.Column(
            'Commit Timestamp',
            disabled=True,
        ),
        'RowCount': st.column_config.Column(
            'Number of Inserted Rows',
            disabled=True,
        ),
        'MinDate': st.column_config.Column(
            'First Date',
            disabled=True,
        ),
        'MaxDate': st.column_config.Column(
            'Last Date',
            disabled=True,
        ),
        'DistinctReceivers': st.column_config.Column(
            'Distinct Receivers',
            disabled=True,
        ),
        'DistinctCategories': st.column_config.Column(
            'Distinct Categories',
            disabled=True,
        ),
        'TotalAmount': st.column_config.Column(
            'Total Amount',
            disabled=True,
        ),
        'selection': st.column_config.CheckboxColumn(
            "Select",
            help="Select rows for deletion",
            default=False,
        )


    },
    hide_index=True,
    height=35*df.shape[0] + 38
)

if edited_df['selection'].any():

    with col:
        st.divider()
        st.header('You have selected rows for deletion')
        st.dataframe(
            edited_df[edited_df['selection']],
            hide_index=True,
            use_container_width=True
        )

        st.divider()

        if st.button('Delete Selected Insertations', use_container_width=True):
            to_delete = edited_df[edited_df['selection']]
            if st.button('ARE YOU SURE?', type='primary', use_container_width=True, on_click=run_deletion, args=(to_delete,)):
                st.success('Selected insertations have been deleted successfully!')
                #time.sleep(1.0)
                #st.rerun()
