
import logging
import time

from app.core.config import settings
from app.services.treasury_sync import sync_treasury_from_onedrive


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("treasury-sync-worker")


def run_worker():
    interval = max(1, settings.MS_SYNC_INTERVAL_MINUTES) * 60

    logger.info("Genvicure Treasury Sync Worker starting")
    logger.info("Sync enabled: %s", settings.MS_SYNC_ENABLED)
    logger.info("Sync interval: %s minutes", settings.MS_SYNC_INTERVAL_MINUTES)

    if not settings.MS_SYNC_ENABLED:
        logger.warning("Automatic sync is disabled. Worker will remain idle.")

        while True:
            time.sleep(60)

    while True:
        try:
            logger.info("Starting scheduled OneDrive synchronization")

            result = sync_treasury_from_onedrive()

            logger.info(
                "Synchronization successful: %s",
                result,
            )

        except Exception:
            logger.exception(
                "Synchronization failed. Existing financial data is retained."
            )

        logger.info(
            "Next synchronization in %s minutes",
            settings.MS_SYNC_INTERVAL_MINUTES,
        )

        time.sleep(interval)


if __name__ == "__main__":
    run_worker()
