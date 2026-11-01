
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


class FakePromotionRepository:

    def __init__(self, promotions=None):
        self.promotions = promotions if promotions is not None else [
            {
                "promotion_id": 10,
                "product_id": 1,
                "name": "Yamaha C40",
                "description": "Desconto especial",
                "original_price": 599.90,
                "discount_percent": 10,
                "final_price": 539.91
            }
        ]
        self.active_calls = 0
        self.product_searches = []

    def get_active_promotions(self):
        self.active_calls += 1
        return self.promotions

    def get_product_promotion(self, product_id):
        self.product_searches.append(product_id)

        for promotion in self.promotions:
            if promotion["product_id"] == product_id:
                return promotion

        return None


def make_product_call(**kwargs):
    return types.FunctionCall(
        name="search_products",
        args=kwargs
    )


def make_promotion_call(name, **kwargs):
    return types.FunctionCall(
        name=name,
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


def test_agent_gets_active_promotions():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call("get_active_promotions")
            ]
        ),
        FakeResponse(text="Temos o Yamaha C40 com 10% de desconto.")
    ])

    repository = FakePromotionRepository()

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    answer = agent.chat("Quais produtos estão em promoção?")

    assert repository.active_calls == 1
    assert answer == "Temos o Yamaha C40 com 10% de desconto."

    tool_message = client.chats.session.messages[1]
    function_response = tool_message[0].function_response

    assert function_response.name == "get_active_promotions"
    assert function_response.response == {
        "promotions": repository.promotions
    }


def test_agent_returns_empty_promotions():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call("get_active_promotions")
            ]
        ),
        FakeResponse(text="Não temos promoções disponíveis no momento.")
    ])

    repository = FakePromotionRepository(promotions=[])

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    answer = agent.chat("Tem alguma promoção?")

    assert answer == "Não temos promoções disponíveis no momento."
    assert repository.active_calls == 1

    tool_message = client.chats.session.messages[1]

    assert tool_message[0].function_response.response == {
        "promotions": []
    }


def test_agent_gets_product_promotion():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call(
                    "get_product_promotion",
                    product_id=1
                )
            ]
        ),
        FakeResponse(text="O Yamaha C40 está com 10% de desconto.")
    ])

    repository = FakePromotionRepository()

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    answer = agent.chat("O Yamaha C40 está em promoção?")

    assert repository.product_searches == [1]
    assert answer == "O Yamaha C40 está com 10% de desconto."

    tool_message = client.chats.session.messages[1]

    assert tool_message[0].function_response.response == {
        "promotion": repository.promotions[0]
    }


def test_agent_returns_no_product_promotion():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call(
                    "get_product_promotion",
                    product_id=999
                )
            ]
        ),
        FakeResponse(text="Esse produto não está em promoção.")
    ])

    repository = FakePromotionRepository()

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    answer = agent.chat("O produto 999 está em promoção?")

    assert repository.product_searches == [999]
    assert answer == "Esse produto não está em promoção."

    tool_message = client.chats.session.messages[1]

    assert tool_message[0].function_response.response == {
        "promotion": None
    }


def test_agent_rejects_invalid_promotion_product_id():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call(
                    "get_product_promotion",
                    product_id=-1
                )
            ]
        ),
        FakeResponse(text="Não consegui consultar esse produto.")
    ])

    repository = FakePromotionRepository()

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    agent.chat("Consulte a promoção do produto -1.")

    assert repository.product_searches == []

    tool_message = client.chats.session.messages[1]

    assert tool_message[0].function_response.response == {
        "error": "ID do produto inválido"
    }


def test_agent_handles_multiple_promotion_calls():
    client = FakeClient([
        FakeResponse(
            function_calls=[
                make_promotion_call("get_active_promotions"),
                make_promotion_call(
                    "get_product_promotion",
                    product_id=1
                )
            ]
        ),
        FakeResponse(text="O Yamaha C40 está em promoção.")
    ])

    repository = FakePromotionRepository()

    agent = TeoAgent(
        client=client,
        promotion_repository=repository
    )

    answer = agent.chat("Quais promoções existem para o Yamaha C40?")

    assert repository.active_calls == 1
    assert repository.product_searches == [1]
    assert answer == "O Yamaha C40 está em promoção."

    tool_message = client.chats.session.messages[1]

    assert len(tool_message) == 2
    assert [
        part.function_response.name
        for part in tool_message
    ] == [
        "get_active_promotions",
        "get_product_promotion"
    ]
