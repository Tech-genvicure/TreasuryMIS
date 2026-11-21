from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.inspection import inspect
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user
from app.db.session import get_db
from app.models import (
    User,
    FundPosition,
    Payable,
    Borrowing,
    Receivable,
)
from io import BytesIO

from fastapi.responses import StreamingResponse
from openpyxl import Workbook


router = APIRouter(
    prefix="/treasury",
    tags=["Treasury"],
)


# ============================================================
# SERIALIZATION
# ============================================================

def serialize_model(row):
    result = {}

    for column in inspect(row).mapper.column_attrs:
        value = getattr(row, column.key)

        if isinstance(value, Decimal):
            result[column.key] = float(value)
        else:
            result[column.key] = value

    return result


# ============================================================
# FUNDS POSITION
# ============================================================

@router.get("/fund-positions")
def get_fund_positions(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(FundPosition)
        .order_by(FundPosition.id)
        .all()
    )

    return [
        serialize_model(row)
        for row in rows
    ]


@router.post("/fund-positions")
def create_fund_position(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_fields = {
        "company_name",
        "bank_name",
        "account_no",
        "balance_inr",
        "balance_usd",
        "inr_equivalent",
        "entity_type",
    }

    data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    row = FundPosition(**data)

    db.add(row)
    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.put("/fund-positions/{row_id}")
def update_fund_position(
    row_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(FundPosition)
        .filter(FundPosition.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Fund position not found",
        )

    allowed_fields = {
        "company_name",
        "bank_name",
        "account_no",
        "balance_inr",
        "balance_usd",
        "inr_equivalent",
        "entity_type",
    }

    for key, value in payload.items():

        if key not in allowed_fields:
            continue

        if value == "":
            value = None

        setattr(row, key, value)

    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.delete("/fund-positions/{row_id}")
def delete_fund_position(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(FundPosition)
        .filter(FundPosition.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Fund position not found",
        )

    db.delete(row)
    db.commit()

    return {
        "message": "Fund position deleted",
        "id": row_id,
    }


# ============================================================
# PAYABLES
# ============================================================

@router.get("/payables")
def get_payables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Payable)
        .order_by(Payable.id)
        .all()
    )

    return [
        serialize_model(row)
        for row in rows
    ]


@router.post("/payables")
def create_payable(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_fields = {
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
    }

    data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    row = Payable(**data)

    db.add(row)
    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.put("/payables/{row_id}")
def update_payable(
    row_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Payable)
        .filter(Payable.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Payable not found",
        )

    allowed_fields = {
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
    }

    for key, value in payload.items():

        if key not in allowed_fields:
            continue

        if value == "":
            value = None

        setattr(row, key, value)

    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.delete("/payables/{row_id}")
def delete_payable(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Payable)
        .filter(Payable.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Payable not found",
        )

    db.delete(row)
    db.commit()

    return {
        "message": "Payable deleted",
        "id": row_id,
    }


# ============================================================
# BORROWINGS
# ============================================================

@router.get("/borrowings")
def get_borrowings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Borrowing)
        .order_by(Borrowing.id)
        .all()
    )

    return [
        serialize_model(row)
        for row in rows
    ]


@router.post("/borrowings")
def create_borrowing(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_fields = {
        "sanctioned",
        "disbursed",
        "outstanding",
    }

    data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    row = Borrowing(**data)

    db.add(row)
    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.put("/borrowings/{row_id}")
def update_borrowing(
    row_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Borrowing)
        .filter(Borrowing.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Borrowing record not found",
        )

    allowed_fields = {
        "sanctioned",
        "disbursed",
        "outstanding",
    }

    for key, value in payload.items():

        if key not in allowed_fields:
            continue

        if value == "":
            value = None

        setattr(row, key, value)

    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.delete("/borrowings/{row_id}")
def delete_borrowing(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Borrowing)
        .filter(Borrowing.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Borrowing record not found",
        )

    db.delete(row)
    db.commit()

    return {
        "message": "Borrowing deleted",
        "id": row_id,
    }


# ============================================================
# RECEIVABLES
# ============================================================

@router.get("/receivables")
def get_receivables(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rows = (
        db.query(Receivable)
        .order_by(Receivable.id)
        .all()
    )

    return [
        serialize_model(row)
        for row in rows
    ]


@router.post("/receivables")
def create_receivable(
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    allowed_fields = {
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
    }

    data = {
        key: value
        for key, value in payload.items()
        if key in allowed_fields
    }

    row = Receivable(**data)

    db.add(row)
    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.put("/receivables/{row_id}")
def update_receivable(
    row_id: int,
    payload: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Receivable)
        .filter(Receivable.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Receivable not found",
        )

    allowed_fields = {
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
    }

    for key, value in payload.items():

        if key not in allowed_fields:
            continue

        if value == "":
            value = None

        setattr(row, key, value)

    db.commit()
    db.refresh(row)

    return serialize_model(row)


@router.delete("/receivables/{row_id}")
def delete_receivable(
    row_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    row = (
        db.query(Receivable)
        .filter(Receivable.id == row_id)
        .first()
    )

    if not row:
        raise HTTPException(
            status_code=404,
            detail="Receivable not found",
        )

    db.delete(row)
    db.commit()

    return {
        "message": "Receivable deleted",
        "id": row_id,
    }

# ============================================================
# EXCEL EXPORT
# ============================================================

@router.get("/export/excel")
def export_treasury_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workbook = Workbook()

    # Remove the default empty worksheet
    workbook.remove(workbook.active)

    sheets = [
        ("Funds_Position", FundPosition),
        ("Payables", Payable),
        ("Borrowing", Borrowing),
        ("Receivables", Receivable),
    ]

    for sheet_name, model in sheets:
        worksheet = workbook.create_sheet(
            title=sheet_name
        )

        # Use the actual database model columns
        columns = [
            column.key
            for column in model.__table__.columns
            if column.key not in (
                "created_at",
                "updated_at",
            )
        ]

        # Write column headers
        worksheet.append(columns)

        # Fetch the latest saved database records
        records = (
            db.query(model)
            .order_by(model.id)
            .all()
        )

        # Write data rows
        for record in records:
            values = []

            for column in columns:
                value = getattr(record, column)

                # Convert date/time values to Excel-friendly text
                if hasattr(value, "isoformat"):
                    value = value.isoformat()

                # Convert Decimal values to Excel numbers
                elif isinstance(value, Decimal):
                    value = float(value)

                values.append(value)

            worksheet.append(values)

        # Format the worksheet
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = worksheet.dimensions

        for cell in worksheet[1]:
            cell.font = cell.font.copy(bold=True)

        for column_cells in worksheet.columns:
            max_length = max(
                (
                    len(str(cell.value))
                    for cell in column_cells
                    if cell.value is not None
                ),
                default=10,
            )

            worksheet.column_dimensions[
                column_cells[0].column_letter
            ].width = min(max_length + 2, 35)

    # Generate the Excel file in memory
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
            "Content-Disposition": (
                'attachment; filename="Genvicure_Treasury_Master.xlsx"'
            )
        },
    )