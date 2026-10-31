
from pathlib import Path

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class ProductRepository:
    """Provide read-only access to the product catalog."""

    def __init__(self, data_dir: Path = DATA_DIR) -> None:
        self.data_dir = Path(data_dir)
        self.products = pd.read_csv(self.data_dir / "products.csv")
        self.categories = pd.read_csv(self.data_dir / "categories.csv")

        self.catalog = self.products.merge(
            self.categories[["category_id", "name"]],
            on="category_id",
            how="left",
            validate="many_to_one",
            suffixes=("", "_category"),
        ).rename(columns={"name_category": "category_name"})

    def search_products(
        self,
        name: str | None = None,
        category: str | None = None,
        max_price: float | None = None,
        available_only: bool = True,
        limit: int = 10,
    ) -> list[dict]:
        """Search products using optional filters."""

        if max_price is not None and max_price < 0:
            raise ValueError("Maximum price cannot be negative.")

        if not 1 <= limit <= 50:
            raise ValueError("Limit must be between 1 and 50.")

        results = self.catalog.copy()

        if name:
            results = results[
                results["name"].str.contains(
                    name,
                    case=False,
                    regex=False,
                    na=False,
                )
            ]

        if category:
            results = results[
                results["category_name"].str.contains(
                    category,
                    case=False,
                    regex=False,
                    na=False,
                )
            ]

        if max_price is not None:
            results = results[
                results["price_brl"] <= max_price
            ]

        if available_only:
            results = results[
                (results["status"] == "active")
                & (results["stock_quantity"] > 0)
            ]

        results = results.sort_values(
            by=["price_brl", "product_id"]
        ).head(limit)

        columns = [
            "product_id",
            "name",
            "category_name",
            "price_brl",
            "stock_quantity",
            "status",
        ]

        return results[columns].to_dict(orient="records")

    def get_product_by_id(self, product_id: int) -> dict | None:
        """Return a product by its unique identifier."""

        results = self.catalog[
            self.catalog["product_id"] == product_id
        ]

        if results.empty:
            return None

        return results.iloc[0].to_dict()
