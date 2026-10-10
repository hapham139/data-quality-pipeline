import pandas as pd


DUPLICATE_KEY = ["InvoiceNo", "StockCode", "InvoiceDate", "Quantity", "UnitPrice"]


def split_by_quality(frame: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    checked = frame.copy().reset_index(drop=True)
    checks = [
        (
            "missing_required_field",
            checked[
                ["InvoiceNo", "StockCode", "InvoiceDate", "Country"]
            ].isna().any(axis=1),
        ),
        (
            "invalid_quantity",
            checked["Quantity"].isna()
            | checked["Quantity"].eq(0)
            | checked["Quantity"].mod(1).ne(0),
        ),
        (
            "invalid_unit_price",
            checked["UnitPrice"].isna() | checked["UnitPrice"].lt(0),
        ),
        (
            "duplicate_record",
            checked.duplicated(subset=DUPLICATE_KEY, keep="first"),
        ),
    ]

    checked["quality_issues"] = ""
    for issue, failed_rows in checks:
        checked.loc[failed_rows.fillna(False), "quality_issues"] += issue + ";"
    checked["quality_issues"] = checked["quality_issues"].str.rstrip(";")
    rejected_mask = checked["quality_issues"].ne("")

    rejected_columns = [
        "source_row",
        "InvoiceNo",
        "StockCode",
        "Description",
        "Quantity",
        "InvoiceDate",
        "UnitPrice",
        "CustomerID",
        "Country",
        "quality_issues",
    ]
    rejected = checked.loc[rejected_mask, rejected_columns].copy()

    valid = checked.loc[~rejected_mask].copy()
    valid["Quantity"] = valid["Quantity"].astype("int64")
    valid["transaction_type"] = "sale"
    valid.loc[valid["Quantity"] < 0, "transaction_type"] = "return"
    valid.loc[
        valid["InvoiceNo"].str.startswith("C", na=False), "transaction_type"
    ] = "cancellation"
    valid["line_total"] = valid["Quantity"] * valid["UnitPrice"]
    valid = valid.rename(
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
    valid = valid[
        [
            "source_row",
            "invoice_no",
            "stock_code",
            "description",
            "quantity",
            "invoice_date",
            "unit_price",
            "customer_id",
            "country",
            "transaction_type",
            "line_total",
        ]
    ]
    return valid, rejected