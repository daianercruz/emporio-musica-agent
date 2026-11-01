
from src.services.pricing_service import PricingService


class FakeProductRepository:

    def get_product_by_id(self, product_id):
        products = {
            1: {
                "product_id": 1,
                "name": "Yamaha C40",
                "price_brl": 1000.00,
                "stock_quantity": 5,
                "status": "active"
            },
            2: {
                "product_id": 2,
                "name": "Fender Stratocaster",
                "price_brl": 1200.00,
                "stock_quantity": 3,
                "status": "active"
            },
            3: {
                "product_id": 3,
                "name": "Casio CT-S200",
                "price_brl": 500.00,
                "stock_quantity": 0,
                "status": "active"
            }
        }

        return products.get(product_id)


class FakePromotionRepository:

    def get_product_promotion(self, product_id):
        if product_id == 1:
            return {
                "description": "Special Offer",
                "discount_percent": 15,
                "final_price": 850.00
            }

        return None


def create_service():
    return PricingService(
        product_repository=FakeProductRepository(),
        promotion_repository=FakePromotionRepository()
    )


def test_pix_discount():
    service = create_service()
    price = service.get_price(2)

    assert price["pix_price"] == 1140.00
    assert price["lowest_price_method"] == "pix"


def test_promotion_discount():
    service = create_service()
    price = service.get_price(1)

    assert price["promotion"]["price"] == 850.00
    assert price["lowest_price"] == 850.00
    assert price["lowest_price_method"] == "promotion"


def test_discounts_are_not_combined():
    service = create_service()
    price = service.get_price(1)

    assert price["lowest_price"] == 850.00


def test_unknown_product():
    service = create_service()

    assert service.get_price(999) is None


def test_unavailable_product():
    service = create_service()

    assert service.get_price(3) is None


def test_installment_minimum():
    service = create_service()
    result = service.get_installments(1)

    options = result["installment_options"]
    quantities = [option["installments"] for option in options]

    assert 6 in quantities
    assert 10 in quantities
    assert 11 not in quantities


def test_installments_require_confirmation():
    service = create_service()
    result = service.get_installments(2)

    assert result["requires_payment_confirmation"] is True
