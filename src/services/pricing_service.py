
from decimal import Decimal, ROUND_HALF_UP

from src.repositories.product_repository import ProductRepository
from src.repositories.promotion_repository import PromotionRepository


class PricingService:

    def __init__(self, product_repository=None, promotion_repository=None):
        self.products = product_repository or ProductRepository()
        self.promotions = promotion_repository or PromotionRepository()

    def get_price(self, product_id: int):
        product = self.products.get_product_by_id(product_id)

        if product is None:
            return None

        if product["status"] != "active" or product["stock_quantity"] <= 0:
            return None

        original_price = Decimal(str(product["price_brl"]))
        promotion = self.promotions.get_product_promotion(product_id)

        pix_price = self._round(original_price * Decimal("0.95"))

        result = {
            "product_id": int(product_id),
            "name": product["name"],
            "original_price": float(original_price),
            "pix_price": float(pix_price),
            "promotion": None,
            "lowest_price": float(pix_price),
            "lowest_price_method": "pix"
        }

        if promotion:
            promotional_price = Decimal(str(promotion["final_price"]))

            result["promotion"] = {
                "description": promotion["description"],
                "discount_percent": promotion["discount_percent"],
                "price": float(promotional_price)
            }

            if promotional_price < pix_price:
                result["lowest_price"] = float(promotional_price)
                result["lowest_price_method"] = "promotion"

        return result

    def get_installments(self, product_id: int):
        product = self.products.get_product_by_id(product_id)

        if product is None:
            return None

        if product["status"] != "active" or product["stock_quantity"] <= 0:
            return None

        price = Decimal(str(product["price_brl"]))
        options = []

        for installments in range(4, 13):
            minimum = Decimal("80") if installments <= 6 else Decimal("100")
            installment_value = self._round(price / installments)

            if price / installments >= minimum:
                options.append({
                    "installments": installments,
                    "reference_amount": float(installment_value)
                })

        return {
            "product_id": int(product_id),
            "base_price": float(price),
            "installment_options": options,
            "requires_payment_confirmation": True
        }

    @staticmethod
    def _round(value):
        return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
