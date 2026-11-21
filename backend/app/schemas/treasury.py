from decimal import Decimal
from datetime import date

from pydantic import BaseModel, ConfigDict


# ============================================================
# FUND POSITION
# ============================================================

class FundPositionResponse(BaseModel):
    id: int
    company_name: str | None = None
    bank_name: str | None = None
    account_no: str | None = None
    balance_inr: Decimal | None = None
    balance_usd: Decimal | None = None
    inr_equivalent: Decimal | None = None
    entity_type: str | None = None

    model_config = ConfigDict(from_attributes=True)


class FundPositionUpdate(BaseModel):
    company_name: str | None = None
    bank_name: str | None = None
    account_no: str | None = None
    balance_inr: Decimal | None = None
    balance_usd: Decimal | None = None
    inr_equivalent: Decimal | None = None
    entity_type: str | None = None


# ============================================================
# PAYABLE
# ============================================================

class PayableResponse(BaseModel):
    id: int

    tracker_serial_no: str | None = None
    cost_for_project: str | None = None
    payment_processed: str | None = None
    payment_cycle: str | None = None
    payer_company: str | None = None
    branch: str | None = None
    approved_in_vendor_management: str | None = None
    approval_date: date | None = None
    vendor_name_expense_name: str | None = None
    product_service: str | None = None
    pass_through_bill: str | None = None
    invoice_ref: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    transaction_posting_date: date | None = None
    amount_payable: Decimal | None = None
    due_date_2: date | None = None
    payment_status: str | None = None
    bank_account_number: str | None = None
    ifsc_code: str | None = None
    bank_branch: str | None = None
    remarks: str | None = None
    timeline_bucket: str | None = None

    model_config = ConfigDict(from_attributes=True)


class PayableUpdate(BaseModel):
    tracker_serial_no: str | None = None
    cost_for_project: str | None = None
    payment_processed: str | None = None
    payment_cycle: str | None = None
    payer_company: str | None = None
    branch: str | None = None
    approved_in_vendor_management: str | None = None
    approval_date: date | None = None
    vendor_name_expense_name: str | None = None
    product_service: str | None = None
    pass_through_bill: str | None = None
    invoice_ref: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    transaction_posting_date: date | None = None
    amount_payable: Decimal | None = None
    due_date_2: date | None = None
    payment_status: str | None = None
    bank_account_number: str | None = None
    ifsc_code: str | None = None
    bank_branch: str | None = None
    remarks: str | None = None
    timeline_bucket: str | None = None


# ============================================================
# BORROWING
# ============================================================

class BorrowingResponse(BaseModel):
    id: int
    sanctioned: Decimal | None = None
    disbursed: Decimal | None = None
    outstanding: Decimal | None = None

    model_config = ConfigDict(from_attributes=True)


class BorrowingUpdate(BaseModel):
    sanctioned: Decimal | None = None
    disbursed: Decimal | None = None
    outstanding: Decimal | None = None


# ============================================================
# RECEIVABLE
# ============================================================

class ReceivableResponse(BaseModel):
    id: int

    tracker_serial_no: str | None = None
    receipt_cycle: str | None = None
    receiver_company: str | None = None
    branch: str | None = None
    vendor_name_income_name: str | None = None
    product_service: str | None = None
    invoice_ref: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    transaction_posting_date: date | None = None
    amount_receivable: Decimal | None = None
    payment_status: str | None = None
    remarks: str | None = None
    timeline_bucket: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ReceivableUpdate(BaseModel):
    tracker_serial_no: str | None = None
    receipt_cycle: str | None = None
    receiver_company: str | None = None
    branch: str | None = None
    vendor_name_income_name: str | None = None
    product_service: str | None = None
    invoice_ref: str | None = None
    invoice_date: date | None = None
    due_date: date | None = None
    transaction_posting_date: date | None = None
    amount_receivable: Decimal | None = None
    payment_status: str | None = None
    remarks: str | None = None
    timeline_bucket: str | None = None