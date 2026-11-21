from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends
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

from app.schemas.dashboard import (
    DashboardResponse,
    DashboardKPIs,
    BorrowingSummary,
    TimelineAmount,
    FundSummary,
    VendorExposure,
)


router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"],
)


def decimal_or_zero(value):
    return value if value is not None else Decimal("0")


@router.get(
    "",
    response_model=DashboardResponse,
)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ========================================================
    # FUND POSITION
    # ========================================================

    fund_positions = (
        db.query(FundPosition)
        .order_by(FundPosition.id)
        .all()
    )

    total_cash_inr = sum(
        (
            decimal_or_zero(row.inr_equivalent)
            for row in fund_positions
        ),
        Decimal("0"),
    )

    total_cash_usd = sum(
        (
            decimal_or_zero(row.balance_usd)
            for row in fund_positions
        ),
        Decimal("0"),
    )


    # ========================================================
    # PAYABLES
    # ========================================================

    payables = (
        db.query(Payable)
        .order_by(Payable.id)
        .all()
    )

    total_payables = sum(
        (
            decimal_or_zero(row.amount_payable)
            for row in payables
        ),
        Decimal("0"),
    )


    # ========================================================
    # RECEIVABLES
    # ========================================================

    receivables = (
        db.query(Receivable)
        .order_by(Receivable.id)
        .all()
    )

    total_receivables = sum(
        (
            decimal_or_zero(row.amount_receivable)
            for row in receivables
        ),
        Decimal("0"),
    )


    # ========================================================
    # BORROWINGS
    # ========================================================

    borrowings = (
        db.query(Borrowing)
        .order_by(Borrowing.id)
        .all()
    )

    total_sanctioned = sum(
        (
            decimal_or_zero(row.sanctioned)
            for row in borrowings
        ),
        Decimal("0"),
    )

    total_disbursed = sum(
        (
            decimal_or_zero(row.disbursed)
            for row in borrowings
        ),
        Decimal("0"),
    )

    total_outstanding = sum(
        (
            decimal_or_zero(row.outstanding)
            for row in borrowings
        ),
        Decimal("0"),
    )


    # ========================================================
    # NET CASH POSITION
    # ========================================================

    net_cash_position = (
        total_cash_inr
        + total_receivables
        - total_payables
    )


    # ========================================================
    # FUND SUMMARY
    # ========================================================
    # Dashboard categories are fixed:
    # Bank of America
    # ICICI
    # Mutual Funds
    # FD
    #
    # Values are calculated from Fund Position records.
    # ========================================================

    fund_buckets = {
        "Bank of America": Decimal("0"),
        "ICICI": Decimal("0"),
        "Mutual Funds": Decimal("0"),
        "FD": Decimal("0"),
    }


    
    for row in fund_positions:

        amount = decimal_or_zero(
            row.inr_equivalent
        )

        bank_name = (
            row.bank_name or ""
        ).strip().lower()

        company_name = (
            row.company_name or ""
        ).strip().lower()

        entity_type = (
            row.entity_type or ""
        ).strip().lower()

        # --------------------------------------------
        # MUTUAL FUNDS
        # --------------------------------------------

        if (
            "mutual" in entity_type
            or "mutual fund" in bank_name
            or "mutual fund" in company_name
        ):

            fund_buckets[
                "Mutual Funds"
            ] += amount

        # --------------------------------------------
        # FD
        # --------------------------------------------

        elif (
            entity_type == "fd"
            or "fixed deposit" in entity_type
            or "fixed deposit" in bank_name
            or "fixed deposit" in company_name
            or entity_type.startswith("fd ")
        ):

            fund_buckets[
                "FD"
            ] += amount

        # --------------------------------------------
        # BANK OF AMERICA
        # --------------------------------------------

        elif (
            "bank of america" in bank_name
            or "bank of america" in company_name
        ):

            fund_buckets[
                "Bank of America"
            ] += amount

        # --------------------------------------------
        # ICICI
        # --------------------------------------------

        elif "icici" in bank_name:

            fund_buckets[
                "ICICI"
            ] += amount


    fund_summary = [
        FundSummary(
            company_name=category,
            amount=amount,
        )
        for category, amount in fund_buckets.items()
    ]


    # ========================================================
    # TOP VENDOR EXPOSURE
    # ========================================================

    vendor_buckets = {}

    for row in payables:

        vendor = (
            row.vendor_name_expense_name
            or "Unclassified"
        )

        amount = decimal_or_zero(
            row.amount_payable
        )

        vendor_buckets[vendor] = (
            vendor_buckets.get(
                vendor,
                Decimal("0"),
            )
            + amount
        )


    vendor_exposure = [
        VendorExposure(
            vendor_name=vendor,
            amount=amount,
        )
        for vendor, amount in vendor_buckets.items()
    ]

    vendor_exposure.sort(
        key=lambda item: item.amount,
        reverse=True,
    )

    # Match the reference design: top 12
    vendor_exposure = vendor_exposure[:12]


    # ========================================================
    # PAYABLE TIMELINE
    # ========================================================

    payable_buckets = {}

    for row in payables:

        bucket = (
            row.timeline_bucket
            or "Unclassified"
        )

        amount = decimal_or_zero(
            row.amount_payable
        )

        payable_buckets[bucket] = (
            payable_buckets.get(
                bucket,
                Decimal("0"),
            )
            + amount
        )


    payable_timeline = [
        TimelineAmount(
            bucket=bucket,
            amount=amount,
        )
        for bucket, amount in payable_buckets.items()
    ]


    # ========================================================
    # RECEIVABLE TIMELINE
    # ========================================================

    receivable_buckets = {}

    for row in receivables:

        bucket = (
            row.timeline_bucket
            or "Unclassified"
        )

        amount = decimal_or_zero(
            row.amount_receivable
        )

        receivable_buckets[bucket] = (
            receivable_buckets.get(
                bucket,
                Decimal("0"),
            )
            + amount
        )


    receivable_timeline = [
        TimelineAmount(
            bucket=bucket,
            amount=amount,
        )
        for bucket, amount in receivable_buckets.items()
    ]


    # ========================================================
    # REPORTING DATE
    # ========================================================

    dates = []

    for row in payables:

        if row.transaction_posting_date:
            dates.append(
                row.transaction_posting_date
            )

    for row in receivables:

        if row.transaction_posting_date:
            dates.append(
                row.transaction_posting_date
            )

    if dates:
        reporting_date = max(dates).isoformat()
    else:
        reporting_date = date.today().isoformat()


    # ========================================================
    # RESPONSE
    # ========================================================

    return DashboardResponse(

        reporting_date=reporting_date,

        kpis=DashboardKPIs(
            total_cash_inr=total_cash_inr,
            total_cash_usd=total_cash_usd,
            total_payables=total_payables,
            total_receivables=total_receivables,
            net_cash_position=net_cash_position,
        ),

        borrowings=BorrowingSummary(
            sanctioned=total_sanctioned,
            disbursed=total_disbursed,
            outstanding=total_outstanding,
        ),

        fund_summary=fund_summary,

        vendor_exposure=vendor_exposure,

        payable_timeline=payable_timeline,

        receivable_timeline=receivable_timeline,
    )