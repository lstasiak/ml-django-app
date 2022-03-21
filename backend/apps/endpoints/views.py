import json

from apps.endpoints.models import (MLAlgorithm, MLAlgorithmStatus, MLEndpoint,
                                   MLRequest)
from apps.endpoints.serializers import (MLAlgorithmSerializer,
                                        MLAlgorithmStatusSerializer,
                                        MLEndpointSerializer,
                                        MLRequestSerializer)
from apps.ml.mlregistry import MLRegistry
from django.shortcuts import render
from numpy.random import rand
from rest_framework import status, views
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,
                                   RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from server.wsgi import registry


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


class PredictView(views.APIView):

    def post(self, request, endpoint_name, format=None):

        algorithm_status = self.request.query_params.get("status", "production")
        algorithm_version = self.request.query_params.get("version")

        algorithms = MLAlgorithm.objects.filter(parent_endpoint__name = endpoint_name, status__status = algorithm_status, status__active=True)

        if algorithm_version is not None:
            algorithms = algorithms.filter(version = algorithm_version)

        if len(algorithms) == 0:
            return Response(
                {"status": "Error", "message": "ML algorithm is not available"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if len(algorithms) != 1 and algorithm_status != "ab_testing":
            return Response(
                {"status": "Error", "message": "ML algorithm selection is ambiguous. Please specify algorithm version."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        alg_index = 0
        if algorithm_status == "ab_testing":
            alg_index = 0 if rand() < 0.5 else 1

        algorithm_object = registry.endpoints[algorithms[alg_index].id]
        prediction = algorithm_object.compute_prediction(request.data)


        label = prediction["label"] if "label" in prediction else "error"
        ml_request = MLRequest(
            input_data=json.dumps(request.data),
            full_response=prediction,
            response=label,
            feedback="",
            parent_mlalgorithm=algorithms[alg_index],
        )
        ml_request.save()

        prediction["request_id"] = ml_request.id

        return Response(prediction)
