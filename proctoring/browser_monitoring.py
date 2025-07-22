import streamlit as st

def inject_browser_monitoring(interview_id, report_dir):
    log_path = f"{report_dir}/browser_events_{interview_id}.json"
    st.markdown(
        f"""
        <script>
        let logs = [];
        window.onblur = () => logs.push({{time: new Date().toISOString(), message: 'Tab out detected'}});
        document.addEventListener('keydown', e => {{
            if (e.key === 'F12' || (e.ctrlKey && e.shiftKey && (e.key === 'I' || e.key === 'J'))) {{
                logs.push({{time: new Date().toISOString(), message: 'Devtools open detected'}});
            }}
        }});
        window.onbeforeunload = () => {{
            fetch('http://localhost:5000/api/proctoring/log_browser_event', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{interviewId: '{interview_id}', events: logs}})
            }});
        }};
        </script>
        """, unsafe_allow_html=True
    )
