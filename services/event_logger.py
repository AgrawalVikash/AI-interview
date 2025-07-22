import requests

# BACKEND_ENDPOINT = "http://localhost:5000/api/proctoring-event"  # Replace with your backend endpoint

# def log_proctoring_event(interview_id, event, reason):
#     payload = {
#         "interview_id": interview_id,
#         "event": event,
#         "reason": reason
#     }
#     try:
#         requests.post(BACKEND_ENDPOINT, json=payload)
#     except Exception as e:
#         print(f"Failed to log event: {e}")


def log_proctoring_event(interview_id, event_type, message, backend_url="http://localhost:5000/api/proctoring/log"):
    payload = {
        "interviewId": interview_id,
        "event": event_type,
        "message": message
    }
    try:
        requests.post(backend_url, json=payload, timeout=3)
    except:
        pass