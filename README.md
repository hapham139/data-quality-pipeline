# Online Retail Data Quality Pipeline

A Phon project that reads the Online Retail Excel file,
checks its rows, and saves the results in PostgreSQL.

## What it does

1. Reads `data/Online Retail.xlsx`.
2. Cleans text, dates, and numeric values.
3. Checks required fields, quantities, prices, and duplicate rows.
4. Saves good rows to `retail_transactions` and problem rows to
   `quarantined_records` in PostgreSQL.

Returns and cancellations are kept and labeled, not discarded. Missing
`CustomerID` is allowed.

## Run on Windows PowerShell

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
docker compose up -d db
python -m src.pipeline
```

Keep the workbook at `data/Online Retail.xlsx`. Docker starts a local PostgreSQL
database with the development credentials configured in `docker-compose.yml`.
The pipeline replaces its two tables each time it runs.

Stop the database with `docker compose down`.

## Run tests

```powershell
pytest
```