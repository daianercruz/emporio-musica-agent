
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

from src.repositories.product_repository import ProductRepository
from src.repositories.order_repository import OrderRepository
from src.repositories.promotion_repository import PromotionRepository
from src.repositories.policy_repository import PolicyRepository


load_dotenv()


class TeoAgent:
    def __init__(
        self,
        client=None,
        product_repository=None,
        order_repository=None,
        promotion_repository=None,
        policy_repository=None
    ):
        self.client = client if client is not None else genai.Client(
            api_key=os.getenv("GEMINI_API_KEY"),
            http_options=types.HttpOptions(timeout=30000)
        )

        self.model = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

        self.products = (
            product_repository
            if product_repository is not None
            else ProductRepository()
        )

        self.orders = (
            order_repository
            if order_repository is not None
            else OrderRepository()
        )

        self.promotions = (
            promotion_repository
            if promotion_repository is not None
            else PromotionRepository()
        )

        self.policies = (
            policy_repository
            if policy_repository is not None
            else PolicyRepository()
        )

        self.instructions = """
        You are Téo, the virtual assistant of Empório da Música,
        a musical instrument store in Campo Grande, Brazil.

        Always speak in natural Brazilian Portuguese.
        Be friendly, direct and conversational.
        Keep answers concise and avoid repetitive greetings.

        Use search_products whenever customers ask about products,
        prices, availability or product recommendations.

        Use the category parameter for product types.
        Use the name parameter for brands or specific models.

        Never invent products, prices or stock availability.
        Only use information returned by the store catalog.

        Respect the customer's budget and preferences.

        Use get_active_promotions when customers ask about current
        promotions, discounts or promotional offers.

        Use get_product_promotion when a customer asks whether
        a specific product has a promotion and its product ID
        is already known from the catalog or conversation.

        If the product ID is unknown, use search_products first.
        Never guess product IDs.

        Never invent discounts, promotional prices or offers.
        Only present promotions returned by the tools.

        When a request combines products, prices and promotions,
        consult all relevant tools before answering.

        Do not claim that a product has a promotion unless
        it matches a promotion returned by the tools.

        Use get_order when a customer wants to check an order.

        When a customer wants to check an order, collect the
        required information one question at a time.

        First, ask for the order number.
        After the customer provides the order number, ask for
        the email address used for the purchase.

        Never ask for both details in the same question.

        Do not call get_order until both details are available.

        Remember the order number and email provided during
        the conversation.

        Never reveal order details without a matching order
        number and customer email.

        If the order is not found, explain that the provided
        information did not match an order.

        Never invent order statuses, delivery dates or
        tracking codes.

        Do not ask for passwords, payment card details or
        other unnecessary personal information.

        Use search_store_policies whenever customers ask about
        store rules, returns, exchanges, refunds, warranties,
        shipping, deliveries, payment methods or opening hours.

        Always consult the store policy repository before
        answering questions about store policies.

        Answer policy questions exclusively using information
        returned by search_store_policies.

        Do not invent policy rules, deadlines, exceptions,
        payment conditions or store opening hours.

        If the retrieved passages do not contain enough
        information to answer, clearly explain that you
        could not confirm the policy.

        Distinguish online purchases from in-store purchases
        whenever the policy makes that distinction.

        Do not assume the purchase channel if the customer
        has not provided that information.

        Do not confuse return deadlines with exchange
        deadlines or warranty periods.

        When answering questions about store policies,
        respond naturally as a customer support assistant.

        Never mention page numbers, PDF files, document names
        or internal sources to customers.

        Present policy information directly, without phrases
        such as "according to page 7".

        After receiving tool results, determine whether
        additional tool calls are needed to answer the question.

        Use additional tools when necessary, but avoid
        repeating the same consultation unnecessarily.

        Never claim to have canceled, refunded or modified
        an order because these actions are not available.

        If a request is outside the store's scope,
        politely explain what you can help with.
        
        When a customer asks about returning or exchanging a product
        without specifying whether the purchase was made online
        or in a physical store, ask which purchase channel was used
        before explaining the applicable return policy.

        Do not assume that the purchase was made online or in-store.

        Ask only one clarification question at a time.

        Once the customer confirms the purchase channel,
        consult the store policies and explain the applicable rules.
        """

        search_products_tool = types.FunctionDeclaration(
            name="search_products",
            description="Search products in the store catalog.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "name": {
                        "type": "STRING",
                        "description": "Product brand or model"
                    },
                    "category": {
                        "type": "STRING",
                        "description": "Product category"
                    },
                    "max_price": {
                        "type": "NUMBER",
                        "description": "Maximum price in Brazilian reais"
                    }
                }
            }
        )

        get_order_tool = types.FunctionDeclaration(
            name="get_order",
            description=(
                "Retrieve an order using its number "
                "and the customer's email."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "order_id": {
                        "type": "INTEGER",
                        "description": "Order number"
                    },
                    "customer_email": {
                        "type": "STRING",
                        "description": "Email address used for the order"
                    }
                },
                "required": ["order_id", "customer_email"]
            }
        )

        get_active_promotions_tool = types.FunctionDeclaration(
            name="get_active_promotions",
            description=(
                "Retrieve active promotions for available products."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {}
            }
        )

        get_product_promotion_tool = types.FunctionDeclaration(
            name="get_product_promotion",
            description=(
                "Retrieve the active promotion "
                "for a specific product ID."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "product_id": {
                        "type": "INTEGER",
                        "description": "Product ID from the store catalog"
                    }
                },
                "required": ["product_id"]
            }
        )

        search_store_policies_tool = types.FunctionDeclaration(
            name="search_store_policies",
            description=(
                "Search the official store policy PDF for information "
                "about returns, exchanges, refunds, warranties, "
                "shipping, deliveries, payments and opening hours."
            ),
            parameters={
                "type": "OBJECT",
                "properties": {
                    "question": {
                        "type": "STRING",
                        "description": (
                            "Customer question or search terms "
                            "related to store policies"
                        )
                    }
                },
                "required": ["question"]
            }
        )

        self.session = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                system_instruction=self.instructions,
                tools=[
                    types.Tool(
                        function_declarations=[
                            search_products_tool,
                            get_order_tool,
                            get_active_promotions_tool,
                            get_product_promotion_tool,
                            search_store_policies_tool
                        ]
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
            max_tool_rounds = 5

            for _ in range(max_tool_rounds):
                calls = response.function_calls or []

                if not calls:
                    return (
                        response.text
                        or "Não consegui apresentar as informações encontradas."
                    )

                results = []

                for call in calls:
                    args = dict(call.args or {})

                    if call.name == "search_products":
                        allowed_args = {
                            key: value
                            for key, value in args.items()
                            if key in {"name", "category", "max_price"}
                        }

                        products = self.products.search_products(
                            **allowed_args
                        )

                        result = {"products": products}

                    elif call.name == "get_order":
                        order_id = args.get("order_id")
                        customer_email = args.get("customer_email")

                        if (
                            isinstance(order_id, int)
                            and not isinstance(order_id, bool)
                            and order_id > 0
                            and isinstance(customer_email, str)
                            and customer_email.strip()
                        ):
                            order = self.orders.get_order(
                                order_id=order_id,
                                customer_email=customer_email
                            )

                            result = {"order": order}
                        else:
                            result = {
                                "error": "Número do pedido ou e-mail inválido"
                            }

                    elif call.name == "get_active_promotions":
                        promotions = (
                            self.promotions.get_active_promotions()
                        )

                        result = {"promotions": promotions}

                    elif call.name == "get_product_promotion":
                        product_id = args.get("product_id")

                        if (
                            isinstance(product_id, int)
                            and not isinstance(product_id, bool)
                            and product_id > 0
                        ):
                            promotion = (
                                self.promotions.get_product_promotion(
                                    product_id=product_id
                                )
                            )

                            result = {"promotion": promotion}
                        else:
                            result = {
                                "error": "ID do produto inválido"
                            }

                    elif call.name == "search_store_policies":
                        question = args.get("question")

                        if (
                            isinstance(question, str)
                            and question.strip()
                        ):
                            policies = self.policies.search(
                                question=question,
                                limit=3
                            )

                            result = {"policies": policies}
                        else:
                            result = {
                                "error": "Pergunta de política inválida"
                            }

                    else:
                        result = {
                            "error": "Função não disponível"
                        }

                    results.append(
                        types.Part.from_function_response(
                            name=call.name,
                            response=result
                        )
                    )

                response = self.session.send_message(results)

            if response.function_calls:
                return (
                    "Não consegui concluir todas as consultas "
                    "necessárias. Pode tentar novamente?"
                )

            return (
                response.text
                or "Não consegui apresentar as informações encontradas."
            )

        except ServerError as error:
            if error.code in (503, 504):
                return (
                    "Estou com dificuldade para acessar o sistema agora. "
                    "Pode tentar novamente em instantes?"
                )
            raise

        except ClientError as error:
            if error.code == 429:
                return (
                    "O limite de consultas foi atingido. "
                    "Pode tentar novamente mais tarde?"
                )
            raise
