
import pandas as pd
import pytest

from src.repositories.product_repository import ProductRepository


@pytest.fixture
def repository(tmp_path):
    """Create an isolated product catalog for testing."""

    products = pd.DataFrame([
        {
            "product_id": 1,
            "name": "Yamaha C40",
            "category_id": 5,
            "price_brl": 599.90,
            "stock_quantity": 12,
            "status": "active",
        },
        {
            "product_id": 2,
            "name": "Takamine GD20",
            "category_id": 5,
            "price_brl": 1800.00,
            "stock_quantity": 0,
            "status": "active",
        },
        {
            "product_id": 3,
            "name": "Fender Stratocaster",
            "category_id": 1,
            "price_brl": 4500.00,
            "stock_quantity": 3,
            "status": "active",
        },
    ])

    categories = pd.DataFrame([
        {"category_id": 1, "name": "Guitarras"},
        {"category_id": 5, "name": "Violões"},
    ])

    products.to_csv(tmp_path / "products.csv", index=False)
    categories.to_csv(tmp_path / "categories.csv", index=False)

    return ProductRepository(data_dir=tmp_path)


def test_search_products_by_name(repository):
    results = repository.search_products(name="Yamaha")

    assert len(results) == 1
    assert results[0]["name"] == "Yamaha C40"


def test_search_products_by_category_and_price(repository):
    results = repository.search_products(
        category="Violões",
        max_price=1000,
    )

    assert len(results) == 1
    assert results[0]["price_brl"] <= 1000


def test_out_of_stock_products_are_excluded(repository):
    results = repository.search_products(name="Takamine")

    assert results == []


def test_search_includes_unavailable_products(repository):
    results = repository.search_products(
        name="Takamine",
        available_only=False,
    )

    assert len(results) == 1
    assert results[0]["stock_quantity"] == 0


def test_get_product_by_id(repository):
    product = repository.get_product_by_id(1)

    assert product is not None
    assert product["name"] == "Yamaha C40"


def test_unknown_product_returns_none(repository):
    assert repository.get_product_by_id(999) is None


def test_negative_price_filter_raises_error(repository):
    with pytest.raises(ValueError):
        repository.search_products(max_price=-100)


def test_invalid_limit_raises_error(repository):
    with pytest.raises(ValueError):
        repository.search_products(limit=0)
