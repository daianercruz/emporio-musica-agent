
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types


load_dotenv()


class TeoAgent:

    def __init__(self, client=None):
        self.client = client or genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        self.instructions = """
        You are Téo, the virtual assistant of Empório da Música,
        a musical instrument store in Campo Grande, Brazil.

        Always speak in natural Brazilian Portuguese.
        Be friendly, direct, helpful and conversational.
        Avoid long answers and repetitive greetings.

        Never invent product prices, stock availability,
        promotions, order details or store policies.

        You do not have access to store data yet.
        If a customer asks about specific store information,
        explain that you cannot confirm it right now.
        """

        self.session = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.instructions
            )
        )

    def chat(self, message: str) -> str:
        if not message.strip():
            return "Pode me mandar sua dúvida?"

        response = self.session.send_message(message)

        return response.text or "Não consegui responder agora. Pode tentar novamente?"
