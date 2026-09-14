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

# Initialize the Error Log in session state
if 'error_log' not in st.session_state:
    st.session_state['error_log'] = pd.DataFrame(columns=['Q_Num', 'Subject', 'Error_Type'])

# --- Interactive Practice Mode ---
st.markdown("### 📝 Tactical Practice Arena")

for index, row in filtered_df.iterrows():
    st.markdown(f"**Q{row['q_num']}. {row['question']}**")
    q_key = f"q_{row['question_id']}"
    
    # 1. Statement Striker (Triggers only for multi-statement questions)
    if "Statement" in str(row['q_pattern']):
        st.caption("🛠️ **Statement Striker:**")
        eliminated = st.multiselect("Select statements you know are FALSE to cross-reference options:", 
                                    ["1", "2", "3", "4"], key=f"strike_{q_key}")
        if eliminated:
            st.info(f"💡 *Eliminated: {', '.join(eliminated)}. Any option containing these numbers is incorrect.*")

    options = [f"A) {row['opt_a']}", f"B) {row['opt_b']}", f"C) {row['opt_c']}", f"D) {row['opt_d']}"]
    user_choice = st.radio("Select your answer:", options, key=f"radio_{q_key}", index=None)
    
    if st.button("Check Answer", key=f"btn_{q_key}"):
        if user_choice:
            selected_letter = user_choice[0]
            correct_letter = str(row['final_opt']).strip()
            
            if selected_letter == correct_letter:
                st.success("✅ **Correct!**")
            else:
                st.error(f"❌ **Incorrect.** The correct answer is **{correct_letter}**.")
                
                # 2. Trap Identification (Simulated tag extraction)
                # In a full production database, add a 'trap_type' column to your Excel sheet.
                st.warning("🪤 **Trap Identified:** Fact Swap (Examiner altered specific data points).")
                
                # 3. Error Logging
                error_type = st.selectbox("Categorize this mistake for your vault:", 
                                          ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"], 
                                          key=f"log_{q_key}")
                
                if st.button("Save to Vault", key=f"save_{q_key}"):
                    new_error = pd.DataFrame({'Q_Num': [row['q_num']], 'Subject': [row['subject']], 'Error_Type': [error_type]})
                    st.session_state['error_log'] = pd.concat([st.session_state['error_log'], new_error], ignore_index=True)
                    st.success("Logged to Mistake Vault.")
                
            st.info(f"**Explanation:**\n{row['explanation']}")
    st.divider()

# --- The Mistake Vault ---
st.markdown("### 🏦 Your Mistake Vault")
if not st.session_state['error_log'].empty:
    st.dataframe(st.session_state['error_log'], use_container_width=True)
else:
    st.caption("Your vault is currently empty. Incorrect answers will populate here.")
