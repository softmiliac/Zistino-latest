from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample

from .models import Configuration
from .serializers import ConfigurationSerializer, ConfigRequestSerializer


@extend_schema(
    tags=['Customer'],
    operation_id='configurations_client_search',
    request=ConfigRequestSerializer,
    examples=[
        OpenApiExample(
            'Search by name',
            description='Search configuration by name',
            value={
                "name": "delivery_time",
                "type": 1
            }
        ),
        OpenApiExample(
            'Search by type',
            description='Search configurations by type',
            value={
                "name": "",
                "type": 1
            }
        ),
        OpenApiExample(
            'Get all',
            description='Get all active configurations',
            value={
                "name": "",
                "type": 0
            }
        )
    ]
)
class ConfigurationSearchView(APIView):
    """Search configurations - matches configurations/client/search endpoint."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Search configurations by name and/or type."""
        serializer = ConfigRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        queryset = Configuration.objects.filter(is_active=True)

        # Filter by name if provided
        if data.get('name'):
            queryset = queryset.filter(name__icontains=data['name'])

        # Filter by type if provided and not 0
        if data.get('type', 0) > 0:
            queryset = queryset.filter(type=data['type'])

        configs = queryset.order_by('name')
        serializer = ConfigurationSerializer(configs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Configurations'])
class ConfigurationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing configurations (admin use)."""
    queryset = Configuration.objects.all()
    serializer_class = ConfigurationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Configuration.objects.all()

