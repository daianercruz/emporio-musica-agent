
from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


class OrderRepository:

    def __init__(self, data_dir=DATA_DIR):
        self.orders = pd.read_csv(data_dir / "orders.csv")
        self.customers = pd.read_csv(data_dir / "customers.csv")
        self.order_items = pd.read_csv(data_dir / "order_items.csv")
        self.products = pd.read_csv(data_dir / "products.csv")

    def get_order(self, order_id: int, customer_email: str):

        if order_id <= 0 or not customer_email.strip():
            return None

        order = self.orders[self.orders["order_id"] == order_id]

        if order.empty:
            return None

        order = order.iloc[0]

        customer = self.customers[
            self.customers["customer_id"] == order["customer_id"]
        ]

        if customer.empty:
            return None

        email = customer.iloc[0]["email"]

        if email.strip().lower() != customer_email.strip().lower():
            return None

        items = self.order_items[
            self.order_items["order_id"] == order_id
        ]

        items = items.merge(
            self.products[["product_id", "name"]],
            on="product_id",
            how="left"
        )

        products = []

        for _, item in items.iterrows():
            products.append({
                "product_id": int(item["product_id"]),
                "name": item["name"] if pd.notna(item["name"]) else None,
                "quantity": int(item["quantity"])
            })

        tracking_code = order["tracking_code"]
        estimated_delivery = order["estimated_delivery"]

        return {
            "order_id": int(order["order_id"]),
            "status": order["status"],
            "order_date": order["order_date"],
            "total_brl": float(order["total_brl"]),
            "payment_method": order["payment_method"],
            "tracking_code": tracking_code if pd.notna(tracking_code) else None,
            "estimated_delivery": estimated_delivery if pd.notna(estimated_delivery) else None,
            "items": products
        }
