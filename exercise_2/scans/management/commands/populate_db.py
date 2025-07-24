import os
import random

from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from scans.models import Check, Finding, Provider, Scan

User = get_user_model()


class Command(BaseCommand):
    help = "Populate the database with initial data for testing"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing data before populating",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write("Clearing existing data...")
            self.clear_data()

        with transaction.atomic():
            self.create_superuser()
            providers = self.create_providers()
            self.create_checks(providers)
            self.create_scans(providers)

        self.stdout.write(self.style.SUCCESS("Successfully populated the database!"))

    def clear_data(self):
        """Clear all existing data"""
        Provider.objects.all().delete()  # Let's use ON DELETE CASCADE
        User.objects.filter(is_superuser=True).delete()
        self.stdout.write("Existing data cleared.")

    def create_superuser(self):
        """Create a superuser if it doesn't exist"""
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_superuser(
                username=os.environ.get("SUPER_USERNAME"),
                email=os.environ.get("SUPER_EMAIL"),
                password=os.environ.get("SUPER_PASSWORD"),
            )
            self.stdout.write(f"Created superuser: {user.username}")
        else:
            self.stdout.write("Superuser already exists, skipping...")

    def create_providers(self):
        providers_data = [
            {"name": "aws"},
            {"name": "azure"},
            {"name": "gcp"},
        ]

        providers = {}
        for provider_data in providers_data:
            provider, created = Provider.objects.get_or_create(**provider_data)
            providers[provider.name] = provider
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: Provider {provider.name}")

        return providers

    def create_checks(self, providers):
        checks_data = [
            # AWS
            {"provider": providers["aws"], "name": "EC2 Security Groups Open to World"},
            {"provider": providers["aws"], "name": "S3 Bucket Public Read Access"},
            # Azure
            {"provider": providers["azure"], "name": "Network Security Groups Allow All Inbound"},
            {"provider": providers["azure"], "name": "Storage Account Public Access Enabled"},
            {"provider": providers["azure"], "name": "Key Vault Soft Delete Disabled"},
            # GCP
            {"provider": providers["gcp"], "name": "Compute Instance Default Service Account"},
            {"provider": providers["gcp"], "name": "Cloud Storage Bucket Public Access"},
            {"provider": providers["gcp"], "name": "Firewall Rules Allow All Traffic"},
            {"provider": providers["gcp"], "name": "Cloud SQL Instance Public IP"},
        ]

        for check_data in checks_data:
            check, created = Check.objects.get_or_create(provider=check_data["provider"], name=check_data["name"])
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: Check {check.provider.name} - {check.name}")

    def create_scans(self, providers):
        scans_data = [
            # AWS
            {
                "provider": providers["aws"],
                "name": "Production Environment Scan",
                "status": Scan.Status.COMPLETED,
                "comment": "Weekly security scan of production AWS environment",
            },
            # Azure
            {
                "provider": providers["azure"],
                "name": "Development Environment Scan",
                "status": Scan.Status.IN_PROGRESS,
                "comment": "Development AZure environment security assessment",
            },
            # GCP
            {
                "provider": providers["gcp"],
                "name": "Staging Environment Scan",
                "status": Scan.Status.PENDING,
                "comment": "Scan for new GCP resources deployment",
            },
        ]

        for scan_data in scans_data:
            scan, created = Scan.objects.get_or_create(
                provider=scan_data["provider"],
                name=scan_data["name"],
                defaults={"status": scan_data["status"], "comment": scan_data["comment"]},
            )
            status = "Created" if created else "Already exists"
            self.stdout.write(f"{status}: Scan {scan.provider.name} - {scan.name}")

            if scan.status == Scan.Status.COMPLETED and created:
                scan.started_at = datetime.now()
                scan.finished_at = datetime.now()
                scan.save()
                self.create_sample_findings(scan)

            elif scan.status == Scan.Status.IN_PROGRESS and created:
                scan.started_at = datetime.now()
                scan.save()
                self.create_sample_findings(scan, False)

    def create_sample_findings(self, scan, all_findings=True):
        checks = Check.objects.filter(provider=scan.provider)

        for check in checks:
            if not all_findings and random.random() < 0.5:
                continue

            success = random.random() < 0.5
            comment = f"Check error `{check.name}` with Manolo" if not success else "Check passed successfully"

            finding, created = Finding.objects.get_or_create(
                scan=scan, check_parent=check, defaults={"success": success, "comment": comment}
            )

            if created:
                self.stdout.write(f"Created: Finding {check.name} - {'SUCCESS' if success else 'FAILURE'}")
