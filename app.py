from fastapi import FastAPI
import uvicorn
import openai

app = FastAPI()


@app.get('/')
def read_root():
    return {"Hello World!"}

@app.get('/test-openai')
def test_openai():
    response = openai.OpenAI().get_response()
    return {"message": response}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
