import streamlit as st
from frontend.utils import valid_user_state

st.set_page_config(layout="wide")
valid_user_state()


# Utilities
def predict():
    if not st.session_state.backend.ml.has_model():
        st.session_state.backend.ml.load_model_from_gcs()

    preds, probs = st.session_state.backend.ml.predict(st.session_state['banking_file'])

    st.session_state['banking_file']['Category'] = preds
    st.session_state['banking_file']['Confidence'] = probs

@st.cache_data(ttl=300)
def get_categories():
    all_categories = st.session_state.backend.categories.get_expenditure_categories()
    old_categories = list(st.session_state.backend.ml.get_priors().keys()) # Get existing categories in desc prior order
    added_cateogries = [item for item in all_categories if item not in old_categories]
    old_categories.extend(added_cateogries)
    return old_categories

def category_formatter(category):
    mapping = {
        'HOUSEHOLD-ITEMS': '🛋️ - ' + category,
        'TECHNOLOGY': '💻 - ' + category,
        'HEALTH': '💊 - ' + category,
        'COMMUTING': '🚃 - ' + category,
        'CLOTHING': '👕 - ' + category,
        'SALARY': '💶 - ' + category,
        'HOBBIES': '💪🏻 - ' + category,
        'UNCATEGORIZED': '❔ - ' + category,
        'FOOD': '🛒 - ' + category,
        'LIVING': '🏠 - ' + category,
        'OTHER-INCOME': '🤝 - ' + category,
        'ENTERTAINMENT': '🎉 - ' + category,
        'INVESTING': '📈 - ' + category,
    }
    return mapping.get(category, category)

def push_data():
    with st.spinner('Sending data...', show_time=True):
        if st.session_state.backend.filesystem.database.add_transactions_to_database(edited_df, user_name=st.session_state['user'].name):
                st.toast('File was uploaded successfully!', icon='✅', duration='long')
        else:
            st.toast('Failure during upload!', icon='⚠️', duration='infinite')



if st.session_state['banking_file']['Category'].isna().all():
    predict()

_, col, _ = st.columns([1,2,1])
edited_df = col.data_editor(
    st.session_state['banking_file'],
    column_config={
        'KeyDate': st.column_config.Column(
            'Date',
            disabled=True,
            width='small'
        ),
        'Amount': st.column_config.NumberColumn(
            'Amount [€]',
            format="%.2f",
            disabled=True,
            width='small'
        ),
        'Receiver': st.column_config.Column(
            'Receiver',
            disabled=True,
        ),
        'Category': st.column_config.SelectboxColumn(
            label='Category',
            options=get_categories(),
            width='large',
            format_func=category_formatter,
        ),
        'Confidence': st.column_config.ProgressColumn(
            'Confidence',
            format='%.1f',
            min_value=0.0,
            max_value=1.0,
        ),
    },
    hide_index=True,
    height=35*len(st.session_state['banking_file'])+38
)

with col:
    if st.button('Upload the file', width='stretch'):
        if st.session_state.backend.filesystem.database.date_not_in_transactions_table(edited_df['KeyDate'].min(), user_name=st.session_state['user'].name): # Check for duplicated Dates
            push_data()
        else:
            st.error(f"There already exists DATE after '{edited_df['KeyDate'].min()}' for user '{st.session_state['user'].name}'")
            st.button('Force Push Data?', on_click=push_data, width='stretch')


