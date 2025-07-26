from django.conf import settings
from rest_framework import serializers
from rest_framework_nested import serializers as serializers_nested

from api import models

BASE_FIELDS = ["id", "created_at", "updated_at"]


class URLFieldsMixin:
    url_fields = []

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        if not settings.DEBUG or request.query_params.get("format") == "json":
            for field in self.url_fields:
                representation.pop(field, None)

        return representation


class ProviderSerializer(URLFieldsMixin, serializers.HyperlinkedModelSerializer):
    checks_total = serializers.IntegerField(read_only=True)
    checks_url = serializers.HyperlinkedIdentityField(
        view_name="provider-checks-list", read_only=True, lookup_url_kwarg="provider_pk"
    )
    # TODO: Comment about the urls

    class Meta:
        model = models.Provider
        url_fields = ["url", "checks_url"]
        fields = BASE_FIELDS + ["name", "checks_total"] + url_fields
        read_only_fields = BASE_FIELDS + ["checks_total"] + url_fields
        extra_kwargs = {
            "url": {"view_name": "providers-detail", "read_only": True},
        }

    url_fields = Meta.url_fields


class CheckSerializer(URLFieldsMixin, serializers_nested.NestedHyperlinkedModelSerializer):
    provider_url = serializers.HyperlinkedRelatedField(source="provider", read_only=True, view_name="providers-detail")

    parent_lookup_kwargs = {
        "provider_pk": "provider__pk",
    }

    class Meta:
        model = models.Check
        url_fields = ["url", "provider_url"]
        fields = BASE_FIELDS + ["provider_id", "name"] + url_fields
        read_only_fields = BASE_FIELDS + ["provider_id"] + url_fields
        extra_kwargs = {
            "url": {"view_name": "provider-checks-detail", "read_only": True},
        }

    url_fields = Meta.url_fields


class ScanSerializer(URLFieldsMixin, serializers.ModelSerializer):
    def __init__(self, *args, **kwargs):  # Making `provider_id` read-only when updating
        super().__init__(*args, **kwargs)

        if self.instance:
            self.fields["provider_id"].read_only = True

    provider_id = serializers.UUIDField()
    checks_total = serializers.IntegerField(read_only=True)
    checks_executed = serializers.IntegerField(read_only=True)
    checks_pending = serializers.IntegerField(read_only=True)
    checks_success = serializers.IntegerField(read_only=True)
    checks_failed = serializers.IntegerField(read_only=True)
    status_url = serializers.HyperlinkedIdentityField(view_name="scans-status", read_only=True, lookup_url_kwarg="pk")
    findings_url = serializers.HyperlinkedIdentityField(
        view_name="scan-findings-list", read_only=True, lookup_url_kwarg="scan_pk"
    )
    # TODO: Comment checks it's not the most efficient way to do this, but just for doing it

    class Meta:
        model = models.Scan
        url_fields = ["url", "status_url", "findings_url"]
        fields = (
            BASE_FIELDS
            + [
                "provider_id",
                "status",
                "failed_reason",
                "started_at",
                "finished_at",
                "name",
                "comment",
                "checks_total",
                "checks_executed",
                "checks_pending",
                "checks_success",
                "checks_failed",
                "success",
            ]
            + url_fields
        )
        read_only_fields = (
            BASE_FIELDS
            + [
                "status",
                "failed_reason",
                "started_at",
                "finished_at",
                "checks_total",
                "checks_executed",
                "checks_pending",
                "checks_success",
                "checks_failed",
                "success",
            ]
            + url_fields
        )
        extra_kwargs = {
            "url": {"view_name": "scans-detail", "read_only": True},
        }

    url_fields = Meta.url_fields


class FindingSerializer(URLFieldsMixin, serializers_nested.NestedHyperlinkedModelSerializer):
    check_id = serializers.UUIDField(read_only=True, source="check_parent_id")
    scan_url = serializers.HyperlinkedRelatedField(source="scan", read_only=True, view_name="scans-detail")

    parent_lookup_kwargs = {
        "scan_pk": "scan__pk",
    }

    class Meta:
        model = models.Finding
        url_fields = ["url", "scan_url"]
        fields = BASE_FIELDS + ["scan_id", "check_id", "success", "comment"] + url_fields
        read_only_fields = BASE_FIELDS + ["scan_id", "check_id", "success"] + url_fields
        extra_kwargs = {
            "url": {"view_name": "scan-findings-detail", "read_only": True},
        }

    url_fields = Meta.url_fields
