from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

from src.quality_checks import split_by_quality
from src.transform import transform


ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / "data" / "Online Retail.xlsx"
DATABASE_URL = "postgresql+psycopg2://retail:retail@localhost:5434/retail"


def run_pipeline() -> None:
    print(f"Reading {DATA_FILE}")
    raw = pd.read_excel(DATA_FILE, sheet_name=0, engine="calamine")
    raw.columns = [str(column).strip() for column in raw.columns]
    raw.insert(0, "source_row", range(2, len(raw) + 2))

    cleaned = transform(raw)
    valid, rejected = split_by_quality(cleaned)
    rejected = rejected.rename(
        columns={
            "InvoiceNo": "invoice_no",
            "StockCode": "stock_code",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "UnitPrice": "unit_price",
            "CustomerID": "customer_id",
            "Country": "country",
        }
    )

    engine = create_engine(DATABASE_URL)
    with engine.begin() as connection:
        valid.to_sql("retail_transactions", connection, if_exists="replace", index=False)
        rejected.to_sql("quarantined_records", connection, if_exists="replace", index=False)
    engine.dispose()

    print(f"Rows read: {len(raw)}")
    print(f"Rows loaded: {len(valid)}")
    print(f"Rows quarantined: {len(rejected)}")
    print("Tables saved to PostgreSQL")


if __name__ == "__main__":
    run_pipeline()