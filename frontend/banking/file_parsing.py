import streamlit as st


@st.cache_data
def st_wrapper_predict(df, threshold):
    if not st.session_state['api']['ml'].has_model():
        st.session_state['api']['ml'].load_model_from_gcs()

    return st.session_state['api']['ml'].predict(df, threshold)



st.dataframe(st.session_state['banking_file'])


pred =st_wrapper_predict(st.session_state['banking_file'], threshold=0.1)