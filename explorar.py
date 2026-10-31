
from pathlib import Path
import pandas as pd


# Directory containing the store datasets
DATA_DIR = Path(__file__).resolve().parent / "data"

# Available CSV datasets
CSV_FILES = [
    "categories.csv",
    "customers.csv",
    "order_items.csv",
    "orders.csv",
    "products.csv",
    "promotions.csv",
]


def explore_dataset(file_name: str) -> None:
    """
    Load and inspect a CSV dataset.

    Displays dataset dimensions, column names,
    missing values, duplicate rows, and sample records.
    """

    file_path = DATA_DIR / file_name

    print(f"\n{'=' * 60}")
    print(f"DATASET: {file_name}")
    print(f"{'=' * 60}")

    try:
        df = pd.read_csv(file_path)

        # Dataset dimensions
        rows, columns = df.shape

        print(f"\nRows: {rows}")
        print(f"Columns: {columns}")

        # Column names and data types
        print("\nCOLUMN INFORMATION:")
        print(df.dtypes.to_string())

        # Missing values
        print("\nMISSING VALUES:")
        print(df.isnull().sum().to_string())

        # Duplicate records
        print("\nDUPLICATE ROWS:")
        print(df.duplicated().sum())

        # Sample records
        print("\nFIRST FIVE RECORDS:")
        print(df.head(5).to_string(index=False))

    except FileNotFoundError:
        print(f"ERROR: File not found: {file_path}")

    except pd.errors.EmptyDataError:
        print(f"ERROR: Dataset {file_name} is empty.")

    except pd.errors.ParserError as error:
        print(f"ERROR: Could not parse {file_name}: {error}")


def main() -> None:
    """
    Run exploratory analysis for all available datasets.
    """

    print("EMPORIO DA MUSICA - DATA EXPLORATION")

    for file_name in CSV_FILES:
        explore_dataset(file_name)

    print("\nData exploration completed.")


if __name__ == "__main__":
    main()
