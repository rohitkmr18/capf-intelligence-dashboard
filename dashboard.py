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

# ==========================================
# --- SESSION STATE INITIALIZATION ---
# ==========================================
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'checked_questions' not in st.session_state:
    st.session_state['checked_questions'] = set()
if 'error_tags' not in st.session_state:
    st.session_state['error_tags'] = {}
if 'exam_submitted' not in st.session_state:
    st.session_state['exam_submitted'] = False

# ==========================================
# --- TEST MODE SELECTION ---
# ==========================================
st.markdown("---")
st.markdown("## 🎯 Test & Practice Arena")

mode = st.radio(
    "Select your preferred testing mode before beginning:",
    ["Instant Feedback Mode (Practice one by one)", "Full Mock Exam Mode (Submit all at the end)"],
    index=0,
    horizontal=True
)

is_exam_mode = "Full Mock Exam" in mode

# Reset button for clearing session attempts
col_mode1, col_mode2 = st.columns([4, 1])
with col_mode2:
    if st.button("🔄 Reset Test / Answers"):
        st.session_state['user_answers'] = {}
        st.session_state['checked_questions'] = set()
        st.session_state['error_tags'] = {}
        st.session_state['exam_submitted'] = False
        st.rerun()

# ==========================================
# --- QUESTION RENDERING LOOP ---
# ==========================================
for index, row in filtered_df.iterrows():
    qid = str(row['question_id'])
    q_num = row['q_num']
    correct_opt = str(row['final_opt']).strip()

    st.markdown(f"**Q{q_num}. {row['question']}**")

    # Statement Striker (for multi-statement questions)
    if "Statement" in str(row['q_pattern']):
        eliminated = st.multiselect(
            "🛠️ Statement Striker (Eliminate false statements):",
            ["1", "2", "3", "4"],
            key=f"strike_{qid}"
        )
        if eliminated:
            st.caption(f"💡 *Eliminated: Statement(s) {', '.join(eliminated)}. Discard options containing them.*")

    options = [
        f"A) {row['opt_a']}",
        f"B) {row['opt_b']}",
        f"C) {row['opt_c']}",
        f"D) {row['opt_d']}"
    ]

    # Pre-select previous choice if available
    saved_choice = st.session_state['user_answers'].get(qid, None)
    saved_index = None
    if saved_choice:
        for idx, opt in enumerate(options):
            if opt.startswith(saved_choice):
                saved_index = idx

    selected_choice = st.radio(
        "Select Option:",
        options,
        index=saved_index,
        key=f"radio_{qid}"
    )

    if selected_choice:
        st.session_state['user_answers'][qid] = selected_choice[0]

    # --- Mode 1: Instant Feedback Mechanics ---
    if not is_exam_mode:
        col_btn, _ = st.columns([2, 5])
        with col_btn:
            if st.button(f"Check Answer", key=f"btn_check_{qid}"):
                if qid in st.session_state['user_answers']:
                    st.session_state['checked_questions'].add(qid)
                else:
                    st.warning("Select an option first.")

        if qid in st.session_state['checked_questions']:
            user_pick = st.session_state['user_answers'].get(qid)
            if user_pick == correct_opt:
                st.success(f"✅ **Correct!** (Answer: {correct_opt})")
            else:
                st.error(f"❌ **Incorrect.** Correct Answer is **{correct_opt}**")
                st.warning("🪤 **Trap Identified:** Data / Concept Swap")

                # Error categorization dropdown
                current_tag = st.session_state['error_tags'].get(qid, "Conceptual Gap")
                selected_tag = st.selectbox(
                    "Categorize this mistake for Individual Analysis:",
                    ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                    index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_tag),
                    key=f"tag_{qid}"
                )
                st.session_state['error_tags'][qid] = selected_tag

            st.info(f"**Explanation:**\n{row['explanation']}")
            st.caption(f"**Source:** {row['source']}")

    st.divider()

# --- Mode 2: Submit Button for Exam Mode ---
if is_exam_mode:
    if st.button("🚀 Submit Mock Test & Generate Analysis", type="primary"):
        st.session_state['exam_submitted'] = True
        st.rerun()

# ==========================================
# --- INDIVIDUAL ANALYSIS ENGINE ---
# ==========================================
should_show_analysis = (is_exam_mode and st.session_state['exam_submitted']) or \
                       (not is_exam_mode and len(st.session_state['checked_questions']) > 0)

if should_show_analysis:
    st.markdown("## 📊 Individual Analysis & Performance Audit")

    # Evaluate responses
    records = []
    eval_set = filtered_df if is_exam_mode else filtered_df[filtered_df['question_id'].astype(str).isin(st.session_state['checked_questions'])]

    for _, row in eval_set.iterrows():
        qid = str(row['question_id'])
        user_pick = st.session_state['user_answers'].get(qid, "Unattempted")
        correct_opt = str(row['final_opt']).strip()

        if user_pick == "Unattempted":
            status = "Unattempted"
        elif user_pick == correct_opt:
            status = "Correct"
        else:
            status = "Incorrect"

        records.append({
            'Q_Num': row['q_num'],
            'Subject': row['subject'],
            'Topic': row['topic'],
            'Static_Current': row['static_current_link'],
            'User_Choice': user_pick,
            'Correct_Choice': correct_opt,
            'Status': status,
            'Error_Type': st.session_state['error_tags'].get(qid, "Uncategorized" if status == "Incorrect" else "N/A"),
            'Explanation': row['explanation']
        })

    analysis_df = pd.DataFrame(records)

    # Core Metrics
    total_questions = len(analysis_df)
    attempted = len(analysis_df[analysis_df['Status'] != "Unattempted"])
    correct = len(analysis_df[analysis_df['Status'] == "Correct"])
    incorrect = len(analysis_df[analysis_df['Status'] == "Incorrect"])
    unattempted = total_questions - attempted

    # UPSC Marking Scheme: +2.0 for correct, -0.667 for incorrect
    net_score = (correct * 2.0) - (incorrect * 0.667)
    max_score = total_questions * 2.0
    accuracy = (correct / attempted * 100) if attempted > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Net Score", f"{net_score:.2f} / {max_score:.0f}")
    m2.metric("Accuracy", f"{accuracy:.1f}%")
    m3.metric("Correct (+2.0)", correct)
    m4.metric("Incorrect (-0.67)", incorrect)
    m5.metric("Unattempted", unattempted)

    # --- Subject-wise Breakdown ---
    st.markdown("### 📌 Subject-Wise Precision")
    subj_summary = analysis_df[analysis_df['Status'] != "Unattempted"].groupby('Subject').agg(
        Total_Attempted=('Status', 'count'),
        Correct=('Status', lambda x: (x == 'Correct').sum()),
        Incorrect=('Status', lambda x: (x == 'Incorrect').sum())
    )
    if not subj_summary.empty:
        subj_summary['Accuracy %'] = (subj_summary['Correct'] / subj_summary['Total_Attempted'] * 100).round(1)
        st.dataframe(subj_summary, use_container_width=True)

    # --- Mistake Vault Table ---
    st.markdown("### 🏦 The Mistake Vault")
    mistakes_df = analysis_df[analysis_df['Status'] == "Incorrect"]

    if not mistakes_df.empty:
        st.dataframe(
            mistakes_df[['Q_Num', 'Subject', 'Topic', 'User_Choice', 'Correct_Choice', 'Error_Type']],
            use_container_width=True
        )

        # In Exam Mode: Allow post-exam categorization
        if is_exam_mode:
            st.caption("Categorize your errors below to sharpen the roadmap recommendations:")
            for _, m_row in mistakes_df.iterrows():
                mqid = str(filtered_df[filtered_df['q_num'] == m_row['Q_Num']]['question_id'].values[0])
                c1, c2 = st.columns([3, 2])
                with c1:
                    st.write(f"**Q{m_row['Q_Num']} ({m_row['Subject']}):** {m_row['Topic']}")
                with c2:
                    current_et = st.session_state['error_tags'].get(mqid, "Conceptual Gap")
                    new_et = st.selectbox(
                        f"Error reason Q{m_row['Q_Num']}",
                        ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                        index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_et),
                        key=f"post_tag_{mqid}",
                        label_visibility="collapsed"
                    )
                    st.session_state['error_tags'][mqid] = new_et
    else:
        st.success("🎯 No errors recorded in this test set!")

    # --- Strategic Roadmap ---
    st.markdown("### 🗺️ Data-Driven Preparation Roadmap")

    roadmap_points = []

    # Accuracy logic
    if accuracy < 60 and attempted > 0:
        roadmap_points.append(
            "⚠️ **Elimination Discipline:** Your accuracy is below 60%. Restrict 50-50 speculative guesses and only commit when you can eliminate at least two options."
        )

    # Subject-specific weaknesses
    if not subj_summary.empty:
        weakest_subjects = subj_summary[subj_summary['Accuracy %'] < 60].index.tolist()
        if weakest_subjects:
            roadmap_points.append(
                f"📚 **Priority Syllabus Revision:** Focus revision sprints on **{', '.join(weakest_subjects)}**, where your accuracy dipped below the 60% threshold."
            )

    # Error type patterns
    error_counts = analysis_df['Error_Type'].value_counts()
    if 'Conceptual Gap' in error_counts and error_counts['Conceptual Gap'] >= 2:
        roadmap_points.append(
            "🧠 **Theory Re-anchoring:** You have multiple 'Conceptual Gap' tags. Step back from mock testing for these topics and re-read core NCERT chapters before practicing more questions."
        )
    if 'Factual Recall Failure' in error_counts and error_counts['Factual Recall Failure'] >= 2:
        roadmap_points.append(
            "📝 **Active Recall Drill:** High factual recall errors detected. Implement concise one-page cheat sheets for dates, constitutional articles, and scheme nodal ministries."
        )
    if 'Silly Mistake / Misread' in error_counts and error_counts['Silly Mistake / Misread'] >= 1:
        roadmap_points.append(
            "🔍 **Question Decoupling:** You are dropping marks to question misreading. Circle or highlight keywords like 'NOT correct', 'INCORRECT', and statement counts before marking choices."
        )

    if not roadmap_points:
        roadmap_points.append(
            "🔥 **Maintain Consistency:** High accuracy across all attempted sections. Continue mixed-subject timed drill sets to build speed."
        )

    for pt in roadmap_points:
        st.markdown(f"- {pt}")
