from fastapi import FastAPI
import uvicorn
import openai
from pydantic import BaseModel

app = FastAPI()

class TestModel(BaseModel):
    prompt: str

@app.get('/')
def read_root():
    return {"Hello World!"}

@app.post('/test-openai')
def test_openai(input : TestModel):
    response = openai.OpenAI().get_response(input.prompt)
    return {"response": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
