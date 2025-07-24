from uuid import UUID

import uuid_utils

from django.core.exceptions import ValidationError
from django.db import models


# uuid_utils is missing needed Python's UUID properties
# Note: Python 3.14 and Postgres 18 will have native support for UUIDv7
def generate_uuid7():
    return UUID(str(uuid_utils.uuid7()))


# I'm a declared enemy of using time zones in the backend
class DateTimeUTCField(models.DateTimeField):
    def db_type(self, connection):
        return "timestamp"  # This works on most SQL databases


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=generate_uuid7, editable=False)
    created_at = DateTimeUTCField(auto_now_add=True)
    updated_at = DateTimeUTCField(auto_now=True)

    class Meta:
        abstract = True


"""
TODO: A note to myself
Taking a look to the Prowler documentation, it seems that `checks` are main entities: definitions of what to _check_ in
each service of each provider.
`scans` are the executions of those `checks` against a specific provider, at a specific time, by a specific user.
So, `findings` are related directly to `scans` and `checks`: what was found during a specific check of a specific scan.

But `Define relationships between models (e.g., a scan can have many checks, a check can have  many findings)` striked
me, and I developed those models, the urls (`rest_framework_nested`) and views accordingly.

I'll change it for what I found in the Prowler documentation, adding `providers`, as having non-dependant `checks` looks too simple.
"""


class Provider(BaseModel):
    name = models.CharField(max_length=32, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Check(BaseModel):
    provider = models.ForeignKey(Provider, related_name="checks", on_delete=models.CASCADE)
    name = models.CharField(max_length=128)

    class Meta:
        ordering = ["provider__name", "name"]
        unique_together = ["provider", "name"]

    def __str__(self):
        return f"{self.provider.name} - {self.name}"


class Scan(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        IN_PROGRESS = "in_progress"
        COMPLETED = "completed"
        FAILED = "failed"

    provider = models.ForeignKey(
        Provider, related_name="scans", on_delete=models.CASCADE
    )  # Maybe if provider is deleted the scans should be saved
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    started_at = DateTimeUTCField(null=True, blank=True)
    finished_at = DateTimeUTCField(null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.provider.name} - {self.status} - {self.name}"

    # It's not the most efficient way to do this, but just for doing it
    @property
    def success(self):
        # If not completed, None
        if self.status != self.Status.COMPLETED:
            return None

        # If no findings, False
        findings = self.findings.all()
        if not findings.exists():
            return False

        # Only True if all findings have succeeded
        return all(finding.success for finding in findings)


class Finding(BaseModel):
    scan = models.ForeignKey(Scan, related_name="findings", on_delete=models.CASCADE)
    check_parent = models.ForeignKey(
        Check, related_name="findings", on_delete=models.CASCADE, verbose_name="check"
    )  # `check` is already used by Django
    success = models.BooleanField(default=False)
    comment = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ["scan", "check_parent"]

    def __str__(self):
        return f"{self.scan.provider.name} - {self.scan.name} - {self.check_parent.name} - {self.success}"

    # Validate providers of the scan and the check are the same
    def clean(self):
        super().clean()
        if self.scan.provider != self.check_parent.provider:
            raise ValidationError("`scan.provider` and `check.provider` must be the same.")
