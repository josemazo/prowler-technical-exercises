from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from api import views

router = DefaultRouter()
router.register(r"health", views.HealthViewSet, basename="health")
router.register(r"providers", views.ProviderViewSet, basename="providers")

providers_router = NestedDefaultRouter(router, r"providers", lookup="provider")
providers_router.register(r"checks", views.CheckViewSet, basename="provider-checks")

router.register(r"scans", views.ScanViewSet, basename="scans")

scans_router = NestedDefaultRouter(router, r"scans", lookup="scan")
scans_router.register(r"findings", views.FindingViewSet, basename="scan-findings")

urlpatterns = router.urls + providers_router.urls + scans_router.urls
