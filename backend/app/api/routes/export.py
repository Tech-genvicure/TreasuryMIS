from io import BytesIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from openpyxl import Workbook
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    FundPosition,
    Payable,
    Borrowing,
    Receivable,
    User,
)


router = APIRouter(
    prefix="/export",
    tags=["Excel Export"],
)


def model_to_dict(record, fields):
    return {
        field: getattr(record, field)
        for field in fields
    }


@router.get("/excel")
def export_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    workbook = Workbook()

    # Remove default sheet
    default_sheet = workbook.active
    workbook.remove(default_sheet)

    # ========================================================
    # FUNDS POSITION
    # ========================================================

    fund_sheet = workbook.create_sheet("Funds_Position")

    fund_fields = [
        "id",
        "company_name",
        "bank_name",
        "account_no",
        "balance_inr",
        "balance_usd",
        "inr_equivalent",
        "entity_type",
    ]

    for col, field in enumerate(fund_fields, start=1):
        fund_sheet.cell(
            row=1,
            column=col,
            value=field,
        )

    fund_records = (
        db.query(FundPosition)
        .order_by(FundPosition.id)
        .all()
    )

    for row_index, record in enumerate(
        fund_records,
        start=2,
    ):
        data = model_to_dict(
            record,
            fund_fields,
        )

        for col, field in enumerate(
            fund_fields,
            start=1,
        ):
            fund_sheet.cell(
                row=row_index,
                column=col,
                value=data[field],
            )

    # ========================================================
    # PAYABLES
    # ========================================================

    payable_sheet = workbook.create_sheet("Payables")

    payable_fields = [
        "id",
        "tracker_serial_no",
        "cost_for_project",
        "payment_processed",
        "payment_cycle",
        "payer_company",
        "branch",
        "approved_in_vendor_management",
        "approval_date",
        "vendor_name_expense_name",
        "product_service",
        "pass_through_bill",
        "invoice_ref",
        "invoice_date",
        "due_date",
        "transaction_posting_date",
        "amount_payable",
        "due_date_2",
        "payment_status",
        "bank_account_number",
        "ifsc_code",
        "bank_branch",
        "remarks",
        "timeline_bucket",
    ]

    for col, field in enumerate(
        payable_fields,
        start=1,
    ):
        payable_sheet.cell(
            row=1,
            column=col,
            value=field,
        )

    payable_records = (
        db.query(Payable)
        .order_by(Payable.id)
        .all()
    )

    for row_index, record in enumerate(
        payable_records,
        start=2,
    ):
        data = model_to_dict(
            record,
            payable_fields,
        )

        for col, field in enumerate(
            payable_fields,
            start=1,
        ):
            payable_sheet.cell(
                row=row_index,
                column=col,
                value=data[field],
            )

    # ========================================================
    # BORROWING
    # ========================================================

    borrowing_sheet = workbook.create_sheet("Borrowinig")

    borrowing_fields = [
        "id",
        "sanctioned",
        "disbursed",
        "outstanding",
    ]

    for col, field in enumerate(
        borrowing_fields,
        start=1,
    ):
        borrowing_sheet.cell(
            row=1,
            column=col,
            value=field,
        )

    borrowing_records = (
        db.query(Borrowing)
        .order_by(Borrowing.id)
        .all()
    )

    for row_index, record in enumerate(
        borrowing_records,
        start=2,
    ):
        data = model_to_dict(
            record,
            borrowing_fields,
        )

        for col, field in enumerate(
            borrowing_fields,
            start=1,
        ):
            borrowing_sheet.cell(
                row=row_index,
                column=col,
                value=data[field],
            )

    # ========================================================
    # RECEIVABLES
    # ========================================================

    receivable_sheet = workbook.create_sheet(
        "Receivables"
    )

    receivable_fields = [
        "id",
        "tracker_serial_no",
        "receipt_cycle",
        "receiver_company",
        "branch",
        "vendor_name_income_name",
        "product_service",
        "invoice_ref",
        "invoice_date",
        "due_date",
        "transaction_posting_date",
        "amount_receivable",
        "payment_status",
        "remarks",
        "timeline_bucket",
    ]

    for col, field in enumerate(
        receivable_fields,
        start=1,
    ):
        receivable_sheet.cell(
            row=1,
            column=col,
            value=field,
        )

    receivable_records = (
        db.query(Receivable)
        .order_by(Receivable.id)
        .all()
    )

    for row_index, record in enumerate(
        receivable_records,
        start=2,
    ):
        data = model_to_dict(
            record,
            receivable_fields,
        )

        for col, field in enumerate(
            receivable_fields,
            start=1,
        ):
            receivable_sheet.cell(
                row=row_index,
                column=col,
                value=data[field],
            )

    # ========================================================
    # BASIC EXCEL FORMATTING
    # ========================================================

    for sheet in workbook.worksheets:

        sheet.freeze_panes = "A2"

        for cell in sheet[1]:
            cell.font = cell.font.copy(
                bold=True
            )

        for column in sheet.columns:

            max_length = 0

            column_letter = column[0].column_letter

            for cell in column:

                if cell.value is not None:
                    max_length = max(
                        max_length,
                        len(str(cell.value)),
                    )

            sheet.column_dimensions[
                column_letter
            ].width = min(
                max_length + 2,
                40,
            )

    # ========================================================
    # CREATE FILE
    # ========================================================

    output = BytesIO()

    workbook.save(output)

    output.seek(0)

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition":
                'attachment; filename="Treasury_Master.xlsx"'
        },
    )