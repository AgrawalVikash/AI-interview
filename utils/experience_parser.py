import re

# def extract_experience(resume_text):
#     pattern = re.findall(r"(\d+)\+?\s+years?\s+of\s+experience", resume_text, re.IGNORECASE)
#     if pattern:
#         return int(max(pattern, key=int))
#     return 2  # default if not found

def extract_experience(text):
    years = re.findall(r"(\d+)\+?\s+years?", text, re.IGNORECASE)
    return int(max(years, key=int)) if years else 2