
from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_datasets() -> dict[str, pd.DataFrame]:
    """Load the datasets required for validation."""

    files = [
        "categories",
        "customers",
        "products",
        "orders",
        "order_items",
        "promotions",
    ]

    datasets = {}

    for name in files:
        file_path = DATA_DIR / f"{name}.csv"
        datasets[name] = pd.read_csv(file_path)

    return datasets


def validate_primary_keys(
    datasets: dict[str, pd.DataFrame],
) -> list[str]:
    """Check missing and duplicated primary keys."""

    primary_keys = {
        "categories": "category_id",
        "customers": "customer_id",
        "products": "product_id",
        "orders": "order_id",
        "promotions": "promotion_id",
    }

    errors = []

    for table, key in primary_keys.items():
        df = datasets[table]

        if df[key].isna().any():
            errors.append(
                f"{table}: null values found in {key}"
            )

        if df[key].duplicated().any():
            errors.append(
                f"{table}: duplicated primary keys in {key}"
            )

    return errors


def validate_foreign_keys(
    datasets: dict[str, pd.DataFrame],
) -> list[str]:
    """Check referential integrity between datasets."""

    relationships = [
        ("products", "category_id", "categories", "category_id"),
        ("orders", "customer_id", "customers", "customer_id"),
        ("order_items", "order_id", "orders", "order_id"),
        ("order_items", "product_id", "products", "product_id"),
        ("promotions", "product_id", "products", "product_id"),
    ]

    errors = []

    for source, foreign_key, target, primary_key in relationships:
        invalid = datasets[source][
            ~datasets[source][foreign_key].isin(
                datasets[target][primary_key]
            )
        ]

        if not invalid.empty:
            errors.append(
                f"{source}.{foreign_key}: "
                f"{len(invalid)} invalid references to {target}"
            )

    return errors


def validate_business_rules(
    datasets: dict[str, pd.DataFrame],
) -> list[str]:
    """Validate numeric constraints and business rules."""

    errors = []

    products = datasets["products"]
    orders = datasets["orders"]
    order_items = datasets["order_items"]
    promotions = datasets["promotions"]

    if (products["price_brl"] < 0).any():
        errors.append("products: negative prices found")

    if (products["stock_quantity"] < 0).any():
        errors.append("products: negative stock quantities found")

    if (orders["total_brl"] < 0).any():
        errors.append("orders: negative order totals found")

    if (order_items["quantity"] <= 0).any():
        errors.append("order_items: invalid quantities found")

    if (
        ~promotions["discount_percent"].between(0, 100)
    ).any():
        errors.append("promotions: invalid discount percentages")

    if (~promotions["is_active"].isin([0, 1])).any():
        errors.append("promotions: invalid activation flags")

    return errors


def main() -> None:
    """Execute dataset integrity checks."""

    print("EMPORIO DA MUSICA - DATA VALIDATION")
    print("=" * 50)

    try:
        datasets = load_datasets()

        checks = {
            "Primary key validation": validate_primary_keys,
            "Foreign key validation": validate_foreign_keys,
            "Business rule validation": validate_business_rules,
        }

        total_errors = 0

        for name, validator in checks.items():
            errors = validator(datasets)

            if errors:
                print(f"\n[FAIL] {name}")

                for error in errors:
                    print(f"  - {error}")

                total_errors += len(errors)
            else:
                print(f"\n[PASS] {name}")

        print("\n" + "=" * 50)
        print(f"Validation completed: {total_errors} errors found.")

        if total_errors:
            raise SystemExit(1)

    except (FileNotFoundError, pd.errors.ParserError) as error:
        print(f"\n[ERROR] Unable to load datasets: {error}")
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
