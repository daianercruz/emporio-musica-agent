
from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class PromotionRepository:

    def __init__(self, data_dir=DATA_DIR):
        self.promotions = pd.read_csv(data_dir / "promotions.csv")
        self.products = pd.read_csv(data_dir / "products.csv")

    def get_active_promotions(self):
        active = self.promotions[
            self.promotions["is_active"] == 1
        ]

        results = active.merge(
            self.products,
            on="product_id",
            how="inner",
            suffixes=("_promotion", "_product")
        )

        results = results[
            (results["status"] == "active") &
            (results["stock_quantity"] > 0)
        ]

        promotions = []

        for _, item in results.iterrows():
            original_price = float(item["price_brl"])
            discount = float(item["discount_percent"])
            final_price = round(
                original_price * (1 - discount / 100),
                2
            )

            promotions.append({
                "promotion_id": int(item["promotion_id"]),
                "product_id": int(item["product_id"]),
                "name": item["name"],
                "description": item["description_promotion"],
                "original_price": original_price,
                "discount_percent": discount,
                "final_price": final_price
            })

        return promotions

    def get_product_promotion(self, product_id: int):
        promotions = self.get_active_promotions()

        for promotion in promotions:
            if promotion["product_id"] == product_id:
                return promotion

        return None
