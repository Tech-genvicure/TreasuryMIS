
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from io import BytesIO

from openpyxl import load_workbook

from app.services.microsoft_graph import download_treasury_workbook


EXPECTED_HEADERS = {
    "Funds_Position": [
        "Name of Company",
        "Bank Name",
        "Account No.",
        "Balance (INR)",
        "Balance (USD)",
        "INR Equivalent",
        "Entity Type",
    ],
    "Payables": [
        "Tracker Serial No.",
        "Cost For Project",
        "Status Payment processed [Y/N]",
        "Payment Cycle",
        "Payer Company",
        "Branch",
        "Approved IN Vendor Management Software?",
        "Approval Date",
        "Vendor Name/ Expense Name",
        "Product/Service",
        "Whether Pass Through Bill",
        "Against Invoice Ref.",
        "Invoice Date",
        "Due Date",
        "Transaction Posting Date",
        "Amount Payable",
        "Due Date2",
        "Payment Status Paid/ Not paid",
        "Bank Account Number",
        "IFSC CODE",
        "Bank Branch",
        "Remarks",
        "Timeline_Bucket",
    ],
    "Borrowing": [
        "Sanctioned",
        "Disbersed",
        "Outstanding",
    ],
    "Receivables": [
        "hoi",
        "Cost For Project",
        "Status Payment processed [Y/N]",
        "Receipt Cycle",
        "Receiver Company",
        "Branch",
        "Approved IN Vendor Management Software?",
        "Approval Date",
        "Vendor Name/ Income Name",
        "Product/Service",
        "Whether Pass Through Bill",
        "Against Invoice Ref.",
        "Invoice Date",
        "Due Date",
        "Transaction Posting Date",
        "Amount Receivable",
        "Due Date2",
        "Payment Status Paid/ Not paid",
        "Bank Account Number",
        "IFSC CODE",
        "Bank Branch",
        "Remarks",
        "Timline_Bucket",
    ],
}


def clean_text(value):
    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    value = str(value).strip()

    return value if value else None


def clean_serial(value):
    """Preserve serial numbers as text, including leading zeros."""

    if value is None:
        return None

    if isinstance(value, float) and value.is_integer():
        value = int(value)

    result = str(value).strip()
    return result or None


def clean_integer(value, sheet, row, column):
    if value is None or str(value).strip() == "":
        return None

    try:
        number = Decimal(str(value).replace(",", "").strip())

        if number != number.to_integral_value():
            raise ValueError("Expected a whole number")

        return int(number)

    except (InvalidOperation, ValueError):
        raise ValueError(
            f"{sheet}, row {row}, column '{column}': "
            f"Invalid integer value."
        )


def clean_decimal(value, sheet, row, column):
    if value is None or str(value).strip() == "":
        return None

    try:
        if isinstance(value, str):
            value = (
                value.replace(",", "")
                .replace("₹", "")
                .replace("$", "")
                .strip()
            )

        return Decimal(str(value))

    except (InvalidOperation, ValueError, TypeError):
        raise ValueError(
            f"{sheet}, row {row}, column '{column}': "
            f"Invalid numeric value."
        )


def clean_date(value, sheet, row, column):
    if value is None or str(value).strip() == "":
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    if isinstance(value, str):
        value = value.strip()

        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%d/%m/%y",
            "%d-%m-%y",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue

    raise ValueError(
        f"{sheet}, row {row}, column '{column}': "
        f"Invalid date value."
    )


def validate_headers(worksheet, sheet_name):
    header_row = next(
        worksheet.iter_rows(min_row=1, max_row=1, values_only=True),
        None,
    )

    if not header_row:
        raise ValueError(f"{sheet_name}: Missing header row.")

    actual_headers = [
        str(value).strip() if value is not None else ""
        for value in header_row
    ]

    if len(actual_headers) != len(set(actual_headers)):
        raise ValueError(f"{sheet_name}: Duplicate column headers found.")

    missing = [
        header
        for header in EXPECTED_HEADERS[sheet_name]
        if header not in actual_headers
    ]

    if missing:
        raise ValueError(
            f"{sheet_name}: Missing required columns: "
            + ", ".join(missing)
        )

    return {
        header: index
        for index, header in enumerate(actual_headers)
    }


def get_value(row, columns, column_name):
    index = columns[column_name]

    return row[index] if index < len(row) else None


def is_blank_row(row):
    return all(
        value is None or str(value).strip() == ""
        for value in row
    )


def parse_funds(worksheet, columns):
    records = []

    for row_number, row in enumerate(
        worksheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        if is_blank_row(row):
            continue

        records.append({
            "company_name": clean_text(
                get_value(row, columns, "Name of Company")
            ),
            "bank_name": clean_text(
                get_value(row, columns, "Bank Name")
            ),
            "account_no": clean_text(
                get_value(row, columns, "Account No.")
            ),
            "balance_inr": clean_decimal(
                get_value(row, columns, "Balance (INR)"),
                "Funds_Position", row_number, "Balance (INR)"
            ),
            "balance_usd": clean_decimal(
                get_value(row, columns, "Balance (USD)"),
                "Funds_Position", row_number, "Balance (USD)"
            ),
            "inr_equivalent": clean_decimal(
                get_value(row, columns, "INR Equivalent"),
                "Funds_Position", row_number, "INR Equivalent"
            ),
            "entity_type": clean_text(
                get_value(row, columns, "Entity Type")
            ),
        })

    return records


def parse_payables(worksheet, columns):
    records = []

    for row_number, row in enumerate(
        worksheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        if is_blank_row(row):
            continue

        records.append({
            "tracker_serial_no": clean_integer(
                get_value(row, columns, "Tracker Serial No."),
                "Payables", row_number, "Tracker Serial No."
            ),
            "cost_for_project": clean_text(
                get_value(row, columns, "Cost For Project")
            ),
            "payment_processed": clean_text(
                get_value(row, columns, "Status Payment processed [Y/N]")
            ),
            "payment_cycle": clean_text(
                get_value(row, columns, "Payment Cycle")
            ),
            "payer_company": clean_text(
                get_value(row, columns, "Payer Company")
            ),
            "branch": clean_text(
                get_value(row, columns, "Branch")
            ),
            "approved_in_vendor_management": clean_text(
                get_value(row, columns, "Approved IN Vendor Management Software?")
            ),
            "approval_date": clean_date(
                get_value(row, columns, "Approval Date"),
                "Payables", row_number, "Approval Date"
            ),
            "vendor_name_expense_name": clean_text(
                get_value(row, columns, "Vendor Name/ Expense Name")
            ),
            "product_service": clean_text(
                get_value(row, columns, "Product/Service")
            ),
            "pass_through_bill": clean_text(
                get_value(row, columns, "Whether Pass Through Bill")
            ),
            "invoice_ref": clean_text(
                get_value(row, columns, "Against Invoice Ref.")
            ),
            "invoice_date": clean_date(
                get_value(row, columns, "Invoice Date"),
                "Payables", row_number, "Invoice Date"
            ),
            "due_date": clean_date(
                get_value(row, columns, "Due Date"),
                "Payables", row_number, "Due Date"
            ),
            "transaction_posting_date": clean_date(
                get_value(row, columns, "Transaction Posting Date"),
                "Payables", row_number, "Transaction Posting Date"
            ),
            "amount_payable": clean_decimal(
                get_value(row, columns, "Amount Payable"),
                "Payables", row_number, "Amount Payable"
            ),
            "due_date_2": clean_date(
                get_value(row, columns, "Due Date2"),
                "Payables", row_number, "Due Date2"
            ),
            "payment_status": clean_text(
                get_value(row, columns, "Payment Status Paid/ Not paid")
            ),
            "bank_account_number": clean_text(
                get_value(row, columns, "Bank Account Number")
            ),
            "ifsc_code": clean_text(
                get_value(row, columns, "IFSC CODE")
            ),
            "bank_branch": clean_text(
                get_value(row, columns, "Bank Branch")
            ),
            "remarks": clean_text(
                get_value(row, columns, "Remarks")
            ),
            "timeline_bucket": clean_text(
                get_value(row, columns, "Timeline_Bucket")
            ),
        })

    return records


def parse_borrowings(worksheet, columns):
    records = []

    for row_number, row in enumerate(
        worksheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        if is_blank_row(row):
            continue

        sanctioned = clean_decimal(
            get_value(row, columns, "Sanctioned"),
            "Borrowing", row_number, "Sanctioned"
        )

        disbursed = clean_decimal(
            get_value(row, columns, "Disbersed"),
            "Borrowing", row_number, "Disbersed"
        )

        outstanding = clean_decimal(
            get_value(row, columns, "Outstanding"),
            "Borrowing", row_number, "Outstanding"
        )

        records.append({
            "sanctioned": sanctioned if sanctioned is not None else Decimal("0"),
            "disbursed": disbursed if disbursed is not None else Decimal("0"),
            "outstanding": outstanding if outstanding is not None else Decimal("0"),
        })

    return records


def parse_receivables(worksheet, columns):
    records = []

    for row_number, row in enumerate(
        worksheet.iter_rows(min_row=2, values_only=True),
        start=2,
    ):
        if is_blank_row(row):
            continue

        records.append({
            "serial_no": clean_serial(
                get_value(row, columns, "hoi")
            ),
            "cost_for_project": clean_text(
                get_value(row, columns, "Cost For Project")
            ),
            "payment_processed": clean_text(
                get_value(row, columns, "Status Payment processed [Y/N]")
            ),
            "receipt_cycle": clean_text(
                get_value(row, columns, "Receipt Cycle")
            ),
            "receiver_company": clean_text(
                get_value(row, columns, "Receiver Company")
            ),
            "branch": clean_text(
                get_value(row, columns, "Branch")
            ),
            "approved_in_vendor_management": clean_text(
                get_value(row, columns, "Approved IN Vendor Management Software?")
            ),
            "approval_date": clean_date(
                get_value(row, columns, "Approval Date"),
                "Receivables", row_number, "Approval Date"
            ),
            "vendor_name_income_name": clean_text(
                get_value(row, columns, "Vendor Name/ Income Name")
            ),
            "product_service": clean_text(
                get_value(row, columns, "Product/Service")
            ),
            "pass_through_bill": clean_text(
                get_value(row, columns, "Whether Pass Through Bill")
            ),
            "invoice_ref": clean_text(
                get_value(row, columns, "Against Invoice Ref.")
            ),
            "invoice_date": clean_date(
                get_value(row, columns, "Invoice Date"),
                "Receivables", row_number, "Invoice Date"
            ),
            "due_date": clean_date(
                get_value(row, columns, "Due Date"),
                "Receivables", row_number, "Due Date"
            ),
            "transaction_posting_date": clean_date(
                get_value(row, columns, "Transaction Posting Date"),
                "Receivables", row_number, "Transaction Posting Date"
            ),
            "amount_receivable": clean_decimal(
                get_value(row, columns, "Amount Receivable"),
                "Receivables", row_number, "Amount Receivable"
            ),
            "due_date_2": clean_date(
                get_value(row, columns, "Due Date2"),
                "Receivables", row_number, "Due Date2"
            ),
            "payment_status": clean_text(
                get_value(row, columns, "Payment Status Paid/ Not paid")
            ),
            "bank_account_number": clean_text(
                get_value(row, columns, "Bank Account Number")
            ),
            "ifsc_code": clean_text(
                get_value(row, columns, "IFSC CODE")
            ),
            "bank_branch": clean_text(
                get_value(row, columns, "Bank Branch")
            ),
            "remarks": clean_text(
                get_value(row, columns, "Remarks")
            ),
            "timeline_bucket": clean_text(
                get_value(row, columns, "Timline_Bucket")
            ),
        })

    return records


def parse_treasury_workbook(file_bytes: bytes):
    """Validate and parse the complete workbook without changing the DB."""

    try:
        workbook = load_workbook(
            BytesIO(file_bytes),
            read_only=True,
            data_only=True,
        )
    except Exception as exc:
        raise ValueError(
            "The downloaded file is not a valid readable Excel workbook."
        ) from exc

    try:
        missing_sheets = [
            name
            for name in EXPECTED_HEADERS
            if name not in workbook.sheetnames
        ]

        if missing_sheets:
            raise ValueError(
                "Workbook is missing required sheets: "
                + ", ".join(missing_sheets)
            )

        parsed = {}

        parsers = {
            "Funds_Position": parse_funds,
            "Payables": parse_payables,
            "Borrowing": parse_borrowings,
            "Receivables": parse_receivables,
        }

        for sheet_name, parser in parsers.items():
            worksheet = workbook[sheet_name]

            columns = validate_headers(
                worksheet,
                sheet_name,
            )

            parsed[sheet_name] = parser(
                worksheet,
                columns,
            )

        return parsed

    finally:
        workbook.close()


def download_and_parse_treasury_workbook():
    """Download the latest OneDrive workbook and parse it."""

    file_bytes = download_treasury_workbook()

    return parse_treasury_workbook(file_bytes)
