import streamlit as st
import plotly.graph_objects as go
from frontend.utils import valid_user_state

valid_user_state()
st.set_page_config(layout='centered')


# Utility
@st.cache_data
def st_wrapper_pull_training_data():
    return st.session_state.backend.ml.pull_training_data()


#Training Section
st.title('Train a new Naive-Bayes Model')

# Pull the training Data and Select the date-range
df = st_wrapper_pull_training_data()
d0 = st.date_input(
    'Training Data Range Start',
    df['date'].min(),
    df['date'].min(),
    df['date'].max(),
    format='YYYY-MM-DD',
)
d1 = st.date_input(
    'Training Data Range End',
    df['date'].max(),
    df['date'].min(),
    df['date'].max(),
    format='YYYY-MM-DD',
)
df = df.loc[(df['date'] > d0) & (df['date'] < d1)]
df = df.drop('date', axis=1) # Remove the date, that is only used to select the date range

# Display the selected training data
st.subheader(f'Selected Training Data: {df.shape[0]} Rows')
st.dataframe(df, width='stretch')

# Train Valid Split
st.subheader('Training-Validation Split')
ratio = st.slider('Percentage', 0.05, 0.95, 0.90, 0.01)
df_train = df.iloc[:int(df.shape[0] * ratio)]
df_valid = df.iloc[int(df.shape[0] * ratio):]

# Fit the model automatically constantly (if json is shown, this may be slow)
st.session_state.backend.ml.train_new_model(df_train, target_col='category')

# Save the model
if st.button('Save the Model', width='stretch'):
    st.session_state.backend.ml.save_model_to_gcs()


# Results section
st.divider()
st.title('Model Results')

# Prior Prob. Distribution
priors = st.session_state.backend.ml.get_priors()
fig = go.Figure(data=[go.Bar(
    x=list(priors.keys()),
    y=list(priors.values()),
    marker_color='red',
    hovertemplate = '%{y:.2f}<extra></extra>'
)])
fig.update_layout(hovermode='x unified')
fig.update_layout(yaxis_title='Prior Prob. [%]', title='Class Prior Propabilities')
st.plotly_chart(fig, use_container_width=True)

# Accuracy Plot
st.subheader('Validation data Results')
max_error = st.number_input('Maximum Allowed Error on Placement', 0, 5, 1)
wa, stats = st.session_state.backend.ml.validate_model(df_valid, target_col='category', accepted_error=max_error)
st.subheader(f'Total Weighted Accuracy: {wa*100:.2f}%')
st.dataframe(
    stats,
    column_config={
        'y_valid': st.column_config.Column(
            'Class',
        ),
        'Events': st.column_config.Column(
            'Class',
        ),
        'place_q50': st.column_config.NumberColumn(
            'Median Place',
            format="%.2f",
        ),
        'accuracy': st.column_config.ProgressColumn(
            'Accuracy',
            format='%.2f',
            min_value=0.0,
            max_value=1.0,
        ),
    },
    width='stretch'
)

# Print all Likelihoods as JSON
if st.toggle('Show Likelihoods'):
    likes = st.session_state.backend.ml.get_likelihoods()
    st.write(likes)