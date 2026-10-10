import pandas as pd


def _clean_text(series: pd.Series) -> pd.Series:
    cleaned = series.astype("string").str.strip()
    return cleaned.mask(cleaned.eq(""))


def _clean_identifier(series: pd.Series) -> pd.Series:
    cleaned = _clean_text(series)
    return cleaned.str.replace(r"\.0$", "", regex=True)


def transform(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()

    for column in ("InvoiceNo", "StockCode", "CustomerID"):
        result[column] = _clean_identifier(result[column])

    for column in ("Description", "Country"):
        result[column] = _clean_text(result[column])

    result["InvoiceDate"] = pd.to_datetime(result["InvoiceDate"], errors="coerce")
    result["Quantity"] = pd.to_numeric(result["Quantity"], errors="coerce")
    result["UnitPrice"] = pd.to_numeric(result["UnitPrice"], errors="coerce")
    return result