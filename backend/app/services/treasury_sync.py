
from datetime import datetime

from sqlalchemy import delete

from app.db.session import SessionLocal
from app.models import (
    FundPosition,
    Payable,
    Borrowing,
    Receivable,
    SyncRun,
)
from app.services.treasury_excel_parser import (
    download_and_parse_treasury_workbook,
)


def sync_treasury_from_onedrive():
    """
    Download and validate the OneDrive workbook, then atomically
    replace all four financial tables.

    Empty sheets are valid and clear their corresponding tables.
    """

    db = SessionLocal()
    sync_run_id = None

    try:
        # 1. Create and persist the sync history entry.
        sync_run = SyncRun(
            status="running",
            started_at=datetime.utcnow(),
        )

        db.add(sync_run)
        db.commit()
        db.refresh(sync_run)

        sync_run_id = sync_run.id

        # IMPORTANT:
        # refresh() starts a new implicit transaction.
        # Commit it before starting the replacement transaction.
        db.commit()

        # 2. Download and validate the workbook.
        # No financial records are modified here.
        parsed = download_and_parse_treasury_workbook()

        funds = parsed["Funds_Position"]
        payables = parsed["Payables"]
        borrowings = parsed["Borrowing"]
        receivables = parsed["Receivables"]

        counts = {
            "funds_count": len(funds),
            "payables_count": len(payables),
            "borrowing_count": len(borrowings),
            "receivables_count": len(receivables),
        }

        # 3. Replace all four tables atomically.
        with db.begin():

            db.execute(delete(Payable))
            db.execute(delete(Receivable))
            db.execute(delete(Borrowing))
            db.execute(delete(FundPosition))

            db.add_all([
                FundPosition(**record)
                for record in funds
            ])

            db.add_all([
                Payable(**record)
                for record in payables
            ])

            db.add_all([
                Borrowing(**record)
                for record in borrowings
            ])

            db.add_all([
                Receivable(**record)
                for record in receivables
            ])

            # Update sync history within the same transaction.
            sync_run = db.get(SyncRun, sync_run_id)

            sync_run.status = "success"
            sync_run.completed_at = datetime.utcnow()
            sync_run.funds_count = counts["funds_count"]
            sync_run.payables_count = counts["payables_count"]
            sync_run.borrowing_count = counts["borrowing_count"]
            sync_run.receivables_count = counts["receivables_count"]
            sync_run.error_message = None

        return {
            "status": "success",
            "sync_run_id": sync_run_id,
            **counts,
            "total_records": sum(counts.values()),
        }

    except Exception as exc:
        db.rollback()

        # Record the failure separately from the financial transaction.
        if sync_run_id is not None:
            try:
                with db.begin():
                    sync_run = db.get(SyncRun, sync_run_id)

                    if sync_run:
                        sync_run.status = "failed"
                        sync_run.completed_at = datetime.utcnow()
                        sync_run.error_message = str(exc)[:4000]

            except Exception:
                db.rollback()

        raise

    finally:
        db.close()
