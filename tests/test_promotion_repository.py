
import pandas as pd
import pytest

from src.repositories.promotion_repository import PromotionRepository


@pytest.fixture
def repository(tmp_path):
    products = pd.DataFrame([
        {
            "product_id": 1,
            "name": "Yamaha C40",
            "price_brl": 800.00,
            "stock_quantity": 5,
            "status": "active"
        },
        {
            "product_id": 2,
            "name": "Fender Stratocaster",
            "price_brl": 3500.00,
            "stock_quantity": 3,
            "status": "active"
        },
        {
            "product_id": 3,
            "name": "Casio CT-S200",
            "price_brl": 1200.00,
            "stock_quantity": 0,
            "status": "active"
        }
    ])

    promotions = pd.DataFrame([
        {
            "promotion_id": 1,
            "product_id": 1,
            "discount_percent": 10,
            "description": "Black Friday",
            "is_active": 1
        },
        {
            "promotion_id": 2,
            "product_id": 2,
            "discount_percent": 20,
            "description": "Winter Sale",
            "is_active": 0
        },
        {
            "promotion_id": 3,
            "product_id": 3,
            "discount_percent": 15,
            "description": "Special Offer",
            "is_active": 1
        }
    ])

    products.to_csv(tmp_path / "products.csv", index=False)
    promotions.to_csv(tmp_path / "promotions.csv", index=False)

    return PromotionRepository(tmp_path)


def test_get_active_promotions(repository):
    promotions = repository.get_active_promotions()

    assert len(promotions) == 1
    assert promotions[0]["name"] == "Yamaha C40"


def test_calculate_discount(repository):
    promotion = repository.get_product_promotion(1)

    assert promotion["original_price"] == 800.00
    assert promotion["final_price"] == 720.00


def test_ignore_inactive_promotions(repository):
    promotion = repository.get_product_promotion(2)

    assert promotion is None


def test_ignore_out_of_stock_products(repository):
    promotion = repository.get_product_promotion(3)

    assert promotion is None


def test_unknown_product(repository):
    promotion = repository.get_product_promotion(999)

    assert promotion is None
