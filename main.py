from fastapi import FastAPI
from pdfminer.high_level import extract_text
from pydantic import BaseModel
import docx2txt
import io
import uvicorn
import base64
from fastapi.middleware.cors import CORSMiddleware
import requests
from bs4 import BeautifulSoup
import json
import openai

app = FastAPI()

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
    base64_data: str
    prompt : str

class UrlInput(BaseModel):
    url: str

class DataAnalysisModel(BaseModel):
    resume_base64: str
    jd_base64: str
    prompt: str

def extract_text_from_base64(base64_str: str, filename: str) -> str:
    """
    Extract text from base64-encoded file content.

    :param base64_str: Base64 encoded file content.
    :param filename: Original filename with extension to detect file type.
    :return: Extracted text.
    """
    # Fix padding if needed
    missing_padding = len(base64_str) % 4
    if missing_padding:
        base64_str += '=' * (4 - missing_padding)

    # Decode and convert to file-like object
    decoded = base64.b64decode(base64_str)
    file_like = io.BytesIO(decoded)

    if filename.endswith(".pdf"):
        # Extract text using pdfminer.six
        text = extract_text(file_like)
        return text

    elif filename.endswith(".docx"):
        # Extract text using docx2txt
        text = docx2txt.process(file_like)
        return text

    elif filename.endswith(".txt"):
        return file_like.read().decode("utf-8")

    else:
        raise ValueError("Unsupported file format")
    
def scrape_text_from_url(url: str) -> str:
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return f"Failed to fetch page: {response.status_code}"
    soup = BeautifulSoup(response.text, "html.parser")
    response = openai.OpenAI().get_response("Extract the text from the HTML content of the job description page. Company name, job title, and job description, Just extract the all content from here which help us to understand about job role. Please extract and understand the company from given url `{url}` it should be like https://company_name.domain.com"+soup.prettify())
    return response


@app.post("/data-analysis")
def data_analysis(input: DataAnalysisModel):
    resume_text = extract_text_from_base64(input.resume_base64, "resume.pdf")
    jd_text = extract_text_from_base64(input.jd_base64, "job_description.pdf")
    prompt = input.prompt + "Resume text: " + resume_text + " Job Description text: " + jd_text
    # print(prompt)
    response = openai.OpenAI().get_response(prompt)
    return {
        "status_code": 200,
        "status": "success",
        "message": "Data analysis completed successfully.",
        "data": json.loads(response),
    }


@app.post("/upload-resume")
def upload_resume(input: UploadResumeModel):
    text = extract_text_from_base64(input.base64_data, input.file_name)
    prompt = text+input.prompt
    response = openai.OpenAI().get_response(prompt)
    return {"response": response}

@app.post("/scrape-url")
def scrape_url_text(input: UrlInput):
    text = scrape_text_from_url(input.url)
    return {"extracted_text": text[:len(text)]}

@app.get("/")
def read_root():
    return {"message": "Welcome to the Resume and Job Description Matcher API. Use /docs for documentation."}
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
