import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
from utils import file_parser, experience_parser
from core import llm_service

QUESTION_LIMIT = 3
DURATION_MIN = 45

def start_interview(interview_id, face_dir, report_dir):
    if "step" not in st.session_state:
        st.session_state.step = 0
        st.session_state.qa_log = []
        st.session_state.start_time = datetime.now()

    st.title("AI Interview Session")

    jd_file = st.file_uploader("Upload Job Description", type=["pdf", "txt"])
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "txt"])
    project_file = st.file_uploader("Upload Project Requirements", type=["pdf", "txt"])

    if st.button("Start Interview") and jd_file and resume_file and project_file:
        jd = file_parser.extract_text(jd_file)
        resume = file_parser.extract_text(resume_file)
        project = file_parser.extract_text(project_file)
        exp = experience_parser.extract_experience(resume)
        st.session_state.jd, st.session_state.resume, st.session_state.project, st.session_state.exp = jd, resume, project, exp
        st.session_state.step = 1

    if st.session_state.step == 1:
        elapsed = datetime.now() - st.session_state.start_time
        remaining = timedelta(minutes=DURATION_MIN) - elapsed
        if remaining.total_seconds() <= 0:
            st.error("Interview time over")
            st.session_state.step = 2
        else:
            st.info(f"⏳ Time Remaining: {remaining}")

            if len(st.session_state.qa_log) < QUESTION_LIMIT:
                question = llm_service.generate_question(st.session_state.jd, st.session_state.resume, st.session_state.project, st.session_state.exp)
                st.write(f"**Question {len(st.session_state.qa_log)+1}: {question}**")
                ans = st.text_area("Answer:")

                if st.button("Submit Answer"):
                    st.session_state.qa_log.append({"question": question, "answer": ans})
                    st.rerun()
            else:
                st.session_state.step = 2

    if st.session_state.step == 2:
        df = pd.DataFrame(st.session_state.qa_log)
        scores = [llm_service.evaluate_answer(q, a) for q, a in zip(df['question'], df['answer'])]
        df["score"] = scores
        avg_score = sum(scores)/len(scores)
        feedback = llm_service.generate_feedback(df)
        report_file = f"{report_dir}/report_{interview_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        with open(report_file, "w") as f:
            f.write(f"Average Score: {avg_score:.2f}\nFeedback: {feedback}\n\n")
            for idx, row in df.iterrows():
                f.write(f"Q{idx+1}: {row['question']}\nA{idx+1}: {row['answer']}\nScore: {row['score']}\n\n")

        st.success("Interview completed!")
        st.write(f"📄 Report generated at: {report_file}")
