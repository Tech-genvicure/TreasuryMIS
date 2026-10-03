import os
from contextlib import contextmanager

import psycopg
from dotenv import load_dotenv
from psycopg.rows import dict_row
from psycopg import sql

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

TABLES = {
    "funds": {
        "table": "funds_position",
        "fields": [
            "company_name", "bank_name", "account_no", "balance_inr",
            "balance_usd", "inr_equivalent", "entity_type"
        ],
        "numeric": {"balance_inr", "balance_usd", "inr_equivalent"},
        "dates": set(),
    },
    "payables": {
        "table": "payables",
        "fields": [
            "tracker_serial_no", "cost_for_project", "status_payment_processed",
            "payment_cycle", "payer_company", "branch",
            "approved_vendor_management", "approval_date",
            "vendor_name", "product_service", "pass_through_bill",
            "invoice_ref", "invoice_date", "due_date",
            "transaction_posting_date", "amount_payable", "due_date2",
            "payment_status", "bank_account_number", "ifsc_code",
            "bank_branch", "remarks", "timeline_bucket"
        ],
        "numeric": {"tracker_serial_no", "amount_payable"},
        "dates": {"approval_date", "invoice_date", "due_date",
                  "transaction_posting_date", "due_date2"},
    },
    "receivables": {
        "table": "receivables",
        "fields": [
            "source_ref", "cost_for_project", "status_payment_processed",
            "receipt_cycle", "receiver_company", "branch",
            "approved_vendor_management", "approval_date",
            "vendor_name", "product_service", "pass_through_bill",
            "invoice_ref", "invoice_date", "due_date",
            "transaction_posting_date", "amount_receivable", "due_date2",
            "payment_status", "bank_account_number", "ifsc_code",
            "bank_branch", "remarks", "timeline_bucket"
        ],
        "numeric": {"amount_receivable"},
        "dates": {"approval_date", "invoice_date", "due_date",
                  "transaction_posting_date", "due_date2"},
    },
    "borrowings": {
        "table": "borrowings",
        "fields": ["sanctioned", "disbursed", "outstanding"],
        "numeric": {"sanctioned", "disbursed", "outstanding"},
        "dates": set(),
    },
}

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(30) NOT NULL DEFAULT 'FINANCE'
);

CREATE TABLE IF NOT EXISTS funds_position (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    company_name TEXT NOT NULL,
    bank_name TEXT,
    account_no TEXT,
    balance_inr NUMERIC(18,2),
    balance_usd NUMERIC(18,2),
    inr_equivalent NUMERIC(18,2),
    entity_type TEXT
);

CREATE TABLE IF NOT EXISTS payables (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    tracker_serial_no INTEGER,
    cost_for_project TEXT,
    status_payment_processed TEXT,
    payment_cycle TEXT,
    payer_company TEXT,
    branch TEXT,
    approved_vendor_management TEXT,
    approval_date DATE,
    vendor_name TEXT,
    product_service TEXT,
    pass_through_bill TEXT,
    invoice_ref TEXT,
    invoice_date DATE,
    due_date DATE,
    transaction_posting_date DATE,
    amount_payable NUMERIC(18,2),
    due_date2 DATE,
    payment_status TEXT,
    bank_account_number TEXT,
    ifsc_code TEXT,
    bank_branch TEXT,
    remarks TEXT,
    timeline_bucket TEXT
);

CREATE TABLE IF NOT EXISTS receivables (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    source_ref TEXT,
    cost_for_project TEXT,
    status_payment_processed TEXT,
    receipt_cycle TEXT,
    receiver_company TEXT,
    branch TEXT,
    approved_vendor_management TEXT,
    approval_date DATE,
    vendor_name TEXT,
    product_service TEXT,
    pass_through_bill TEXT,
    invoice_ref TEXT,
    invoice_date DATE,
    due_date DATE,
    transaction_posting_date DATE,
    amount_receivable NUMERIC(18,2),
    due_date2 DATE,
    payment_status TEXT,
    bank_account_number TEXT,
    ifsc_code TEXT,
    bank_branch TEXT,
    remarks TEXT,
    timeline_bucket TEXT
);

CREATE TABLE IF NOT EXISTS borrowings (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    sanctioned NUMERIC(18,2) NOT NULL DEFAULT 0,
    disbursed NUMERIC(18,2) NOT NULL DEFAULT 0,
    outstanding NUMERIC(18,2) NOT NULL DEFAULT 0
);
"""

@contextmanager
def get_conn():
    if not DATABASE_URL:
        raise RuntimeError("DATABASE_URL is not configured.")
    with psycopg.connect(DATABASE_URL, row_factory=dict_row) as conn:
        yield conn

def init_db():
    with get_conn() as conn:
        conn.execute(CREATE_SQL)
        conn.commit()

def fetch_rows(key):
    meta = TABLES[key]
    with get_conn() as conn:
        return conn.execute(
            sql.SQL("SELECT id, {} FROM {} ORDER BY id").format(
                sql.SQL(", ").join(map(sql.Identifier, meta["fields"])),
                sql.Identifier(meta["table"]),
            )
        ).fetchall()

def _clean_value(key, field, value):
    meta = TABLES[key]
    if value in ("", None):
        return None
    if field in meta["numeric"]:
        return float(value)
    return value

def insert_row(key, data):
    meta = TABLES[key]
    clean = {f: _clean_value(key, f, data.get(f)) for f in meta["fields"]}
    cols = [f for f in meta["fields"] if clean[f] is not None]
    vals = [clean[f] for f in cols]
    if not cols:
        raise ValueError("At least one value is required.")
    with get_conn() as conn:
        row = conn.execute(
            sql.SQL("INSERT INTO {} ({}) VALUES ({}) RETURNING id").format(
                sql.Identifier(meta["table"]),
                sql.SQL(", ").join(map(sql.Identifier, cols)),
                sql.SQL(", ").join(sql.Placeholder() for _ in cols),
            ),
            vals,
        ).fetchone()
        conn.commit()
        return row["id"]

def update_row(key, row_id, data):
    meta = TABLES[key]
    clean = {f: _clean_value(key, f, data.get(f)) for f in meta["fields"]}
    assignments = [
        sql.SQL("{} = {}").format(sql.Identifier(f), sql.Placeholder())
        for f in meta["fields"]
    ]
    values = [clean[f] for f in meta["fields"]] + [row_id]
    with get_conn() as conn:
        conn.execute(
            sql.SQL("UPDATE {} SET {} WHERE id = {}").format(
                sql.Identifier(meta["table"]),
                sql.SQL(", ").join(assignments),
                sql.Placeholder(),
            ),
            values,
        )
        conn.commit()

def delete_row(key, row_id):
    meta = TABLES[key]
    with get_conn() as conn:
        conn.execute(
            sql.SQL("DELETE FROM {} WHERE id = {}").format(
                sql.Identifier(meta["table"]), sql.Placeholder()
            ),
            (row_id,),
        )
        conn.commit()

def dashboard_data():
    with get_conn() as conn:
        funds = conn.execute(
            "SELECT COALESCE(SUM(inr_equivalent),0) AS total FROM funds_position"
        ).fetchone()["total"]
        payables = conn.execute(
            """SELECT COALESCE(SUM(amount_payable),0) AS total
               FROM payables
               WHERE LOWER(COALESCE(payment_status,'')) NOT LIKE 'paid%'"""
        ).fetchone()["total"]
        receivables = conn.execute(
            """SELECT COALESCE(SUM(amount_receivable),0) AS total
               FROM receivables
               WHERE LOWER(COALESCE(payment_status,'')) NOT LIKE 'paid%'"""
        ).fetchone()["total"]
        borrowing = conn.execute(
            """SELECT sanctioned, disbursed, outstanding
               FROM borrowings ORDER BY id LIMIT 1"""
        ).fetchone() or {"sanctioned": 0, "disbursed": 0, "outstanding": 0}

        funds_breakdown = conn.execute(
            """SELECT COALESCE(bank_name,'Unknown') AS name,
                      COALESCE(inr_equivalent,0) AS amount,
                      COALESCE(entity_type,'Other') AS entity_type
               FROM funds_position
               ORDER BY amount DESC"""
        ).fetchall()

        vendors = conn.execute(
            """SELECT COALESCE(vendor_name,'Unspecified') AS name,
                      COALESCE(SUM(amount_payable),0) AS amount
               FROM payables
               WHERE LOWER(COALESCE(payment_status,'')) NOT LIKE 'paid%'
               GROUP BY vendor_name
               ORDER BY amount DESC
               LIMIT 10"""
        ).fetchall()

        cash_flow = conn.execute(
            """WITH p AS (
                 SELECT COALESCE(timeline_bucket,'Unspecified') bucket,
                        COALESCE(SUM(amount_payable),0) amount
                 FROM payables
                 WHERE LOWER(COALESCE(payment_status,'')) NOT LIKE 'paid%'
                 GROUP BY timeline_bucket
               ),
               r AS (
                 SELECT COALESCE(timeline_bucket,'Unspecified') bucket,
                        COALESCE(SUM(amount_receivable),0) amount
                 FROM receivables
                 WHERE LOWER(COALESCE(payment_status,'')) NOT LIKE 'paid%'
                 GROUP BY timeline_bucket
               )
               SELECT COALESCE(p.bucket,r.bucket) AS bucket,
                      COALESCE(p.amount,0) AS payables,
                      COALESCE(r.amount,0) AS receivables
               FROM p FULL OUTER JOIN r ON p.bucket=r.bucket"""
        ).fetchall()

    return {
        "funds": float(funds or 0),
        "payables": float(payables or 0),
        "receivables": float(receivables or 0),
        "borrowing": {k: float(v or 0) for k, v in borrowing.items()},
         "funds_breakdown": [
            {"name": x["name"], "amount": float(x["amount"] or 0), "entity_type": x["entity_type"]}
            for x in funds_breakdown
        ],
        "vendors": [
            {"name": x["name"], "amount": float(x["amount"] or 0)}
            for x in vendors
        ],
        "cash_flow": [
            {"bucket": x["bucket"], "payables": float(x["payables"] or 0),
             "receivables": float(x["receivables"] or 0)}
            for x in cash_flow
        ],
    }
