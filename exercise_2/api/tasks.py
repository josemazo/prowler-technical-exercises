import random
import time

from django.conf import settings
from django.utils import timezone
from procrastinate.contrib.django import app

from api import models
from api.utils import logging

logger = logging.getLogger(__name__)


@app.task
def start_scan(scan_id):
    logger.info(f"Starting scan with ID: {scan_id}")

    try:
        scan = models.Scan.objects.get(id=scan_id)

    except models.Scan.DoesNotExist:
        logger.info(f"Scan with ID {scan_id} does not exist.")
        return

    logger.info(f"({scan_id}) Provider: {scan.provider.name} - Name: {scan.name}")

    scan.status = models.Scan.Status.IN_PROGRESS
    scan.started_at = timezone.now()
    scan.save()

    scan_status = models.Scan.Status.COMPLETED
    failed_reason = None

    checks = models.Check.objects.filter(provider=scan.provider)
    if not checks.exists():
        scan_status = models.Scan.Status.FAILED
        failed_reason = "no checks found for provider"

    for check in checks:
        time.sleep(settings.CHECK_SLEEP_TIME)

        if random.random() < settings.CHECK_EXCEPTION_RATE:
            scan_status = models.Scan.Status.FAILED
            failed_reason = "Some checks could not be completed"
            logger.info(f"({scan_id}) Check: {check.name} - An unexpected error occurred")
            break

        success = random.random() < settings.CHECK_SUCCESS_RATE
        models.Finding.objects.create(scan=scan, check_parent=check, success=success)
        logger.info(f"({scan_id}) Check: {check.name} - Success: {success}")

    scan.status = scan_status
    scan.failed_reason = failed_reason
    scan.finished_at = timezone.now()
    scan.save()

    logger.info(f"({scan_id}) Final status: {scan.status}")
    logger.info(f"Finished scan with ID: {scan_id}")
