import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# --- PAGE CONFIG & CSS INJECTION ---
# ==========================================
st.set_page_config(page_title="Defence Pathshala | PYQ Engine", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
<style>
/* Base Typography & Negative Space */
html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.block-container {
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Banner Design */
.hero-banner {
    background: linear-gradient(135deg, #0F172A 0%, #1E3A8A 100%);
    padding: 30px 20px;
    border-radius: 12px;
    text-align: center;
    color: white;
    margin-bottom: 15px;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.hero-title {
    font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', sans-serif;
    font-weight: 900;
    font-size: 2.2rem;
    margin-bottom: 0px;
    line-height: 1.1;
    color: #FFFFFF;
}
.hero-tagline {
    font-size: 1.05rem;
    color: #93C5FD;
    margin-top: 5px;
    font-weight: 500;
    letter-spacing: 0.5px;
}

/* Credential Badge */
.cred-badge {
    background-color: #F8FAFC;
    border-left: 5px solid #F59E0B;
    padding: 14px;
    border-radius: 6px;
    font-size: 0.95rem;
    text-align: center;
    margin: 20px auto;
    font-weight: 700;
    color: #0F172A;
    box-shadow: 0 2px 4px rgba(0,0,0,0.02);
}

/* Dashboard Description */
.dash-intro {
    text-align: center;
    font-size: 0.95rem;
    color: #475569;
    line-height: 1.6;
    margin-bottom: 30px;
    padding: 0 10px;
}

/* Mobile-Optimized Radio Buttons */
div.stRadio > div[role="radiogroup"] > label {
    padding: 14px 18px !important;
    margin-bottom: 10px !important;
    background-color: #F8FAFC;
    border-radius: 8px;
    border: 1px solid #E2E8F0;
    cursor: pointer;
    transition: all 0.2s ease;
}
div.stRadio > div[role="radiogroup"] > label:hover {
    border-color: #3B82F6;
    background-color: #EFF6FF;
}

/* Metric Typography Override */
[data-testid="stMetricValue"] {
    font-family: 'Comic Sans MS', 'Chalkboard SE', 'Marker Felt', sans-serif !important;
    color: #1E3A8A;
}
</style>
""", unsafe_allow_html=True)

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

@st.cache_data(ttl="10m") 
def load_data():
    return pd.read_excel('PYQ Intelligence.xlsx', sheet_name='CAPF')

df = load_data()

# ==========================================
# --- HERO SECTION ---
# ==========================================
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">DEFENCE PATHSHALA</div>
    <div class="hero-tagline">PYQ Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="cred-badge">Engineered by an IIT Kanpur graduate, UPSC CAPF AC AIR 163 and 4-time CDS qualifier.</div>', unsafe_allow_html=True)

st.markdown('<div class="dash-intro">Transform raw PYQs into a tactical, data-driven preparation engine. Stop passive reading and start actively eliminating. This intelligence dashboard analyzes your performance patterns, isolates specific examiner traps, and dynamically builds a personalized syllabus roadmap to maximize your final score.</div>', unsafe_allow_html=True)

# ==========================================
# --- GLOBAL DATABASE OVERVIEW ---
# ==========================================
st.markdown("### 📊 Database Overview")

# 1. Global Metrics
col1, col2 = st.columns(2)
col1.metric("Total Questions", len(df))

if 'exam' in df.columns and 'year' in df.columns:
    unique_exams = df[['exam', 'year']].drop_duplicates()
    exam_label = ", ".join([f"{row['exam']} {row['year']}" for _, row in unique_exams.iterrows()])
else:
    exam_label = "UPSC CAPF-AC 2025"
col2.metric("Available Exams", exam_label)

# 2. Global Charts (Mobile-Scroll Locked)
c1, c2 = st.columns(2)

with c1:
    fig_sub = px.pie(df, names='subject', hole=0.5, title="Subject Weightage")
    fig_sub.update_layout(dragmode=False, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
    fig_sub.update_xaxes(fixedrange=True)
    fig_sub.update_yaxes(fixedrange=True)
    fig_sub.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig_sub, use_container_width=True, key="global_subject_chart")

with c2:
    fig_pattern = px.bar(df['q_pattern'].value_counts().reset_index(), 
                         x='count', y='q_pattern', 
                         orientation='h', 
                         title="Question Structures", 
                         color='q_pattern')
    fig_pattern.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, dragmode=False)
    fig_pattern.update_xaxes(showgrid=False, fixedrange=True, visible=False)
    fig_pattern.update_yaxes(fixedrange=True, categoryorder='total ascending')
    st.plotly_chart(fig_pattern, use_container_width=True, key="global_pattern_chart")

st.markdown("---")

# ==========================================
# --- CENTRALIZED FILTERS & EXAM TOGGLE ---
# ==========================================
with st.expander("⚙️ Configure Mocks", expanded=True):
    full_paper = st.checkbox("⏱️ Attempt Full Paper (125 Questions - 2 Hours)", on_change=reset_test_state)
    
    if not full_paper:
        selected_subject = st.multiselect(
            "Select Subject", 
            df['subject'].unique(), 
            default=[], 
            on_change=reset_test_state
        )
        selected_difficulty = st.multiselect(
            "Select Difficulty", 
            df['difficulty'].unique(), 
            default=[], 
            on_change=reset_test_state
        )
        
        filtered_df = df[(df['subject'].isin(selected_subject)) & (df['difficulty'].isin(selected_difficulty))]
        
        st.markdown("---")
        mode = st.radio(
            "Testing Mode:",
            ["Instant Feedback (Practice one by one)", "Full Mock Exam (Submit all at the end)"],
            index=0
        )
        is_exam_mode = "Full Mock Exam" in mode
    else:
        filtered_df = df
        st.warning("⏱️ **Timed Mock Activated (2 Hours).** The interface is locked to Full Mock Exam mode. Submit at the end to view your scorecard and personalized report.")
        is_exam_mode = True

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
# --- MAIN CONTENT RENDER (TEST ARENA) ---
# ==========================================
if filtered_df.empty:
    st.info("👆 Select subjects and difficulty levels in the configuration menu above to generate your custom practice set of PYQ.")
else:
    # --- TOP LEVEL METRICS (Filtered Set) ---
    col1, col2 = st.columns(2)
    col1.metric("Total Questions", len(filtered_df))
    
    exam_label = f"{filtered_df['exam'].iloc[0]} {filtered_df['year'].iloc[0]}" if 'exam' in filtered_df.columns and 'year' in filtered_df.columns else "N/A"
    col2.metric("Target Exam", exam_label)
    
    st.markdown("---")
    
    # --- MOBILE OPTIMIZED CHARTS (Filtered Set) ---
    c1, c2 = st.columns(2)
    with c1:
        fig_sub = px.pie(filtered_df, names='subject', hole=0.5, title="Subject Weightage")
        fig_sub.update_layout(dragmode=False, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
        fig_sub.update_xaxes(fixedrange=True)
        fig_sub.update_yaxes(fixedrange=True)
        fig_sub.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig_sub, use_container_width=True, key="filtered_subject_chart")

    with c2:
        fig_pattern = px.bar(filtered_df['q_pattern'].value_counts().reset_index(), 
                             x='count', y='q_pattern', 
                             orientation='h', 
                             title="Question Structures", 
                             color='q_pattern')
        fig_pattern.update_layout(plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)', showlegend=False, dragmode=False)
        fig_pattern.update_xaxes(showgrid=False, fixedrange=True, visible=False)
        fig_pattern.update_yaxes(fixedrange=True, categoryorder='total ascending')
        st.plotly_chart(fig_pattern, use_container_width=True, key="filtered_pattern_chart")

    st.markdown("## 🎯 Test Arena")

    if st.button("🔄 Reset Test / Clear Answers", use_container_width=True):
        reset_test_state()
        st.rerun()

    st.markdown("---")

    # ==========================================
    # --- QUESTION RENDERING LOOP ---
    # ==========================================
    if is_exam_mode and st.session_state['exam_submitted']:
        st.markdown("### 📝 Post-Submission Review")
        st.write("Click on any question to expand explanations and log your errors.")
        
        for index, row in filtered_df.iterrows():
            qid = str(row['question_id'])
            q_num = row['q_num']
            correct_opt = str(row['final_opt']).strip()
            user_pick = st.session_state['user_answers'].get(qid, "Unattempted")
            
            is_expanded = (user_pick != correct_opt)
            
            with st.expander(f"Q{q_num}. {str(row['question'])[:60]}...", expanded=is_expanded):
                cleaned_question = clean_text(row['question'])
                st.markdown(f"**Q{q_num}. {cleaned_question}**")
                
                options_dict = {
                    "A": str(row['opt_a']).strip(),
                    "B": str(row['opt_b']).strip(),
                    "C": str(row['opt_c']).strip(),
                    "D": str(row['opt_d']).strip()
                }
                
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
                    
                    current_tag = st.session_state['error_tags'].get(qid, "Conceptual Gap")
                    selected_tag = st.selectbox(
                        "Categorize this mistake:",
                        ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                        index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_tag),
                        key=f"review_tag_{qid}"
                    )
                    st.session_state['error_tags'][qid] = selected_tag
                    
                cleaned_explanation = clean_text(row['explanation'])
                st.info(f"**Explanation:**\n{cleaned_explanation}")
                st.caption(f"**Source:** {row.get('source', 'N/A')}")

    else:
        for index, row in filtered_df.iterrows():
            qid = str(row['question_id'])
            q_num = row['q_num']
            correct_opt = str(row['final_opt']).strip()

            cleaned_question = clean_text(row['question'])
            st.markdown(f"**Q{q_num}. {cleaned_question}**")

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
                key=f"radio_{qid}",
                label_visibility="collapsed"
            )

            if selected_choice:
                st.session_state['user_answers'][qid] = selected_choice[0]

            if not is_exam_mode:
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

                        current_tag = st.session_state['error_tags'].get(qid, "Conceptual Gap")
                        selected_tag = st.selectbox(
                            "Categorize this mistake:",
                            ["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"],
                            index=["Conceptual Gap", "Factual Recall Failure", "Silly Mistake / Misread"].index(current_tag),
                            key=f"tag_{qid}"
                        )
                        st.session_state['error_tags'][qid] = selected_tag

                    cleaned_explanation = clean_text(row['explanation'])
                    st.info(f"**Explanation:**\n{cleaned_explanation}")

            st.divider()

    if is_exam_mode and not st.session_state['exam_submitted']:
        if st.button("🚀 Submit Mock Test & Generate Analysis", type="primary", use_container_width=True):
            st.session_state['exam_submitted'] = True
            st.rerun()

    # ==========================================
    # --- INDIVIDUAL ANALYSIS ENGINE (TABS) ---
    # ==========================================
    should_show_analysis = (is_exam_mode and st.session_state['exam_submitted']) or \
                           (not is_exam_mode and len(st.session_state['checked_questions']) > 0)

    if should_show_analysis:
        st.markdown("## 📊 Performance Audit")

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

        tab_score, tab_subject, tab_vault, tab_roadmap = st.tabs(["Scorecard", "Subject Precision", "Mistake Vault", "Strategic Roadmap"])

        with tab_score:
            m1, m2 = st.columns(2)
            m1.metric("Net Score", f"{net_score:.2f} / {max_score:.0f}")
            m2.metric("Accuracy", f"{accuracy:.1f}%")
            m3, m4, m5 = st.columns(3)
            m3.metric("Correct", correct)
            m4.metric("Incorrect", incorrect)
            m5.metric("Blank", unattempted)

        with tab_subject:
            if attempted > 0:
                subj_summary = analysis_df[analysis_df['Status'] != "Unattempted"].groupby('Subject').agg(
                    Attempted=('Status', 'count'),
                    Correct=('Status', lambda x: (x == 'Correct').sum()),
                    Incorrect=('Status', lambda x: (x == 'Incorrect').sum())
                )
                subj_summary['Accuracy %'] = (subj_summary['Correct'] / subj_summary['Attempted'] * 100).round(1)
                st.dataframe(subj_summary, use_container_width=True)
            else:
                st.info("No questions attempted yet.")

        with tab_vault:
            mistakes_df = analysis_df[analysis_df['Status'] == "Incorrect"]
            if not mistakes_df.empty:
                st.dataframe(
                    mistakes_df[['Q_Num', 'Subject', 'Topic', 'User_Choice', 'Correct_Choice', 'Error_Type']],
                    use_container_width=True
                )
            else:
                st.success("🎯 No errors recorded in this test set!")

        with tab_roadmap:
            roadmap_points = []
            if attempted > 0 and accuracy < 60:
                roadmap_points.append("⚠️ **Elimination Discipline:** Overall accuracy below 60%. Restrict speculative guessing.")
            
            if 'subj_summary' in locals() and not subj_summary.empty:
                weak_subjects = subj_summary[subj_summary['Accuracy %'] < 60].index.tolist()
                if weak_subjects:
                    roadmap_points.append(f"📚 **Priority Revision:** Focus on **{', '.join(weak_subjects)}** (<60% accuracy).")

            if not mistakes_df.empty:
                error_counts = mistakes_df['Error_Type'].value_counts()
                if not error_counts.empty:
                    top_error = error_counts.idxmax()
                    if top_error == "Conceptual Gap":
                        roadmap_points.append("🧠 **Theory Re-anchoring:** 'Conceptual Gap' is dominant. Re-read NCERTs for these topics.")
                    elif top_error == "Factual Recall Failure":
                        roadmap_points.append("📝 **Active Recall Drill:** Build 1-page cheat sheets for dates/articles.")
                    elif top_error == "Silly Mistake / Misread":
                        roadmap_points.append("🔍 **Question Decoupling:** Highlight 'NOT' and 'INCORRECT' before answering.")

            if not roadmap_points:
                roadmap_points.append("🔥 **Maintain Consistency:** Excellent performance! Continue timed drills.")

            for pt in roadmap_points:
                st.markdown(f"- {pt}")
