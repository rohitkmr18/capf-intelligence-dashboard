import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout
st.set_page_config(page_title="PYQ Intelligence Dashboard", layout="wide")
st.title("CAPF PYQ Intelligence Engine")

# Load data automatically (clears cache if file is updated)
@st.cache_data(ttl="10m") # Checks for updates every 10 mins, or remove cache for instant local reload
def load_data():
    return pd.read_excel('PYQ Intelligence.xlsx', sheet_name='CAPF')

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("Filter Data")
selected_subject = st.sidebar.multiselect("Select Subject", df['subject'].unique(), default=df['subject'].unique())
selected_difficulty = st.sidebar.multiselect("Select Difficulty", df['difficulty'].unique(), default=df['difficulty'].unique())

# Apply filters
filtered_df = df[(df['subject'].isin(selected_subject)) & (df['difficulty'].isin(selected_difficulty))]

# --- Top Level Metrics ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Questions", len(filtered_df))
col2.metric("Most Tested Subject", filtered_df['subject'].mode()[0] if not filtered_df.empty else "N/A")
col3.metric("Static Concepts", len(filtered_df[filtered_df['static_current_link'] == 'Static']))

# --- Visualizations ---
st.markdown("### Subject Weightage")
fig_sub = px.bar(filtered_df['subject'].value_counts().reset_index(), 
                 x='subject', y='count', 
                 labels={'subject': 'Subject', 'count': 'Number of Questions'},
                 color='subject')
st.plotly_chart(fig_sub, use_container_width=True)

col4, col5 = st.columns(2)

with col4:
    st.markdown("### Question Patterns")
    fig_pattern = px.pie(filtered_df, names='q_pattern', hole=0.4)
    st.plotly_chart(fig_pattern, use_container_width=True)

with col5:
    st.markdown("### Difficulty Distribution")
    fig_diff = px.pie(filtered_df, names='difficulty', color='difficulty',
                      color_discrete_map={'Easy':'#00cc96', 'Moderate':'#636efa', 'Hard':'#ef553b'})
    st.plotly_chart(fig_diff, use_container_width=True)

# --- Raw Data Explorer ---
st.markdown("### Question Database")
st.dataframe(filtered_df[['q_num', 'subject', 'theme', 'question', 'difficulty', 'q_pattern']])