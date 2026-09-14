import streamlit as st
import pandas as pd
import plotly.express as px

# Set page layout
st.set_page_config(page_title="PYQ Intelligence Dashboard", layout="wide")
st.title("CAPF PYQ Intelligence Engine")

# ==========================================
# --- HELPER FUNCTIONS ---
# ==========================================
def reset_test_state():
    """Clears all test progress when filters are changed."""
    st.session_state['user_answers'] = {}
    st.session_state['checked_questions'] = set()
    st.session_state['error_tags'] = {}
    st.session_state['exam_submitted'] = False

def clean_text(text):
    """Replaces raw \n or escaped \\n with Markdown double-space line breaks for UPSC formats."""
    if pd.isna(text):
        return ""
    return str(text).replace('\\n', '  \n').replace('\n', '  \n')

# Load data automatically
@st.cache_data(ttl="10m") 
def load_data():
    return pd.read_excel('PYQ Intelligence.xlsx', sheet_name='CAPF')

df = load_data()

# ==========================================
# --- SIDEBAR FILTERS ---
# ==========================================
st.sidebar.header("Filter Data")
selected_subject = st.sidebar.multiselect(
    "Select Subject", 
    df['subject'].unique(), 
    default=df['subject'].unique(),
    on_change=reset_test_state
)
selected_difficulty = st.sidebar.multiselect(
    "Select Difficulty", 
    df['difficulty'].unique(), 
    default=df['difficulty'].unique(),
    on_change=reset_test_state
)

# Apply filters
filtered_df = df[(df['subject'].isin(selected_subject)) & (df['difficulty'].isin(selected_difficulty))]

# ==========================================
# --- TOP LEVEL METRICS & CHARTS ---
# ==========================================
col1, col2, col3 = st.columns(3)
col1.metric("Total Questions", len(filtered_df))
col2.metric("Most Tested Subject", filtered_df['subject'].mode()[0] if not filtered_df.empty else "N/A")
col3.metric("Static Concepts", len(filtered_df[filtered_df['static_current_link'] == 'Static']))

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

# Reset button for clearing session attempts cleanly
col_mode1, col_mode2 = st.columns([4, 1])
with col_mode2:
    if st.button("🔄 Reset Test / Clear Answers"):
        reset_test_state()
        st.rerun()

# ==========================================
# --- QUESTION RENDERING LOOP ---
# ==========================================
if is_exam_mode and st.session_state['exam_submitted']:
    st.markdown("### 📝 Post-Submission Review Mode")
    st.write("Review your performance below. Click on any question to expand its full explanation and log your errors.")
    
    for index, row in filtered_df.iterrows():
        qid = str(row['question_id'])
        q_num = row['q_num']
        correct_opt = str(row['final_opt']).strip()
        user_pick = st.session_state['user_answers'].get(qid, "Unattempted")
        
        # Expand questions that were answered incorrectly or left unattempted
        is_expanded = (user_pick != correct_opt)
        
        with st.expander(f"Q{q_num}. {str(row['question'])[:80]}...", expanded=is_expanded):
            cleaned_question = clean_text(row['question'])
            st.markdown(f"**Q{q_num}. {cleaned_question}**")
            
            options_dict = {
                "A": str(row['opt_a']).strip(),
                "B": str(row['opt_b']).strip(),
                "C": str(row['opt_c']).strip(),
                "D": str(row['opt_d']).strip()
            }
            
            # Color-coded option rendering
            for opt_letter, opt_text in options_dict.items():
                if opt_letter == correct_opt:
                    st.markdown(f"✅ <span style='color:green; font-weight:bold;'>{opt_letter}) {opt_text} (Correct Answer)</span>", unsafe_allow_html=True)
                elif opt_letter == user_pick and user_pick != correct_opt:
                    st.markdown(f"❌ <span style='color:red; font-weight:bold;'>{opt_letter}) {opt_text} (Your Answer)</span>", unsafe_allow_html=True)
                else:
                    st.markdown(f"{opt_letter}) {opt_text}")
            
            st.markdown("---")
            
            if user_pick == "Unattempted":
                st.warning("⚠️ **Status:** Unattempted")
            elif user_pick == correct_opt:
                st.success("🎯 **Status:** Correct")
            else:
                st.error("🚨 **Status:** Incorrect")
                st.caption("🪤 **Trap Identified:** Data / Concept Swap")
                
                # Dynamic Mistake Vault Logging
                current_tag = st.session_state['error_tags'].get(qid, "Conceptual Gap")
                selected_tag = st.selectbox(
                    "Categorize this mistake for your vault:",
                    ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                    index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_tag),
                    key=f"review_tag_{qid}"
                )
                st.session_state['error_tags'][qid] = selected_tag
                
            cleaned_explanation = clean_text(row['explanation'])
            st.info(f"**Explanation:**\n{cleaned_explanation}")
            st.caption(f"**Source:** {row.get('source', 'N/A')}")

else:
    # --- Standard Testing Loop (Instant Feedback or Pre-Submission Mock) ---
    for index, row in filtered_df.iterrows():
        qid = str(row['question_id'])
        q_num = row['q_num']
        correct_opt = str(row['final_opt']).strip()

        cleaned_question = clean_text(row['question'])
        st.markdown(f"**Q{q_num}. {cleaned_question}**")

        # Statement Striker (for multi-statement questions)
        if "Statement" in str(row.get('q_pattern', '')):
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

        saved_choice = st.session_state['user_answers'].get(qid, None)
        saved_index = next((idx for idx, opt in enumerate(options) if saved_choice and opt.startswith(saved_choice)), None)

        selected_choice = st.radio(
            "Select Option:",
            options,
            index=saved_index,
            key=f"radio_{qid}"
        )

        if selected_choice:
            st.session_state['user_answers'][qid] = selected_choice[0]

        # Mode 1: Instant Feedback Mechanics
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

                    current_tag = st.session_state['error_tags'].get(qid, "Conceptual Gap")
                    selected_tag = st.selectbox(
                        "Categorize this mistake for Individual Analysis:",
                        ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                        index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_tag),
                        key=f"tag_{qid}"
                    )
                    st.session_state['error_tags'][qid] = selected_tag

                cleaned_explanation = clean_text(row['explanation'])
                st.info(f"**Explanation:**\n{cleaned_explanation}")
                st.caption(f"**Source:** {row.get('source', 'N/A')}")

        st.divider()

# --- Mode 2: Submit Button for Exam Mode ---
if is_exam_mode and not st.session_state['exam_submitted']:
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
            'User_Choice': user_pick,
            'Correct_Choice': correct_opt,
            'Status': status,
            'Error_Type': st.session_state['error_tags'].get(qid, "Uncategorized" if status == "Incorrect" else "N/A"),
        })

    analysis_df = pd.DataFrame(records)

    total_questions = len(analysis_df)
    attempted = len(analysis_df[analysis_df['Status'] != "Unattempted"])
    correct = len(analysis_df[analysis_df['Status'] == "Correct"])
    incorrect = len(analysis_df[analysis_df['Status'] == "Incorrect"])
    unattempted = total_questions - attempted

    net_score = (correct * 2.0) - (incorrect * 0.667)
    max_score = total_questions * 2.0
    accuracy = (correct / attempted * 100) if attempted > 0 else 0

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Net Score", f"{net_score:.2f} / {max_score:.0f}")
    m2.metric("Accuracy", f"{accuracy:.1f}%")
    m3.metric("Correct (+2.0)", correct)
    m4.metric("Incorrect (-0.67)", incorrect)
    m5.metric("Unattempted", unattempted)

    st.markdown("### 📌 Subject-Wise Precision")
    if attempted > 0:
        subj_summary = analysis_df[analysis_df['Status'] != "Unattempted"].groupby('Subject').agg(
            Total_Attempted=('Status', 'count'),
            Correct=('Status', lambda x: (x == 'Correct').sum()),
            Incorrect=('Status', lambda x: (x == 'Incorrect').sum())
        )
        subj_summary['Accuracy %'] = (subj_summary['Correct'] / subj_summary['Total_Attempted'] * 100).round(1)
        st.dataframe(subj_summary, use_container_width=True)
    else:
        st.info("No questions attempted yet.")

    st.markdown("### 🏦 The Mistake Vault")
    mistakes_df = analysis_df[analysis_df['Status'] == "Incorrect"]

    if not mistakes_df.empty:
        st.dataframe(
            mistakes_df[['Q_Num', 'Subject', 'Topic', 'User_Choice', 'Correct_Choice', 'Error_Type']],
            use_container_width=True
        )
    else:
        st.success("🎯 No errors recorded in this test set!")

    # --- Strategic Roadmap ---
    st.markdown("### 🗺️ Data-Driven Preparation Roadmap")

    roadmap_points = []

    if attempted > 0 and accuracy < 60:
        roadmap_points.append("⚠️ **Elimination Discipline:** Your overall accuracy is below 60%. Restrict speculative guessing and commit only when you can eliminate at least two options.")

    if 'subj_summary' in locals() and not subj_summary.empty:
        weak_subjects = subj_summary[subj_summary['Accuracy %'] < 60].index.tolist()
        if weak_subjects:
            roadmap_points.append(f"📚 **Priority Syllabus Revision:** Focus targeted revision sprints on **{', '.join(weak_subjects)}**, where your accuracy dipped below the 60% threshold.")

    if not mistakes_df.empty:
        error_counts = mistakes_df['Error_Type'].value_counts()
        if not error_counts.empty:
            top_error = error_counts.idxmax()
            
            if top_error == "Conceptual Gap":
                roadmap_points.append("🧠 **Theory Re-anchoring:** 'Conceptual Gap' is your most frequent error. Step back from mock testing and re-read core NCERT chapters or standard reference books for these topics.")
            elif top_error == "Factual Recall Failure":
                roadmap_points.append("📝 **Active Recall Drill:** High 'Factual Recall Failure' detected. Implement concise one-page cheat sheets for dates, constitutional articles, and nodal ministries.")
            elif top_error == "Silly Mistake / Misread":
                roadmap_points.append("🔍 **Question Decoupling:** You are dropping marks to misreading. Circle or highlight keywords like 'NOT', 'INCORRECT', and statement counts before committing to a choice.")

    if not roadmap_points:
        roadmap_points.append("🔥 **Maintain Consistency:** Excellent performance! You have strong accuracy and no dominant weak points in this set. Continue timed mixed-subject drills to build speed.")

    for pt in roadmap_points:
        st.markdown(f"- {pt}")
