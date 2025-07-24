from rest_framework import serializers
from rest_framework_nested import serializers as serializers_nested

from scans import models

BASE_FIELDS = ["id", "created_at", "updated_at"]


class ProviderSerializer(serializers.HyperlinkedModelSerializer):
    checks_total = serializers.IntegerField(read_only=True)
    checks_url = serializers.HyperlinkedIdentityField(
        view_name="provider-checks-list", read_only=True, lookup_url_kwarg="provider_pk"
    )

    class Meta:
        model = models.Provider
        fields = BASE_FIELDS + ["name", "checks_total", "url", "checks_url"]
        read_only_fields = BASE_FIELDS + ["checks_total", "url", "checks_url"]
        extra_kwargs = {
            "url": {"view_name": "providers-detail", "read_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Remove URLs for JSON format
        if request and request.query_params.get("format") == "json":
            representation.pop("url", None)
            representation.pop("checks_url", None)

        return representation


class CheckSerializer(serializers_nested.NestedHyperlinkedModelSerializer):
    provider_url = serializers.HyperlinkedRelatedField(source="provider", read_only=True, view_name="providers-detail")

    parent_lookup_kwargs = {
        "provider_pk": "provider__pk",
    }

    class Meta:
        model = models.Check
        fields = BASE_FIELDS + ["provider_id", "name", "url", "provider_url"]
        read_only_fields = BASE_FIELDS + ["provider_id", "url", "provider_url"]
        extra_kwargs = {
            "url": {"view_name": "provider-checks-detail", "read_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Remove URLs for JSON format
        if request and request.query_params.get("format") == "json":
            representation.pop("url", None)
            representation.pop("provider_url", None)

        return representation


class ScanSerializer(serializers.ModelSerializer):
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

    class Meta:
        model = models.Scan
        fields = BASE_FIELDS + [
            "provider_id",
            "status",
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
            "url",
            "status_url",
            "findings_url",
        ]
        read_only_fields = BASE_FIELDS + [
            "status",
            "started_at",
            "finished_at",
            "checks_total",
            "checks_executed",
            "checks_pending",
            "checks_success",
            "checks_failed",
            "success",
            "url",
            "status_url",
            "findings_url",
        ]
        extra_kwargs = {
            "url": {"view_name": "scans-detail", "read_only": True},
        }

    # Prevent `provider` from being updated
    def update(self, instance, validated_data):
        validated_data.pop("provider_id", None)
        validated_data.pop("provider", None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Remove URLs for JSON format
        if request and request.query_params.get("format") == "json":
            representation.pop("url", None)
            representation.pop("status_url", None)
            representation.pop("findings_url", None)

        return representation


class FindingSerializer(serializers_nested.NestedHyperlinkedModelSerializer):
    check_id = serializers.UUIDField(read_only=True, source="check_parent_id")
    scan_url = serializers.HyperlinkedRelatedField(source="scan", read_only=True, view_name="scans-detail")

    parent_lookup_kwargs = {
        "scan_pk": "scan__pk",
    }

    class Meta:
        model = models.Finding
        fields = BASE_FIELDS + ["scan_id", "check_id", "success", "comment", "url", "scan_url"]
        read_only_fields = BASE_FIELDS + ["scan_id", "check_id", "success", "url", "scan_url"]
        extra_kwargs = {
            "url": {"view_name": "scan-findings-detail", "read_only": True},
        }

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get("request")

        # Remove URLs for JSON format
        if request and request.query_params.get("format") == "json":
            representation.pop("url", None)
            representation.pop("scan_url", None)

        return representation
