
from google.genai import types

from src.agent import TeoAgent


class FakeResponse:

    def __init__(self, text=None, function_calls=None):
        self.text = text
        self.function_calls = function_calls or []


class FakeSession:

    def __init__(self, responses=None):
        self.messages = []
        self.responses = list(responses or [])

    def send_message(self, message):
        self.messages.append(message)

        if self.responses:
            return self.responses.pop(0)

        return FakeResponse(text="Claro! Como posso ajudar?")


class FakeChats:

    def __init__(self, responses=None):
        self.session = FakeSession(responses)

    def create(self, **kwargs):
        return self.session


class FakeClient:

    def __init__(self, responses=None):
        self.chats = FakeChats(responses)


class FakeProductRepository:

    def __init__(self, products=None):
        self.products = products if products is not None else [
            {
                "product_id": 1,
                "name": "Yamaha C40",
                "category_name": "Violões",
                "price_brl": 599.90,
                "stock_quantity": 12,
                "status": "active"
            }
        ]
        self.searches = []

    def search_products(self, **kwargs):
        self.searches.append(kwargs)
        return self.products


def make_product_call(**kwargs):
    return types.FunctionCall(
        name="search_products",
        args=kwargs
    )


def test_agent_returns_response():
    client = FakeClient()

    agent = TeoAgent(client=client)

    answer = agent.chat("Oi, Téo!")

    assert answer == "Claro! Como posso ajudar?"


def test_agent_uses_same_session():
    client = FakeClient()
    agent = TeoAgent(client=client)

    agent.chat("Quero aprender violão.")
    agent.chat("Qual você recomenda?")

    assert client.chats.session.messages == [
        "Quero aprender violão.",
        "Qual você recomenda?"
    ]


def test_empty_message_does_not_call_api():
    client = FakeClient()
    agent = TeoAgent(client=client)

    answer = agent.chat("   ")

    assert answer == "Pode me mandar sua dúvida?"
    assert client.chats.session.messages == []


def test_agent_searches_products():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_product_call(category="Violões")
            ]
        ),
        FakeResponse(text="Temos o Yamaha C40 por R$ 599,90.")
    ])

    repository = FakeProductRepository()

    agent = TeoAgent(
        client=client,
        product_repository=repository
    )

    answer = agent.chat("Quais violões vocês têm?")

    assert repository.searches == [
        {"category": "Violões"}
    ]
    assert answer == "Temos o Yamaha C40 por R$ 599,90."


def test_agent_respects_price_filter():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_product_call(
                    category="Violões",
                    max_price=800
                )
            ]
        ),
        FakeResponse(text="Encontrei opções até R$ 800.")
    ])

    repository = FakeProductRepository()

    agent = TeoAgent(
        client=client,
        product_repository=repository
    )

    agent.chat("Quero um violão até R$ 800.")

    assert repository.searches == [
        {
            "category": "Violões",
            "max_price": 800
        }
    ]


def test_agent_returns_empty_catalog_results():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_product_call(category="Violões")
            ]
        ),
        FakeResponse(text="Não encontrei violões disponíveis.")
    ])

    repository = FakeProductRepository(products=[])

    agent = TeoAgent(
        client=client,
        product_repository=repository
    )

    answer = agent.chat("Tem algum violão disponível?")

    assert answer == "Não encontrei violões disponíveis."

    tool_message = client.chats.session.messages[1]

    assert tool_message[0].function_response.response == {
        "products": []
    }


def test_agent_sends_catalog_results_to_gemini():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_product_call(
                    category="Violões",
                    max_price=800
                )
            ]
        ),
        FakeResponse(text="O Yamaha C40 está disponível.")
    ])

    repository = FakeProductRepository()

    agent = TeoAgent(
        client=client,
        product_repository=repository
    )

    agent.chat("Tem violão até R$ 800?")

    messages = client.chats.session.messages

    assert len(messages) == 2
    assert messages[0] == "Tem violão até R$ 800?"

    tool_message = messages[1]

    assert isinstance(tool_message, list)
    assert len(tool_message) == 1
    assert isinstance(tool_message[0], types.Part)

    function_response = tool_message[0].function_response

    assert function_response.name == "search_products"
    assert function_response.response == {
        "products": repository.products
    }
