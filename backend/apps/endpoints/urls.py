from apps.endpoints.views import (MLAlgorithmStatusViewSet, MLAlgorithmViewSet,
                                  MLEndpointViewSet, MLRequestViewSet,
                                  PredictView)
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

router = DefaultRouter(trailing_slash=False)
router.register(r"mlendpoints", MLEndpointViewSet, basename="mlendpoints")
router.register(r"mlalgorithms", MLAlgorithmViewSet, basename="mlalgorithms")
router.register(r"mlalgorithmstatuses", MLAlgorithmStatusViewSet, basename="mlalgorithmstatuses")
router.register(r"mlrequests", MLRequestViewSet, basename="mlrequests")

urlpatterns = [
    url(r"^api/v1/", include(router.urls)),
    url(
        r"^api/v1/(?P<endpoint_name>.+)/predict$", PredictView.as_view(), name="predict"
    ),
]
