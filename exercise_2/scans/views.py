from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from scans import models, serializers


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

    # Also check `provider` on URL
    def perform_create(self, serializer):
        provider_id = self.kwargs["provider_pk"]
        provider = get_object_or_404(models.Provider, pk=provider_id)
        serializer.save(provider=provider)


class ScanViewSet(ModelViewSet):
    queryset = models.Scan.objects.all().annotate(
        checks_total=Count("provider__checks", distinct=True),
        checks_executed=Count("findings", distinct=True),
        checks_pending=Count("provider__checks", distinct=True) - Count("findings", distinct=True),
        checks_success=Count("findings", filter=Q(findings__success=True), distinct=True),
        checks_failed=Count("findings", filter=Q(findings__success=False), distinct=True),
    )
    serializer_class = serializers.ScanSerializer

    # And here too check `provider` on URL
    def perform_create(self, serializer):
        provider_id = self.request.data["provider_id"]
        provider = get_object_or_404(models.Provider, pk=provider_id)
        serializer.save(provider=provider)

    # This action is not really needed, beacuse we can use the regular `/scans/<scan_id>/` endpoint to get the status
    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        scan = self.get_object()
        return Response({"status": scan.status})


class FindingViewSet(ModelViewSet):
    serializer_class = serializers.FindingSerializer
    http_method_names = ["get", "put", "patch"]

    def get_queryset(self):
        scan_id = self.kwargs["scan_pk"]
        get_object_or_404(models.Scan, pk=scan_id)
        return models.Finding.objects.filter(scan_id=scan_id)

    def perform_create(self, serializer):
        scan_id = self.kwargs["scan_pk"]
        scan = get_object_or_404(models.Scan, pk=scan_id)
        serializer.save(scan=scan)
