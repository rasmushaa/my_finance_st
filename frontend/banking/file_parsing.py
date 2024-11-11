import streamlit as st
import pandas as pd


# Utilities
def predict():
    if not st.session_state['api']['ml'].has_model():
        st.session_state['api']['ml'].load_model_from_gcs()

    preds, probs = st.session_state['api']['ml'].predict(st.session_state['banking_file'])

    st.session_state['banking_file']['category'] = preds
    st.session_state['banking_file']['confidence'] = probs

def highlight_rows(row):
    return ['background-color: grey' if i % 2 != 0 else '' for i in range(len(row))]

@st.cache_data
def get_categories():
    # Get ordered list of old categories by the Prior, and add any new categories to the end of it
    all_categories = st.session_state['api']['categories'].get_expenditure_categories()
    priors = st.session_state['api']['ml'].get_priors()
    prior_keys = list(priors.keys())
    missing_cateogries = [item for item in all_categories if item not in prior_keys]
    prior_keys .extend(missing_cateogries)
    return prior_keys

def push_data():
    if st.session_state['api']['files'].add_transactions_to_database(edited_df, user_name=st.session_state['user'].name):
            st.success('File added successfully')
    else:
        st.error('File was not uploaded, or the operation was only partially completed...')



if st.session_state['banking_file']['category'].isna().all():
    predict()

edited_df = st.data_editor(
    st.session_state['banking_file'],
    column_config={
        'date': st.column_config.Column(
            'Date',
            disabled=True,
            width='small'
        ),
        'amount': st.column_config.NumberColumn(
            'Amount [€]',
            format="%.2f",
            disabled=True,
            width='small'
        ),
        'receiver': st.column_config.Column(
            'Receiver',
            disabled=True
        ),
        'category': st.column_config.SelectboxColumn(
            'Category',
            options=get_categories()
        ),
        'confidence': st.column_config.ProgressColumn(
            'Confidence',
            format='%.1f',
            min_value=0.0,
            max_value=1.0,
        ),
    },
    use_container_width=True,
    hide_index=True,
    height=35*len(st.session_state['banking_file'])+38
)

if st.button('Upload the file', use_container_width=True):

    if st.session_state['api']['files'].date_not_in_database(edited_df['date'].min(), user_name=st.session_state['user'].name): # Check for duplicated Dates
        push_data()

    else:
        st.error(f"There already exists DATE after '{edited_df['date'].min()}' for user '{st.session_state['user'].name}'")

        st.button('Force Push Data?', on_click=push_data, use_container_width=True)


