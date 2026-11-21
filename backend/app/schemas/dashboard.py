from decimal import Decimal

from pydantic import BaseModel


class DashboardKPIs(BaseModel):
    total_cash_inr: Decimal
    total_cash_usd: Decimal
    total_payables: Decimal
    total_receivables: Decimal
    net_cash_position: Decimal


class BorrowingSummary(BaseModel):
    sanctioned: Decimal
    disbursed: Decimal
    outstanding: Decimal


class TimelineAmount(BaseModel):
    bucket: str
    amount: Decimal


class FundSummary(BaseModel):
    company_name: str
    amount: Decimal


class VendorExposure(BaseModel):
    vendor_name: str
    amount: Decimal


class DashboardResponse(BaseModel):
    reporting_date: str

    kpis: DashboardKPIs

    borrowings: BorrowingSummary

    fund_summary: list[FundSummary]

    vendor_exposure: list[VendorExposure]

    payable_timeline: list[TimelineAmount]

    receivable_timeline: list[TimelineAmount]