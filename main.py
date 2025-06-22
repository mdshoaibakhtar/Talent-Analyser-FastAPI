from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from typing import List, Dict
import fitz  # PyMuPDF
import docx2txt
import io
from transformers import pipeline
from sentence_transformers import SentenceTransformer, util
# from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
import uvicorn
import base64
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup

from app import TestModel
import openai

app = FastAPI()

# Load NLP pipeline & embeddings model
# ner = pipeline("ner", grouped_entities=True)
# embedder = SentenceTransformer("all-MiniLM-L6-v2")
# rewrite_tokenizer = T5Tokenizer.from_pretrained("google/flan-t5-base")
# rewrite_model = T5ForConditionalGeneration.from_pretrained("google/flan-t5-base")

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

class ParsedData(BaseModel):
    text: str
    entities: List[Dict[str, str]]

class UploadResumeModel(BaseModel):
    file_name: str
    base64_data: str
    prompt : str

class UrlInput(BaseModel):
    url: str


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

def parse_entities(text: str) -> List[Dict[str, str]]:
    return text


def scrape_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to fetch page: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    paragraphs = [p.text.strip() for p in soup.find_all("p")]
    return "\n".join(paragraphs[:20])

@app.post("/upload-resume")
def upload_resume(input: UploadResumeModel):
    # print('Received file:', input)
    text = extract_text_from_base64(input.base64_data, input.file_name)
    prompt = text+input.prompt
    response = openai.OpenAI().get_response(prompt)
    return {"response": response}

@app.post('/test-openai')
def test_openai(input : TestModel):
    response = openai.OpenAI().get_response(input.prompt)
    return {"response": response}

@app.post("/scrape-url")
def scrape_url_text(input: UrlInput):
    text = scrape_text_from_url(input.url)
    return {"extracted_text": text[:1000] + "..."}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume and Job Description Matcher API. Use /docs for documentation."}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
