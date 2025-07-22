import streamlit as st
import pandas as pd
import uuid
import os
from datetime import datetime, timedelta
from core import llm_service
from proctoring import face_detection
from utils import file_parser
from services import event_logger

# --- Constants ---
QUESTION_LIMIT = 3
INTERVIEW_DURATION_MINUTES = 45
INTERVIEW_ID = str(uuid.uuid4())
SESSION_START_TIME = datetime.now()
FACE_SNAPSHOT_DIR = "face_snapshots"

# --- Setup ---
st.set_page_config(page_title="AI Interviewer")
st.title("AI Interview Application")

# --- Init directories ---
if not os.path.exists(FACE_SNAPSHOT_DIR):
    os.makedirs(FACE_SNAPSHOT_DIR)

# --- Initial Face Snapshot ---
initial_snapshot = face_detection.capture_initial_face_snapshot()
event_logger.log_proctoring_event(INTERVIEW_ID, "initial_face_snapshot", initial_snapshot)

# --- JS to detect tab switch ---
st.markdown("""<script src="/static/js/focus_tracker.js"></script>""", unsafe_allow_html=True)

# --- Time logger ---
st.markdown(f"Session Started: {SESSION_START_TIME.strftime('%H:%M:%S')}")

# if st.button("Validate Face"):
#     face_present = proctoring_utils.detect_face()
#     if not face_present:
#         st.error("Face not detected or multiple faces found.")
#         backend_logger.log_proctoring_event(INTERVIEW_ID, "face_detection_failed", "face not detected")
#     else:
        # st.success("Face validated successfully")

# --- Session State Init ---
if "step" not in st.session_state:
    st.session_state.step = 0
    st.session_state.qa_log = []
    st.session_state.interview_id = INTERVIEW_ID
    st.session_state.start_time = SESSION_START_TIME
    st.session_state.current_answer = ""
    st.session_state.report_generated = False

# --- Upload Inputs ---
jd_file = st.file_uploader("Upload Job Description", type=["txt", "pdf", "docx"])
resume_file = st.file_uploader("Upload Resume", type=["txt", "pdf", "docx"])
project_file = st.file_uploader("Upload Project Requirements", type=["txt", "pdf", "docx"])

# --- Start Interview ---
if st.button("Start Interview") and jd_file and resume_file and project_file:
    jd_text = file_parser.extract_text(jd_file)
    resume_text = file_parser.extract_text(resume_file)
    project_text = file_parser.extract_text(project_file)
    experience = file_parser.extract_experience(resume_text)

    st.session_state.jd_text = jd_text
    st.session_state.resume_text = resume_text
    st.session_state.project_text = project_text
    st.session_state.experience = experience
    st.session_state.step = 1
    st.session_state.qa_log = []
    st.session_state.start_time = datetime.now()
    st.session_state.current_answer = ""

# --- Interview Flow ---
if st.session_state.step == 1:
    # --- Timer check ---
    elapsed = datetime.now() - st.session_state.start_time
    remaining_time = timedelta(minutes=INTERVIEW_DURATION_MINUTES) - elapsed

    if remaining_time.total_seconds() <= 0:
        st.warning("Interview time is over.")
        st.session_state.step = 2
    else:
        st.info(f"⏳ Remaining Time: {str(remaining_time).split('.')[0]}")

        # --- Display previous QA ---
        if st.session_state.qa_log:
            st.subheader("Interview Round 1")
            for i, qa in enumerate(st.session_state.qa_log, start=1):
                st.markdown(f"**Q{i}:** {qa['Question']}")
                st.markdown(f"**A{i}:** {qa['Answer']}")
                # st.markdown(f"**Score:** {qa['Score']}")
                st.markdown("---")

        # --- Ask next question ---
        if len(st.session_state.qa_log) < QUESTION_LIMIT:
            question = llm_service.generate_question(
                st.session_state.jd_text,
                st.session_state.resume_text,
                st.session_state.project_text,
                st.session_state.experience
            )
            st.session_state.current_question = question
            st.session_state.current_answer = ""

            st.subheader(f"Question {len(st.session_state.qa_log) + 1}")
            st.markdown(f"**{question}**")
            # remove value
            answer = st.text_area("Your Answer", value=st.session_state.current_answer, key=f"answer_{len(st.session_state.qa_log)}")

            # --- Manual face validation ---
            if st.button("Validate Face"):
                face_present = face_detection.detect_face()
                if not face_present:
                    st.error("Face not detected or multiple faces found.")
                    event_logger.log_proctoring_event(INTERVIEW_ID, "face_detection_failed", "face not detected")
                else:
                    st.success("Face validated successfully")
                    event_logger.log_proctoring_event(INTERVIEW_ID, "face_validation_success", "face present")

            if st.button("Submit Answer"):
                st.session_state.qa_log.append({
                    "Question": question,
                    "Answer": answer
                })

                # --- Save progress to Excel --- 
                df = pd.DataFrame(st.session_state.qa_log)
                excel_path = f"interview_{st.session_state.interview_id}.xlsx"
                df.to_excel(excel_path, index=False)

                if len(st.session_state.qa_log) >= QUESTION_LIMIT:
                    st.session_state.step = 2
                else:
                    st.rerun()

# --- Interview Report ---
if st.session_state.step == 2:
    if not st.session_state.report_generated:
        st.success("Interview Complete! Thank you for attending.")
        st.markdown("Please wait a few moments while your session is being saved...")

        excel_path = f"interview_{st.session_state.interview_id}.xlsx"
        df = pd.read_excel(excel_path)

        scores = []
        for _, row in df.iterrows():
            score = llm_service.evaluate_answer(row['Question'], row['Answer'])
            scores.append(score)
        df['Score'] = scores

        avg_score = df['Score'].mean()
        feedback = llm_service.generate_feedback(df)
        decision = "Promote to next round" if avg_score >= 6 else "Reject"

        # --- Save feedback report with Q/A and scores ---
        report_lines = [
            f"Interview ID: {st.session_state.interview_id}",
            f"Average Score: {avg_score:.2f}",
            f"Decision: {decision}\n",
            "Detailed Answers and Scores:"
        ]
        for i, row in df.iterrows():
            report_lines.append(f"Q{i+1}: {row['Question']}")
            report_lines.append(f"A{i+1}: {row['Answer']}")
            report_lines.append(f"Score: {row['Score']}\n")

        report_lines.append("Feedback:")
        report_lines.append(feedback)

        report_text = "\n".join(report_lines)
        report_path = f"interview_report_{st.session_state.interview_id}.txt"
        with open(report_path, "w") as report_file:
            report_file.write(report_text)

        # Clean up Excel file
        if os.path.exists(excel_path):
            try:
                os.remove(excel_path)
            except Exception as e:
                pass

        st.session_state.report_generated = True
        st.markdown("### ✅ Your session is saved.")
        st.markdown("You may now close this window.")
