# 🛡️ Defence Pathshala: PYQ Intelligence Engine

**Transform raw Previous Year Questions (PYQs) into a tactical, data-driven preparation engine.**

Stop passive reading and start actively eliminating. The Defence Pathshala PYQ Intelligence Engine is a comprehensive, interactive dashboard designed to analyze performance patterns, isolate specific examiner traps, and dynamically build a personalized syllabus roadmap to maximize your final score in UPSC defence examinations.

## 🚀 Key Features

*   **Multi-Exam Architecture:** Seamlessly toggle between distinct examination databases on the landing page. Currently configured for **CDS II 2026** and **CAPF-AC 2025**.
*   **Tactical Test Arena:**
    *   **Full Mock Mode:** Attempt a complete 125-question paper with a continuous 2-hour floating JavaScript timer, mimicking real exam pressure.
    *   **Instant Feedback Mode:** Practice questions individually with immediate answer validation and detailed explanations.
*   **Granular Database Overview:** Visualize subject weightage, question structures, and difficulty distributions through interactive Plotly charts before starting a test.
*   **Advanced Performance Audit:**
    *   **Scorecard:** Real-time net score and accuracy calculation accounting for standard UPSC negative marking (-0.67).
    *   **Mistake Vault:** Tag and categorize errors (Conceptual Gap, Factual Recall Failure, Silly Mistake) to identify systemic weaknesses.
    *   **Strategic Roadmap:** Receive automated, algorithmic feedback dictating which specific subjects require priority revision based on your accuracy metrics.

## 🛠️ Tech Stack

*   **Language:** Python 3.x
*   **Framework:** Streamlit (UI & State Management)
*   **Data Manipulation:** Pandas
*   **Data Visualization:** Plotly Express

## 📂 Repository Structure

```text
├── app.py                   # Main Streamlit application script
├── PYQ_Intelligence.csv     # Master dataset containing CDS and CAPF questions
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
