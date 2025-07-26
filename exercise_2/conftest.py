import pytest

from procrastinate import testing
from procrastinate.contrib.django import procrastinate_app as procrastinate
from rest_framework.test import APIClient

PROVIDERS = {
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
}

CHECKS = {
    "aws_s3": "S3 Buckets Public Read Access",
    "aws_ec2": "EC2 Instances Security Groups",
    "aws_iam": "IAM Permissions Review",
}

SCANS = {
    "production": "Production Environment scan",
    "staging": "Staging Environment scan",
    "development": "Development Environment scan",
    "comment_daily": "Daily security scan",
    "comment_weekly": "Weekly security scan",
}

FINDINGS = {
    "comment_passed": "Check passed successfully",
    "comment_failed": "Check failed after review",
}

TASK_NAME = "api.tasks.start_scan"


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Enable database access for all tests."""
    yield


@pytest.fixture
def api_client():
    """API client fixture for making HTTP requests."""
    yield APIClient()


@pytest.fixture
def procrastinate_app():
    """Procrastinate app with in-memory connector for testing."""
    in_memory = testing.InMemoryConnector()
    with procrastinate.current_app.replace_connector(in_memory) as app:
        yield app


# About `transactional_db`: `pytest-django` can't close connections when transactions are needed, so a warning is raised
@pytest.fixture
def worker(procrastinate_app, transactional_db):
    """Worker fixture for running tasks in tests."""

    def run_worker():
        procrastinate_app.run_worker(wait=False, install_signal_handlers=False, listen_notify=False)

    yield run_worker
