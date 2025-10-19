import streamlit as st
from frontend.utils import valid_user_state

valid_user_state()

# Utlity function to run deletion
def run_deletion():
    for _, row in st.session_state['to_delete'].iterrows():
        st.session_state.backend.filesystem.database.delete_push_insertion(
            user_name=row['KeyUser'],
            commit_timestamp=row['CommitTimestamp'],
            table=row['TableName']
        )
        st.toast(f'{row["KeyUser"]} - {row["TableName"]} - {row["CommitTimestamp"]}', icon='🗑️', duration='infinite')
    st.session_state.pop('to_delete')
    st.rerun()


st.set_page_config(layout="wide")
_, col, _ = st.columns([1,2,1])

col.title('Transaction Insertations Log')

df = st.session_state.backend.filesystem.database.get_all_push_insertions()
df['selection'] = False

group = col.container(horizontal=True, width='stretch')
users = group.pills('Users', df['KeyUser'].unique().tolist(), selection_mode='multi', default=df['KeyUser'].unique().tolist())
files = group.pills("Tables", df['TableName'].unique().tolist(), selection_mode='multi', default=df['TableName'].unique().tolist())

df_selection = df.loc[df['KeyUser'].isin(users) & df['TableName'].isin(files)]

col.header('Select insertation batch to be deleted')
edited_df = col.data_editor(
    df_selection.reset_index(drop=True),
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
    height=35*df_selection.shape[0] + 38
)

if edited_df['selection'].any():

    with col:
        st.divider()
        st.header('You have selected rows for deletion')
        st.dataframe(
            edited_df[edited_df['selection']],
            hide_index=True,
            width='stretch'
        )

        st.divider()

        if st.button('Delete Selected Insertations', width='stretch'):
            st.session_state['to_delete'] = edited_df[edited_df['selection']]

        if 'to_delete' in st.session_state:
            st.warning('This action is irreversible! All data associated with the selected insertations will be permanently deleted from the database.', icon='⚠️')
            if st.button('ARE YOU SURE?', type='primary', width='stretch'):
                with st.spinner('Removing data...', show_time=True):
                    run_deletion()
