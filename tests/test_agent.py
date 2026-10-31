
from src.agent import TeoAgent


class FakeSession:

    def __init__(self):
        self.messages = []

    def send_message(self, message):
        self.messages.append(message)
        return type("Response", (), {"text": "Claro! Como posso ajudar?"})()


class FakeChats:

    def __init__(self):
        self.session = FakeSession()

    def create(self, **kwargs):
        return self.session


class FakeClient:

    def __init__(self):
        self.chats = FakeChats()


def test_agent_returns_response():
    agent = TeoAgent(client=FakeClient())

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
