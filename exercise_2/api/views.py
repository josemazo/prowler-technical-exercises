from datetime import timedelta

from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from procrastinate.contrib.django import models as models_procrastinate
from procrastinate.exceptions import ProcrastinateException
from rest_framework import status as http_status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet

from api import models, serializers, tasks


class HealthViewSet(ViewSet):
    """`GET` checks in one query if the database and procrastinate are healthy"""

    def list(self, request):
        try:
            thirty_seconds_ago = timezone.now() - timedelta(seconds=30)
            has_active_worker = models_procrastinate.ProcrastinateWorker.objects.filter(
                last_heartbeat__gt=thirty_seconds_ago
            ).exists()

            if has_active_worker:
                return Response({"status": "healthy"}, status=http_status.HTTP_200_OK)
            else:
                raise ProcrastinateException("No active worker found in the last 30 seconds")

        except Exception:
            return Response({"status": "unhealthy"}, status=http_status.HTTP_503_SERVICE_UNAVAILABLE)


class ProviderViewSet(ModelViewSet):
    queryset = models.Provider.objects.all().annotate(checks_total=Count("checks", distinct=True))
    serializer_class = serializers.ProviderSerializer


class CheckViewSet(ModelViewSet):
    serializer_class = serializers.CheckSerializer

    # Check `provider` set on the URL exists
    def get_queryset(self):
        provider_id = self.kwargs["provider_pk"]
        get_object_or_404(models.Provider, pk=provider_id)
        return models.Check.objects.filter(provider_id=provider_id)

    # Also here check `provider` on URL
    def perform_create(self, serializer):
        provider_id = self.kwargs["provider_pk"]
        provider = get_object_or_404(models.Provider, pk=provider_id)
        serializer.save(provider=provider)


class ScanViewSet(ModelViewSet):
    # As in `models.Scan.success`, check counts are costly, just for showing calculated fields in views and serializers
    queryset = models.Scan.objects.all().annotate(
        checks_total=Count("provider__checks", distinct=True),
        checks_executed=Count("findings", distinct=True),
        checks_pending=Count("provider__checks", distinct=True) - Count("findings", distinct=True),
        checks_success=Count("findings", filter=Q(findings__success=True), distinct=True),
        checks_failed=Count("findings", filter=Q(findings__success=False), distinct=True),
    )
    serializer_class = serializers.ScanSerializer

    # Check `provider` set on POST data exists
    def perform_create(self, serializer):
        provider_id = self.request.data["provider_id"]
        provider = get_object_or_404(models.Provider, pk=provider_id)
        serializer.save(provider=provider)

        tasks.start_scan.defer(scan_id=str(serializer.instance.id))

    # This action is not really needed, beacuse we can use the regular `/scans/<scan_id>/` endpoint to get the status
    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        scan = self.get_object()
        return Response({"status": scan.status})


class FindingViewSet(ModelViewSet):
    serializer_class = serializers.FindingSerializer
    http_method_names = ["options", "get", "put", "patch"]  # No POST or DELETE allowed

    # Check `scan` set on the URL exists
    def get_queryset(self):
        scan_id = self.kwargs["scan_pk"]
        get_object_or_404(models.Scan, pk=scan_id)
        return models.Finding.objects.filter(scan_id=scan_id)

    # Also here check `scan` on URL
    def perform_create(self, serializer):
        scan_id = self.kwargs["scan_pk"]
        scan = get_object_or_404(models.Scan, pk=scan_id)
        serializer.save(scan=scan)
