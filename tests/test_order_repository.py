import pandas as pd
import pytest

from src.repositories.order_repository import OrderRepository


@pytest.fixture
def repository(tmp_path):
    customers = pd.DataFrame([
        {"customer_id": 1, "email": "ana@example.com"}
    ])

    orders = pd.DataFrame([
        {
            "order_id": 101,
            "customer_id": 1,
            "order_date": "2026-10-10",
            "status": "shipped",
            "total_brl": 599.90,
            "payment_method": "pix",
            "tracking_code": "BR123456789BR",
            "estimated_delivery": "2026-10-20"
        }
    ])

    products = pd.DataFrame([
        {"product_id": 81, "name": "Yamaha C40"}
    ])

    order_items = pd.DataFrame([
        {"order_id": 101, "product_id": 81, "quantity": 1}
    ])

    customers.to_csv(tmp_path / "customers.csv", index=False)
    orders.to_csv(tmp_path / "orders.csv", index=False)
    products.to_csv(tmp_path / "products.csv", index=False)
    order_items.to_csv(tmp_path / "order_items.csv", index=False)

    return OrderRepository(tmp_path)


def test_invalid_order_id(repository):
    assert repository.get_order(-1, "ana@example.com") is None


def test_missing_email(repository):
    assert repository.get_order(101, "") is None