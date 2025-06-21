from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
import fitz  # PyMuPDF
import docx2txt
import io
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
import uvicorn
import base64
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Load NLP pipeline & embeddings model
# ner = pipeline("ner", grouped_entities=True)
# embedder = SentenceTransformer("all-MiniLM-L6-v2")

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UploadResumeModel(BaseModel):
    file_name: str
    data:str


def extract_text_from_base64(base64_str: str, filename: str) -> str:
    """
    :param base64_str: base64 encoded file content
    :param filename: original filename with extension to detect file type
    :return: extracted text
    """
    missing_padding = len(base64_str) % 4
    if missing_padding:
        base64_str += '=' * (4 - missing_padding)
    decoded = base64.b64decode(base64_str)
    file_like = io.BytesIO(decoded)

    if filename.endswith(".pdf"):
        pdf = fitz.open(stream=file_like.read(), filetype="pdf")
        text = "\n".join([page.get_text() for page in pdf])
        return text

    elif filename.endswith(".docx"):
        text = docx2txt.process(file_like)
        return text

    elif filename.endswith(".txt"):
        return file_like.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file format")

@app.post("/upload-resume")
def upload_resume(input: UploadResumeModel):
    print('Received file:', input)
    text = extract_text_from_base64(input.data, input.file_name)
    return {"extracted_data": text[:3000], "length": len(text)}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume and Job Description Matcher API. Use /docs for documentation."}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
