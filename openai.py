import os
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential
import dotenv
dotenv.load_dotenv()

class OpenAI:
    endpoint = "https://models.github.ai/inference"
    model = "openai/gpt-4.1"
    token = os.getenv("OPENAI_API_KEY")

    # def __init__(self):
    #     self.api_key = os.getenv("AZURE_OPENAI_API_KEY")

    def get_client(self):
        return ChatCompletionsClient(
            endpoint=self.endpoint,
            credential=AzureKeyCredential(self.token),
        )

    def get_response(self, prompt:str) -> str:
        client = self.get_client()
        response = client.complete(
            messages=[
                SystemMessage("You are a helpful assistant."),
                UserMessage(prompt),
            ],
            temperature=1.0,
            top_p=1.0,
            model=self.model
        )
        return response.choices[0].message.content