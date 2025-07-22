import fitz  # PyMuPDF

# def extract_text(file):
#     text = ""
#     if file.name.endswith(".pdf"):
#         with fitz.open(stream=file.read(), filetype="pdf") as doc:
#             for page in doc:
#                 text += page.get_text()
#     else:
#         text = file.read().decode("utf-8")
#     return text

def extract_text(file):
    if file.name.endswith('.pdf'):
        with fitz.open(stream=file.read(), filetype="pdf") as doc:
            return "\n".join(page.get_text() for page in doc)
    else:
        return file.read().decode("utf-8")