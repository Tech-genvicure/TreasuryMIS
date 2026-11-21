from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path


import pandas as pd
from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models import (
    FundPosition,
    Payable,
    Borrowing,
    Receivable,
)


EXCEL_FILE = Path(__file__).resolve().parents[3] / "Treasury_Master.xlsx"


def clean_string(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if not value:
        return None

    return value


def clean_decimal(value):
    if pd.isna(value):
        return None

    try:
        if isinstance(value, str):
            value = (
                value.replace(",", "")
                .replace("₹", "")
                .strip()
            )

            if not value:
                return None

        return Decimal(str(value))

    except (ValueError, TypeError, InvalidOperation):
        return None


def clean_int(value):
    if pd.isna(value):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


def clean_date(value):
    if pd.isna(value):
        return None

    try:
        return pd.to_datetime(value, dayfirst=True).date()
    except (ValueError, TypeError):
        return None


def import_fund_positions(db):
    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Funds_Position",
    )

    records = []

    for _, row in df.iterrows():
        records.append(
            FundPosition(
                company_name=clean_string(row["Name of Company"]),
                bank_name=clean_string(row["Bank Name "]),
                account_no=clean_string(row["Account No."]),
                balance_inr=clean_decimal(row["Balance (INR)"]),
                balance_usd=clean_decimal(row["Balance (USD)"]),
                inr_equivalent=clean_decimal(row["INR Equivalent"]),
                entity_type=clean_string(row["Entity Type"]),
            )
        )

    db.add_all(records)

    print(f"Imported {len(records)} fund position records.")


def import_payables(db):
    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Payables",
    )

    records = []

    for _, row in df.iterrows():
        records.append(
            Payable(
                tracker_serial_no=clean_int(row["Tracker Serial No."]),
                cost_for_project=clean_string(row["Cost For Project"]),
                payment_processed=clean_string(
                    row["Status Payment processed [Y/N]"]
                ),
                payment_cycle=clean_string(row["Payment Cycle"]),
                payer_company=clean_string(row["Payer Company"]),
                branch=clean_string(row["Branch"]),
                approved_in_vendor_management=clean_string(
                    row["Approved IN Vendor Management Software?"]
                ),
                approval_date=clean_date(row["Approval Date"]),
                vendor_name_expense_name=clean_string(
                    row["Vendor Name/ Expense Name"]
                ),
                product_service=clean_string(row["Product/Service"]),
                pass_through_bill=clean_string(
                    row["Whether Pass Through Bill"]
                ),
                invoice_ref=clean_string(row["Against Invoice Ref."]),
                invoice_date=clean_date(row["Invoice Date"]),
                due_date=clean_date(row["Due Date"]),
                transaction_posting_date=clean_date(
                    row["Transaction Posting Date"]
                ),
                amount_payable=clean_decimal(row["Amount Payable"]),
                due_date_2=clean_date(row["Due Date2"]),
                payment_status=clean_string(
                    row["Payment Status Paid/ Not paid"]
                ),
                bank_account_number=clean_string(
                    row["Bank Account Number"]
                ),
                ifsc_code=clean_string(row["IFSC CODE"]),
                bank_branch=clean_string(row["Bank Branch"]),
                remarks=clean_string(row["Remarks"]),
                timeline_bucket=clean_string(row["Timeline_Bucket"]),
            )
        )

    db.add_all(records)

    print(f"Imported {len(records)} payable records.")


def import_borrowings(db):
    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Borrowinig",
    )

    # The sheet represents the borrowing summary.
    # Store one current snapshot row.
    if df.empty:
        print("No borrowing data found.")
        return

    row = df.iloc[0]

    record = Borrowing(
        sanctioned=clean_decimal(row["Sanctioned"]) or Decimal("0"),
        disbursed=clean_decimal(row["Disbersed"]) or Decimal("0"),
        outstanding=clean_decimal(row["Outstanding"]) or Decimal("0"),
    )

    db.add(record)

    print("Imported borrowing summary.")


def import_receivables(db):
    df = pd.read_excel(
        EXCEL_FILE,
        sheet_name="Receivables",
    )

    records = []

    for _, row in df.iterrows():
        records.append(
            Receivable(
                cost_for_project=clean_string(row["Cost For Project"]),
                payment_processed=clean_string(
                    row["Status Payment processed [Y/N]"]
                ),
                receipt_cycle=clean_string(row["Receipt Cycle"]),
                receiver_company=clean_string(row["Receiver Company"]),
                branch=clean_string(row["Branch"]),
                approved_in_vendor_management=clean_string(
                    row["Approved IN Vendor Management Software?"]
                ),
                approval_date=clean_date(row["Approval Date"]),
                vendor_name_income_name=clean_string(
                    row["Vendor Name/ Income Name"]
                ),
                product_service=clean_string(row["Product/Service"]),
                pass_through_bill=clean_string(
                    row["Whether Pass Through Bill"]
                ),
                invoice_ref=clean_string(row["Against Invoice Ref."]),
                invoice_date=clean_date(row["Invoice Date"]),
                due_date=clean_date(row["Due Date"]),
                transaction_posting_date=clean_date(
                    row["Transaction Posting Date"]
                ),
                amount_receivable=clean_decimal(
                    row["Amount Receivable"]
                ),
                due_date_2=clean_date(row["Due Date2"]),
                payment_status=clean_string(
                    row["Payment Status Paid/ Not paid"]
                ),
                bank_account_number=clean_string(
                    row["Bank Account Number"]
                ),
                ifsc_code=clean_string(row["IFSC CODE"]),
                bank_branch=clean_string(row["Bank Branch"]),
                remarks=clean_string(row["Remarks"]),
                timeline_bucket=clean_string(row["Timline_Bucket"]),
            )
        )

    db.add_all(records)

    print(f"Imported {len(records)} receivable records.")


def main():
    print("=" * 60)
    print("Genvicure Treasury MIS - Initial Data Import")
    print("=" * 60)

    if not EXCEL_FILE.exists():
        raise FileNotFoundError(
            f"Treasury_Master.xlsx not found at: {EXCEL_FILE}"
        )

    print(f"Source file: {EXCEL_FILE}")

    db = SessionLocal()

    try:
        # This is an initial import.
        # Clear existing data so the script can safely be rerun.
        db.execute(delete(FundPosition))
        db.execute(delete(Payable))
        db.execute(delete(Borrowing))
        db.execute(delete(Receivable))

        import_fund_positions(db)
        import_payables(db)
        import_borrowings(db)
        import_receivables(db)

        db.commit()

        print("=" * 60)
        print("IMPORT COMPLETED SUCCESSFULLY")
        print("=" * 60)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()