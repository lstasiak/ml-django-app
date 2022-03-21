from apps.endpoints.models import (MLAlgorithm, MLAlgorithmStatus, MLEndpoint,
                                   MLRequest)
from apps.endpoints.serializers import (MLAlgorithmSerializer,
                                        MLAlgorithmStatusSerializer,
                                        MLEndpointSerializer,
                                        MLRequestSerializer)
from django.shortcuts import render
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.viewsets import GenericViewSet


class MLEndpointViewSet(
    RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = MLEndpointSerializer
    queryset = MLEndpoint.objects.all()


class MLAlgorithmViewSet(
    RetrieveModelMixin, ListModelMixin, GenericViewSet
):
    serializer_class = MLAlgorithmSerializer
    queryset = MLAlgorithm.objects.all()


def deactivate_other_statuses(instance):
    old_statuses = MLAlgorithmStatus.objects.filter(
        parent_mlalgorithm=instance.parent_mlalgorithm,
        created_at__lt=instance.created_at,
        active=True,
    )
    for i in range(len(old_statuses)):
        old_statuses[i].active = False
    MLAlgorithmStatus.objects.bulk_update(old_statuses, ["active"])


class MLAlgorithmStatusViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
    CreateModelMixin,
):
    serializer_class = MLAlgorithmStatusSerializer
    queryset = MLAlgorithmStatus.objects.all()

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                instance = serializer.save(active=True)
                # set active=False for other statuses
                deactivate_other_statuses(instance)
        except Exception as e:
            raise APIException(str(e))


class MLRequestViewSet(
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
    UpdateModelMixin,
):

    serializer_class = MLRequestSerializer
    queryset = MLRequest.objects.all()
