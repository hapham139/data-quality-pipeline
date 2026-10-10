import pandas as pd

from src.quality_checks import split_by_quality
from src.transform import transform


def sample_rows() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "source_row": 2,
                "InvoiceNo": 536365,
                "StockCode": "85123A",
                "Description": "Product",
                "Quantity": 2,
                "InvoiceDate": "2010-12-01 08:26:00",
                "UnitPrice": 2.5,
                "CustomerID": 17850,
                "Country": "United Kingdom",
            },
            {
                "source_row": 3,
                "InvoiceNo": "C536366",
                "StockCode": "85123A",
                "Description": "Returned product",
                "Quantity": -1,
                "InvoiceDate": "2010-12-01 08:30:00",
                "UnitPrice": 2.5,
                "CustomerID": None,
                "Country": "United Kingdom",
            },
            {
                "source_row": 6,
                "InvoiceNo": 536369,
                "StockCode": "44444",
                "Description": "Returned product",
                "Quantity": -1,
                "InvoiceDate": "2010-12-01 08:35:00",
                "UnitPrice": 2.5,
                "CustomerID": 17850,
                "Country": "United Kingdom",
            },
            {
                "source_row": 4,
                "InvoiceNo": 536367,
                "StockCode": "22222",
                "Description": "Zero quantity",
                "Quantity": 0,
                "InvoiceDate": "2010-12-01 09:00:00",
                "UnitPrice": 1.0,
                "CustomerID": 13047,
                "Country": "United Kingdom",
            },
            {
                "source_row": 5,
                "InvoiceNo": 536368,
                "StockCode": "33333",
                "Description": "Invalid price",
                "Quantity": 1,
                "InvoiceDate": "2010-12-01 09:10:00",
                "UnitPrice": -1.0,
                "CustomerID": 13047,
                "Country": "United Kingdom",
            },
        ]
    )


def test_returns_are_classified_and_missing_customer_is_allowed() -> None:
    normalized = transform(sample_rows())
    valid, rejected = split_by_quality(normalized)

    assert len(valid) == 3
    assert rejected["source_row"].tolist() == [4, 5]
    cancellation = valid.loc[valid["invoice_no"] == "C536366"].iloc[0]
    assert cancellation["transaction_type"] == "cancellation"
    assert pd.isna(cancellation["customer_id"])
    returned = valid.loc[valid["invoice_no"] == "536369"].iloc[0]
    assert returned["transaction_type"] == "return"


def test_invalid_quantity_and_price_are_quarantined() -> None:
    normalized = transform(sample_rows())
    _, rejected = split_by_quality(normalized)

    issues_by_row = rejected.set_index("source_row")["quality_issues"]
    assert issues_by_row.loc[4] == "invalid_quantity"
    assert issues_by_row.loc[5] == "invalid_unit_price"


def test_duplicate_rows_are_quarantined() -> None:
    rows = sample_rows().iloc[[0, 0]].copy()
    rows.iloc[1, rows.columns.get_loc("source_row")] = 99
    _, rejected = split_by_quality(transform(rows))

    assert rejected["source_row"].tolist() == [99]
    assert rejected.iloc[0]["quality_issues"] == "duplicate_record"