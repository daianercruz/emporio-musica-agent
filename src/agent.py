
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from src.repositories.product_repository import ProductRepository


load_dotenv()


class TeoAgent:

    def __init__(self, client=None, product_repository=None):
        self.client = client if client is not None else genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options=types.HttpOptions(
                timeout=30000
            )
        )

        self.model = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

        self.products = (
            product_repository
            if product_repository is not None
            else ProductRepository()
        )

        self.instructions = """
        You are Téo, the virtual assistant of Empório da Música,
        a musical instrument store in Campo Grande, Brazil.

        Always speak in natural Brazilian Portuguese.
        Be friendly, direct and conversational.
        Keep answers concise and avoid repetitive greetings.

        Use search_products whenever customers ask about products,
        prices, availability or product recommendations.

        Use the category parameter for product types, such as
        Violões, Guitarras, Teclados and Ukuleles.

        Use the name parameter for brands or specific models.

        Never invent products, prices or stock availability.
        Only use information returned by the store catalog.

        Respect the customer's budget and preferences.
        If no matching products are found, say so clearly.

        After receiving catalog results, answer the customer
        directly instead of searching again for the same request.

        You cannot access orders, promotions or store policies yet.
        Do not invent that information.
        """

        search_products_tool = types.FunctionDeclaration(
            name="search_products",
            description="Search the store catalog. Use category for product types and name for brands or specific models.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "name": {
                        "type": "STRING",
                        "description": "Brand or specific product model"
                    },
                    "category": {
                        "type": "STRING",
                        "description": "Product category, such as Violões, Guitarras, Teclados or Ukuleles"
                    },
                    "max_price": {
                        "type": "NUMBER",
                        "description": "Maximum product price in Brazilian reais"
                    }
                }
            }
        )

        self.session = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.instructions,
                tools=[
                    types.Tool(
                        function_declarations=[search_products_tool]
                    )
                ],
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

    def chat(self, message: str) -> str:
        if not message.strip():
            return "Pode me mandar sua dúvida?"

        try:
            response = self.session.send_message(message)
            calls = response.function_calls or []

            if not calls:
                return response.text or "Não consegui responder agora."

            results = []

            for call in calls:
                if call.name == "search_products":
                    args = dict(call.args or {})

                    allowed_args = {
                        key: value
                        for key, value in args.items()
                        if key in {"name", "category", "max_price"}
                    }

                    products = self.products.search_products(
                        **allowed_args
                    )

                    result = {"products": products}
                else:
                    result = {"error": "Função não disponível"}

                results.append(
                    types.Part.from_function_response(
                        name=call.name,
                        response=result
                    )
                )

            response = self.session.send_message(results)

            if response.function_calls:
                return "Encontrei os dados do catálogo, mas não consegui concluir a resposta. Pode reformular sua pergunta?"

            return response.text or "Não consegui apresentar os produtos encontrados."

        except ServerError as error:
            if error.code in (503, 504):
                return "Estou com dificuldade para acessar o sistema agora. Pode tentar novamente em instantes?"
            raise

        except ClientError as error:
            if error.code == 429:
                return "O limite de consultas foi atingido. Pode tentar novamente mais tarde?"
            raise
