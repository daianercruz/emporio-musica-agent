
from pathlib import Path
import re
import unicodedata

import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def normalize_text(value: str) -> str:
    text = unicodedata.normalize("NFKD", str(value))
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    return re.sub(r"\s+", " ", text.casefold()).strip()


def normalize_category(value: str) -> str:
    text = normalize_text(value)

    words = []

    for word in text.split():
        if word.endswith("oes"):
            word = word[:-3] + "ao"
        elif word.endswith("ais"):
            word = word[:-3] + "al"
        elif word.endswith("res"):
            word = word[:-1]
        elif word.endswith("s") and not word.endswith("ss"):
            word = word[:-1]

        words.append(word)

    return " ".join(words)


class ProductRepository:
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
        if max_price is not None and max_price < 0:
            raise ValueError("Maximum price cannot be negative.")

        if not 1 <= limit <= 50:
            raise ValueError("Limit must be between 1 and 50.")

        results = self.catalog.copy()

        if name:
            normalized_name = normalize_text(name)

            results = results[
                results["name"].apply(
                    lambda value: normalized_name in normalize_text(value)
                )
            ]

        if category:
            normalized_category = normalize_category(category)

            results = results[
                results["category_name"].apply(
                    lambda value: normalized_category
                    in normalize_category(value)
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
        results = self.catalog[
            self.catalog["product_id"] == product_id
        ]

        if results.empty:
            return None

        return results.iloc[0].to_dict()
