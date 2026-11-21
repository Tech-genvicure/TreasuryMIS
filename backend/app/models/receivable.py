
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Receivable(Base):
    __tablename__ = "receivables"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True,
    )

    serial_no: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    cost_for_project: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    payment_processed: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    receipt_cycle: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    receiver_company: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    branch: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    approved_in_vendor_management: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
    )

    approval_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    vendor_name_income_name: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    product_service: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    pass_through_bill: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    invoice_ref: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    invoice_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    due_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    transaction_posting_date: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    amount_receivable: Mapped[Decimal | None] = mapped_column(
        Numeric(18, 2),
        nullable=True,
    )

    due_date_2: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
    )

    payment_status: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bank_account_number: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    ifsc_code: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )

    bank_branch: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    remarks: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    timeline_bucket: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
