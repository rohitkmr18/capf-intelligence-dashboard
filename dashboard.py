import streamlit as st
import pandas as pd
import plotly.express as px
import time
import streamlit.components.v1 as components

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

/* Briefing Card */
.briefing-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    margin-bottom: 25px;
}
.briefing-header {
    font-size: 1.3rem;
    font-weight: 800;
    color: #0F172A;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}
.briefing-item {
    margin-bottom: 12px;
    line-height: 1.6;
    color: #334155;
    font-size: 0.96rem;
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
    """Clears all test progress, timer, and pagination states."""
    st.session_state['user_answers'] = {}
    st.session_state['checked_questions'] = set()
    st.session_state['error_tags'] = {}
    st.session_state['marked_for_review'] = set()
    st.session_state['exam_submitted'] = False
    st.session_state['exam_started'] = False
    st.session_state['start_time'] = None
    st.session_state['auto_submitted'] = False
    st.session_state['current_page'] = 0

def clean_text(text):
    if pd.isna(text):
        return ""
    return str(text).replace('\\n', '  \n').replace('\n', '  \n')

# ==========================================
# --- DATA FETCHING & SESSION LOCKING ---
# ==========================================
@st.cache_data(ttl="1h") 
def fetch_google_sheet():
    # Replace the URL below with your actual Google Sheets export URL
    sheet_url = "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/export?format=csv&gid=0"
    return pd.read_csv(sheet_url)

# Lock the data to the user's browser session on their first load
if 'master_db' not in st.session_state:
    st.session_state['master_db'] = fetch_google_sheet()

# The rest of your application will use this session-locked dataframe
df = st.session_state['master_db']
# ==========================================
# --- SESSION STATE INITIALIZATION ---
# ==========================================
if 'user_answers' not in st.session_state:
    st.session_state['user_answers'] = {}
if 'checked_questions' not in st.session_state:
    st.session_state['checked_questions'] = set()
if 'error_tags' not in st.session_state:
    st.session_state['error_tags'] = {}
if 'marked_for_review' not in st.session_state:
    st.session_state['marked_for_review'] = set()
if 'exam_submitted' not in st.session_state:
    st.session_state['exam_submitted'] = False
if 'exam_started' not in st.session_state:
    st.session_state['exam_started'] = False
if 'start_time' not in st.session_state:
    st.session_state['start_time'] = None
if 'time_limit_seconds' not in st.session_state:
    st.session_state['time_limit_seconds'] = 7200
if 'auto_submitted' not in st.session_state:
    st.session_state['auto_submitted'] = False
if 'current_page' not in st.session_state:
    st.session_state['current_page'] = 0
if 'is_full_paper' not in st.session_state:
    st.session_state['is_full_paper'] = False

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
# --- EXAM & CYCLE SELECTION (NEW COMPONENT) ---
# ==========================================
if not st.session_state['is_full_paper']:
    st.markdown("### 🎯 Select Examination & Cycle")
    
    # 1. Target Exam Dropdown
    if 'exam' in df.columns:
        exam_options = list(df['exam'].dropna().unique())
    else:
        exam_options = ["CAPF-AC", "CDS"] # Fallback

    selected_exam = st.selectbox(
        "Target Exam:",
        options=exam_options,
        key="exam_selection",
        on_change=reset_test_state
    )

    # 2. Year/Cycle Dropdown (Dynamically filtered based on Exam)
    if 'exam' in df.columns and 'year' in df.columns:
        # Filter the years available for the chosen exam from the dataset
        available_years = list(df[df['exam'] == selected_exam]['year'].dropna().unique())
    else:
        # Fallback if columns are missing
        available_years = ["2025"] if selected_exam == "CAPF-AC" else ["September 2026"]

    selected_year = st.selectbox(
        "Exam Year/Cycle:",
        options=available_years,
        key="year_selection",
        on_change=reset_test_state
    )

else:
    # Retain selected state when full paper mode hides the selectors
    selected_exam = st.session_state.get('exam_selection', "CAPF-AC")
    selected_year = st.session_state.get('year_selection', "2025")

# Filter the master dataframe to match BOTH the selected exam and year
if 'exam' in df.columns and 'year' in df.columns:
    exam_df = df[(df['exam'] == selected_exam) & (df['year'] == selected_year)]
else:
    exam_df = df

st.markdown("---")
# ==========================================
# --- GLOBAL DATABASE OVERVIEW ---
# ==========================================
if not st.session_state['is_full_paper']:
    st.markdown(f"### 📊 Database Overview: {selected_exam} {selected_year}")
    col1, col2 = st.columns(2)
    # Using exam_df to reflect only the selected exam's metrics
    col1.metric("Total Questions", len(exam_df))
    col2.metric("Active Dataset", f"{selected_exam} {selected_year}")

    c1, c2, c3 = st.columns(3)
    chart_config = {'displayModeBar': False}

    with c1:
        if 'subject' in exam_df.columns and not exam_df.empty:
            fig_sub = px.pie(exam_df, names='subject', hole=0.5, title="Subject Weightage")
            fig_sub.update_traces(textposition='inside', textinfo='label+value', hovertemplate="%{label}: %{value} Questions<extra></extra>")
            fig_sub.update_layout(dragmode=False, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            fig_sub.update_xaxes(fixedrange=True)
            fig_sub.update_yaxes(fixedrange=True)
            st.plotly_chart(fig_sub, use_container_width=True, config=chart_config, key="global_subject_chart")

    with c2:
        if 'q_pattern' in exam_df.columns and not exam_df.empty:
            fig_pattern = px.pie(exam_df, names='q_pattern', hole=0.5, title="Question Structures")
            fig_pattern.update_traces(textposition='inside', textinfo='label+value', hovertemplate="%{label}: %{value} Questions<extra></extra>")
            fig_pattern.update_layout(dragmode=False, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            fig_pattern.update_xaxes(fixedrange=True)
            fig_pattern.update_yaxes(fixedrange=True)
            st.plotly_chart(fig_pattern, use_container_width=True, config=chart_config, key="global_pattern_chart")

    with c3:
        if 'difficulty' in exam_df.columns and not exam_df.empty:
            fig_diff = px.pie(exam_df, names='difficulty', hole=0.5, title="Difficulty Level")
            fig_diff.update_traces(textposition='inside', textinfo='label+value', hovertemplate="%{label}: %{value} Questions<extra></extra>")
            fig_diff.update_layout(dragmode=False, showlegend=False, margin=dict(t=30, b=10, l=10, r=10))
            fig_diff.update_xaxes(fixedrange=True)
            fig_diff.update_yaxes(fixedrange=True)
            st.plotly_chart(fig_diff, use_container_width=True, config=chart_config, key="global_difficulty_chart")

    st.markdown("---")

# ==========================================
# --- CENTRALIZED FILTERS & EXAM TOGGLE ---
# ==========================================
with st.expander("⚙️ Configure Mocks", expanded=True):
    full_paper = st.checkbox("⏱️ Attempt Full Paper (125 Questions - 2 Hours)", key="is_full_paper", on_change=reset_test_state)
    
    if not full_paper:
        # Populate multiselect options directly from the exam_df
        selected_subject = st.multiselect(
            "Select Subject", 
            exam_df['subject'].unique() if 'subject' in exam_df.columns else [], 
            default=[], 
            on_change=reset_test_state
        )
        selected_difficulty = st.multiselect(
            "Select Difficulty", 
            exam_df['difficulty'].unique() if 'difficulty' in exam_df.columns else [], 
            default=[], 
            on_change=reset_test_state
        )
        
        # Apply filters to exam_df safely
        if 'subject' in exam_df.columns and 'difficulty' in exam_df.columns:
            filtered_df = exam_df[(exam_df['subject'].isin(selected_subject)) & (exam_df['difficulty'].isin(selected_difficulty))]
        else:
            filtered_df = exam_df
        
        st.markdown("---")
        mode = st.radio(
            "Testing Mode:",
            ["Instant Feedback (Practice one by one)", "Full Mock Exam (Submit all at the end)"],
            index=0
        )
        is_exam_mode = "Full Mock Exam" in mode
    else:
        filtered_df = exam_df # Locks to the selected exam's full paper
        st.warning("⏱️ **Timed Mock Activated (2 Hours).** The interface is locked to Full Mock Exam mode.")
        is_exam_mode = True

# ==========================================
# --- MAIN CONTENT RENDER (TEST ARENA) ---
# ==========================================
if filtered_df.empty:
    st.info("👆 Select subjects and difficulty levels in the configuration menu above to generate your custom practice set of PYQ.")
else:
    st.markdown("## 🎯 Test Arena")

    # ==========================================
    # --- GATEKEEPER / PRE-EXAM BRIEFING ---
    # ==========================================
    if full_paper and not st.session_state['exam_started']:
        st.markdown("""
        <div class="briefing-card">
            <div class="briefing-header">📋 Examination Guidelines & Protocol</div>
            <div class="briefing-item">• <strong>Exam Pattern:</strong> 125 Questions | 250 Total Marks | 2 Hours (120 Minutes).</div>
            <div class="briefing-item">• <strong>Marking Scheme:</strong> <strong>+2.0</strong> for correct answers, <strong>-0.67</strong> negative marking penalty for incorrect attempts, and <strong>0</strong> for unattempted questions.</div>
            <div class="briefing-item">• <strong>Attempt Strategy:</strong> Execute a structured 3-Round elimination cycle:
                <br>&emsp;↳ <em>Round 1:</em> Secure 100% direct-hit questions.
                <br>&emsp;↳ <em>Round 2:</em> Solve 50-50 elimination questions.
                <br>&emsp;↳ <em>Round 3:</em> Execute strictly calculated risks to hit target cutoff.
            </div>
            <div class="briefing-item">• <strong>Timer Rules:</strong> The countdown clock runs continuously once initiated. Responses auto-lock upon timer expiration.</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Let's Start Test", type="primary", use_container_width=True):
            st.session_state['exam_started'] = True
            st.session_state['start_time'] = time.time()
            st.rerun()

    else:
        # ==========================================
        # --- JS FLOATING TIMER INJECTION ---
        # ==========================================
        if full_paper and st.session_state['exam_started']:
            if not st.session_state['exam_submitted']:
                elapsed_time = int(time.time() - st.session_state['start_time'])
                remaining_time = max(0, st.session_state['time_limit_seconds'] - elapsed_time)
                
                if remaining_time <= 0:
                    st.session_state['exam_submitted'] = True
                    st.session_state['auto_submitted'] = True
                    st.rerun()
                
                timer_js = f"""
                <script>
                    var parentDoc = window.parent.document;
                    var timerDiv = parentDoc.getElementById('floating-timer');
                    if (!timerDiv) {{
                        timerDiv = parentDoc.createElement('div');
                        timerDiv.id = 'floating-timer';
                        timerDiv.style.position = 'fixed';
                        timerDiv.style.top = '70px';
                        timerDiv.style.right = '30px';
                        timerDiv.style.zIndex = '999999';
                        timerDiv.style.background = 'rgba(255, 255, 255, 0.95)';
                        timerDiv.style.padding = '12px 20px';
                        timerDiv.style.border = '2px solid #3B82F6';
                        timerDiv.style.borderRadius = '8px';
                        timerDiv.style.fontWeight = 'bold';
                        timerDiv.style.boxShadow = '0 4px 10px rgba(0,0,0,0.15)';
                        timerDiv.style.color = '#1E3A8A';
                        timerDiv.style.fontFamily = 'monospace';
                        timerDiv.style.fontSize = '1.2rem';
                        parentDoc.body.appendChild(timerDiv);
                    }}
                    
                    var remaining = {remaining_time};
                    if (window.timerInterval) clearInterval(window.timerInterval);
                    
                    window.timerInterval = setInterval(function() {{
                        if (remaining <= 0) {{
                            clearInterval(window.timerInterval);
                            timerDiv.innerHTML = "⏰ Time Expired!";
                            timerDiv.style.color = "#991B1B";
                            timerDiv.style.borderColor = "#FCA5A5";
                            timerDiv.style.backgroundColor = "#FEF2F2";
                        }} else {{
                            remaining--;
                            var h = Math.floor(remaining / 3600);
                            var m = Math.floor((remaining % 3600) / 60);
                            var s = remaining % 60;
                            var hStr = (h < 10 ? "0"+h : h);
                            var mStr = (m < 10 ? "0"+m : m);
                            var sStr = (s < 10 ? "0"+s : s);
                            timerDiv.innerHTML = "⏳ " + hStr + ":" + mStr + ":" + sStr;
                            
                            if (remaining < 900) {{
                                timerDiv.style.color = "#991B1B";
                                timerDiv.style.borderColor = "#FCA5A5";
                                timerDiv.style.backgroundColor = "#FEF2F2";
                            }}
                        }}
                    }}, 1000);
                </script>
                """
                components.html(timer_js, height=0, width=0)
            else:
                cleanup_js = """
                <script>
                    var parentDoc = window.parent.document;
                    var timerDiv = parentDoc.getElementById('floating-timer');
                    if (timerDiv) timerDiv.remove();
                    if (window.timerInterval) clearInterval(window.timerInterval);
                </script>
                """
                components.html(cleanup_js, height=0, width=0)

        if st.session_state['auto_submitted']:
            st.error("⏰ **Time Expired!** The 2-hour window has lapsed. Your responses have been automatically submitted.")

        if not st.session_state['exam_submitted']:
            if st.button("🔄 Reset Test / Clear Answers", use_container_width=True):
                reset_test_state()
                st.rerun()

        st.markdown("---")

        # ==========================================
        # --- HTML/CSS QUESTION NAVIGATOR GRID ---
        # ==========================================
        if full_paper and not st.session_state['exam_submitted']:
            with st.expander("📊 Question Navigator Grid", expanded=False):
                grid_html = '<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; text-align: center;">'
                
                for i, row in filtered_df.reset_index().iterrows():
                    qid = str(row['question_id'])
                    q_num = i + 1 
                    
                    if qid in st.session_state['marked_for_review']:
                        bg_color = "#EF4444"
                        text_color = "white"
                    elif qid in st.session_state['user_answers']:
                        bg_color = "#22C55E"
                        text_color = "white"
                    else:
                        bg_color = "#E2E8F0"
                        text_color = "#334155"
                        
                    cell_html = f'<div style="background-color: {bg_color}; color: {text_color}; padding: 10px; border-radius: 6px; font-weight: bold;">{q_num}</div>'
                    grid_html += cell_html
                    
                grid_html += '</div>'
                st.markdown(grid_html, unsafe_allow_html=True)

        # ==========================================
        # --- QUESTION RENDERING & PAGINATION ---
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
            questions_per_page = 5 if full_paper else len(filtered_df)
            total_pages = (len(filtered_df) - 1) // questions_per_page + 1
            
            if st.session_state['current_page'] >= total_pages:
                st.session_state['current_page'] = max(0, total_pages - 1)
                
            start_idx = st.session_state['current_page'] * questions_per_page
            end_idx = start_idx + questions_per_page
            page_df = filtered_df.iloc[start_idx:end_idx]

            for index, row in page_df.iterrows():
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
                
                if full_paper:
                    is_marked = qid in st.session_state['marked_for_review']
                    mark_review = st.checkbox("📌 Mark for Review", value=is_marked, key=f"review_{qid}")
                    if mark_review:
                        st.session_state['marked_for_review'].add(qid)
                    elif qid in st.session_state['marked_for_review']:
                        st.session_state['marked_for_review'].discard(qid)

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
            
            if full_paper:
                col_prev, col_spacer, col_next = st.columns([1, 2, 1])
                with col_prev:
                    if st.session_state['current_page'] > 0:
                        if st.button("⬅️ Previous Page", use_container_width=True):
                            st.session_state['current_page'] -= 1
                            st.rerun()
                with col_next:
                    if st.session_state['current_page'] < total_pages - 1:
                        if st.button("Next Page ➡️", use_container_width=True):
                            st.session_state['current_page'] += 1
                            st.rerun()
                st.markdown(f"<div style='text-align: center; color: gray;'>Page {st.session_state['current_page'] + 1} of {total_pages}</div>", unsafe_allow_html=True)
                st.markdown("---")

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
                    'Topic': row['topic'] if 'topic' in row else "N/A",
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
