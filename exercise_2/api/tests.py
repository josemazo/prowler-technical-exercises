import pytest

from django.urls import reverse
from rest_framework import status

from api.models import Check, Finding, Provider, Scan
from conftest import CHECKS, FINDINGS, PROVIDERS, SCANS, TASK_NAME


class TestHealthAPI:
    """Test health check endpoint"""

    def test_health_endpoint_exists(self, api_client):
        """Test that health endpoint is accessible"""
        url = reverse("health-list")
        response = api_client.get(url)

        # TODO: `/health` checks `procrastinate` workers in DB, as it's working on memory while tests, `200` won't work
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_503_SERVICE_UNAVAILABLE]
        assert "status" in response.data


class TestProviderAPI:
    """Test Provider CRUD operations"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Setup test data for each test"""

        self.provider_data = {"name": PROVIDERS["aws"]}
        self.provider = Provider.objects.create(name=PROVIDERS["azure"])

    def test_create_provider(self, api_client):
        """Test creating a new provider"""

        url = reverse("providers-list")
        response = api_client.post(url, self.provider_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == PROVIDERS["aws"]
        assert Provider.objects.filter(name=PROVIDERS["aws"]).exists()  # Check using Django ORM

    def test_list_providers(self, api_client):
        """Test listing all providers"""

        url = reverse("providers-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        # Create another provider
        api_client.post(url, self.provider_data, format="json")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_provider(self, api_client):
        """Test retrieving a specific provider"""

        url = reverse("providers-detail", kwargs={"pk": self.provider.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == PROVIDERS["azure"]

    def test_update_provider(self, api_client):
        """Test updating a provider"""

        url = reverse("providers-detail", kwargs={"pk": self.provider.id})
        updated_data = {"name": PROVIDERS["gcp"]}
        response = api_client.put(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == PROVIDERS["gcp"]

    def test_delete_provider(self, api_client):
        """Test deleting a provider"""

        url = reverse("providers-detail", kwargs={"pk": self.provider.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND  # Check using API
        assert not Provider.objects.filter(id=self.provider.id).exists()  # Check using Django ORM

    def test_provider_name_unique_constraint(self, api_client):
        """Test that provider names must be unique"""

        url = reverse("providers-list")
        duplicate_data = {"name": PROVIDERS["azure"]}
        response = api_client.post(url, duplicate_data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestCheckAPI:
    """Test Check CRUD operations (nested under providers)"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Setup test data for each test"""

        self.provider = Provider.objects.create(name=PROVIDERS["aws"])
        self.provider_alternative = Provider.objects.create(name=PROVIDERS["azure"])

        self.check_data = {"name": CHECKS["aws_s3"]}
        self.check = Check.objects.create(provider=self.provider, name=CHECKS["aws_ec2"])

    def test_create_check(self, api_client):
        """Test creating a check under a provider"""
        url = reverse("provider-checks-list", kwargs={"provider_pk": self.provider.id})
        response = api_client.post(url, self.check_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == CHECKS["aws_s3"]
        assert response.data["provider_id"] == self.provider.id

    def test_list_provider_checks(self, api_client):
        """Test listing all checks for a provider"""

        url_provider = reverse("provider-checks-list", kwargs={"provider_pk": self.provider.id})
        response = api_client.get(url_provider)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        # Create another check
        api_client.post(url_provider, self.check_data, format="json")
        response = api_client.get(url_provider)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

        # Create a check for another provider
        url_provider_alternative = reverse("provider-checks-list", kwargs={"provider_pk": self.provider_alternative.id})
        response = api_client.post(url_provider_alternative, self.check_data, format="json")

        response = api_client.get(url_provider)

        assert len(response.data["results"]) == 2  # Checks on the _original_ provider remain unaffected

    def test_retrieve_check(self, api_client):
        """Test retrieving a specific check"""

        url = reverse("provider-checks-detail", kwargs={"provider_pk": self.provider.id, "pk": self.check.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == CHECKS["aws_ec2"]

    def test_update_check(self, api_client):
        """Test updating a check"""

        url = reverse("provider-checks-detail", kwargs={"provider_pk": self.provider.id, "pk": self.check.id})
        updated_data = {"name": CHECKS["aws_iam"]}
        response = api_client.put(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == CHECKS["aws_iam"]

    def test_delete_check(self, api_client):
        """Test deleting a check"""

        url = reverse("provider-checks-detail", kwargs={"provider_pk": self.provider.id, "pk": self.check.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND  # Check using API
        assert not Check.objects.filter(id=self.check.id).exists()  # Check using Django ORM

    def test_check_unique_constraint(self, api_client):
        """Test that check names must be unique per provider"""

        url = reverse("provider-checks-list", kwargs={"provider_pk": self.provider.id})
        duplicate_data = {"name": CHECKS["aws_ec2"]}
        response = api_client.post(url, duplicate_data, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT


class TestScanAPI:
    """Test Scan CRUD operations"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Setup test data for each test"""

        self.provider = Provider.objects.create(name=PROVIDERS["aws"])
        self.provider_alternative = Provider.objects.create(name=PROVIDERS["azure"])

        self.check_0 = Check.objects.create(provider=self.provider, name=CHECKS["aws_s3"])
        self.check_1 = Check.objects.create(provider=self.provider, name=CHECKS["aws_ec2"])

        self.scan_data = {
            "provider_id": str(self.provider.id),
            "name": SCANS["production"],
            "comment": SCANS["comment_weekly"],
        }
        self.scan = Scan.objects.create(provider=self.provider, name=SCANS["staging"], status=Scan.Status.COMPLETED)

    def test_create_scan_no_worker(self, api_client, procrastinate_app):
        """Test creating a new scan without running the worker"""

        url = reverse("scans-list")
        response = api_client.post(url, self.scan_data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["name"] == SCANS["production"]
        assert str(response.data["provider_id"]) == str(self.provider.id)
        assert response.data["status"] == Scan.Status.PENDING  # Should start as `PENDING`` status

        # Verify that start_scan task was queued
        jobs = procrastinate_app.connector.jobs
        assert len(jobs) == 1
        assert jobs[1]["task_name"] == TASK_NAME

    def test_create_scan(self, api_client, worker):
        """Test creating a scan and running the worker"""

        url_post = reverse("scans-list")
        response = api_client.post(url_post, self.scan_data, format="json")
        scan_id = response.data["id"]

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["status"] == Scan.Status.PENDING

        # Getting the scan to check its status
        url_get = reverse("scans-detail", kwargs={"pk": scan_id})
        response = api_client.get(url_get)

        assert response.data["status"] == Scan.Status.PENDING

        # Run the worker to process the task
        worker()

        # Getting the scan to check its status again
        response = api_client.get(url_get)

        assert response.data["status"] == Scan.Status.COMPLETED

    def test_list_scans(self, api_client):
        """Test listing all scans"""

        url = reverse("scans-list")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        api_client.post(url, self.scan_data, format="json")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_retrieve_scan(self, api_client):
        """Test retrieving a specific scan"""

        url = reverse("scans-detail", kwargs={"pk": self.scan.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == SCANS["staging"]

    def test_update_scan(self, api_client):
        """Test updating a scan"""

        url = reverse("scans-detail", kwargs={"pk": self.scan.id})
        updated_data = {
            "provider_id": str(self.provider_alternative.id),
            "name": SCANS["production"],
            "comment": SCANS["comment_daily"],
        }
        response = api_client.put(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["comment"] == SCANS["comment_daily"]

        assert str(response.data["provider_id"]) != str(self.provider_alternative.id)
        assert str(response.data["provider_id"]) == str(self.provider.id)

    def test_delete_scan(self, api_client):
        """Test deleting a scan"""

        url = reverse("scans-detail", kwargs={"pk": self.scan.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND  # Check using API
        assert not Scan.objects.filter(id=self.scan.id).exists()  # Check using Django ORM

    def test_scan_status_endpoint(self, api_client, worker):
        """Test the custom status endpoint for scans"""

        url_status = reverse("scans-status", kwargs={"pk": self.scan.id})
        response = api_client.get(url_status)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == Scan.Status.COMPLETED
        assert len(response.data) == 1  # Should return only the status

        # Create a new scan to check its status
        url_post = reverse("scans-list")
        response = api_client.post(url_post, self.scan_data, format="json")

        url_status = reverse("scans-status", kwargs={"pk": response.data["id"]})
        response = api_client.get(url_status)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == Scan.Status.PENDING

    def test_scan_unique_constraint(self, api_client):
        """Test that scan names must be unique per provider"""

        url = reverse("scans-list")
        duplicate_data = {"provider_id": str(self.provider.id), "name": SCANS["staging"]}
        response = api_client.post(url, duplicate_data, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT


class TestFindingAPI:
    """Test Finding operations (nested under scans)"""

    @pytest.fixture(autouse=True)
    def setup_data(self):
        """Setup test data for each test"""

        self.provider = Provider.objects.create(name=PROVIDERS["aws"])

        self.check_0 = Check.objects.create(provider=self.provider, name=CHECKS["aws_s3"])
        self.check_1 = Check.objects.create(provider=self.provider, name=CHECKS["aws_ec2"])

        self.scan_data = {
            "provider_id": str(self.provider.id),
            "name": SCANS["production"],
            "comment": SCANS["development"],
        }
        self.scan = Scan.objects.create(provider=self.provider, name=SCANS["staging"], status=Scan.Status.IN_PROGRESS)
        self.scan_alternative = Scan.objects.create(
            provider=self.provider, name=SCANS["development"], status=Scan.Status.COMPLETED
        )

        self.finding = Finding.objects.create(
            scan=self.scan, check_parent=self.check_0, success=True, comment=FINDINGS["comment_passed"]
        )

    def test_list_scan_findings(self, api_client, worker):
        """Test listing all findings for a scan"""

        url_list_findings = reverse("scan-findings-list", kwargs={"scan_pk": self.scan.id})
        response = api_client.get(url_list_findings)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1

        url_post_scan = reverse("scans-list")
        response = api_client.post(url_post_scan, self.scan_data, format="json")

        worker()

        url_list_findings = reverse("scan-findings-list", kwargs={"scan_pk": response.data["id"]})
        response = api_client.get(url_list_findings)

        assert len(response.data["results"]) == 2

    def test_retrieve_finding(self, api_client):
        """Test retrieving a specific finding"""

        url = reverse("scan-findings-detail", kwargs={"scan_pk": self.scan.id, "pk": self.finding.id})
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"]
        assert response.data["comment"] == FINDINGS["comment_passed"]

    def test_update_finding(self, api_client):
        """Test updating a finding"""

        url = reverse("scan-findings-detail", kwargs={"scan_pk": self.scan.id, "pk": self.finding.id})
        updated_data = {"scan_id": self.scan_alternative.id, "comment": FINDINGS["comment_failed"]}
        response = api_client.patch(url, updated_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["comment"] == FINDINGS["comment_failed"]

        # `scan` can't be changed
        assert str(response.data["scan_id"]) != str(self.scan_alternative.id)
        assert str(response.data["scan_id"]) == str(self.scan.id)

    def test_finding_post_not_allowed(self, api_client):
        """Test that POST is not allowed for findings (read-only except updates)"""

        url = reverse("scan-findings-list", kwargs={"scan_pk": self.scan.id})
        finding_data = {"check_parent": str(self.check_0.id), "success": True, "comment": "New finding"}
        response = api_client.post(url, finding_data, format="json")

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_finding_delete_not_allowed(self, api_client):
        """Test that DELETE is not allowed for findings"""

        url = reverse("scan-findings-detail", kwargs={"scan_pk": self.scan.id, "pk": self.finding.id})
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestWorkflow:
    """End-to-end integration tests simulating real workflows"""

    def test_complete_workflow(self, api_client, worker):
        """Test a complete workflow: create provider → checks → scan → findings"""

        # Create a provider
        provider_url = reverse("providers-list")
        provider_data = {"name": PROVIDERS["aws"]}
        provider_response = api_client.post(provider_url, provider_data, format="json")
        assert provider_response.status_code == status.HTTP_201_CREATED
        provider_id = provider_response.data["id"]

        # Create checks for the provider
        checks_url = reverse("provider-checks-list", kwargs={"provider_pk": provider_id})
        check_data_list = [{"name": CHECKS["aws_s3"]}, {"name": CHECKS["aws_ec2"]}, {"name": CHECKS["aws_iam"]}]

        check_ids = []
        for check_data in check_data_list:
            check_response = api_client.post(checks_url, check_data, format="json")
            assert check_response.status_code == status.HTTP_201_CREATED
            check_ids.append(check_response.data["id"])

        # Create a scan
        scan_url = reverse("scans-list")
        scan_data = {
            "provider_id": provider_id,
            "name": SCANS["production"],
            "comment": SCANS["comment_weekly"],
        }
        scan_response = api_client.post(scan_url, scan_data, format="json")
        assert scan_response.status_code == status.HTTP_201_CREATED
        scan_id = scan_response.data["id"]

        # Verify scan was created as pending
        scan_detail_url = reverse("scans-detail", kwargs={"pk": scan_id})
        scan_detail_response = api_client.get(scan_detail_url)
        assert scan_detail_response.status_code == status.HTTP_200_OK
        assert scan_detail_response.data["status"] == Scan.Status.PENDING

        # Check the scan status
        scan_status_url = reverse("scans-status", kwargs={"pk": scan_id})
        status_response = api_client.get(scan_status_url)
        assert status_response.status_code == status.HTTP_200_OK
        assert status_response.data["status"] == Scan.Status.PENDING

        # List findings for the scan, 0, as it has not been processed yet
        findings_url = reverse("scan-findings-list", kwargs={"scan_pk": scan_id})
        findings_response = api_client.get(findings_url)
        assert findings_response.status_code == status.HTTP_200_OK
        assert len(findings_response.data["results"]) == 0

        # Run the worker to process the scan task
        worker()

        # Verify scan was processed and has findings
        scan = Scan.objects.get(id=scan_id)
        assert scan.status == Scan.Status.COMPLETED
        findings_response = api_client.get(findings_url)
        assert findings_response.status_code == status.HTTP_200_OK
        if scan.status == Scan.Status.COMPLETED:
            assert len(findings_response.data["results"]) == 3

        # Update findings
        if findings_response.data["results"]:
            finding_id = findings_response.data["results"][0]["id"]
            finding_detail_url = reverse("scan-findings-detail", kwargs={"scan_pk": scan_id, "pk": finding_id})
            finding_update_data = {"comment": FINDINGS["comment_passed"]}
            finding_update_response = api_client.patch(finding_detail_url, finding_update_data, format="json")
            assert finding_update_response.status_code == status.HTTP_200_OK
            assert finding_update_response.data["comment"] == FINDINGS["comment_passed"]
