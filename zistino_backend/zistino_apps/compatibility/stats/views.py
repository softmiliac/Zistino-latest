"""
Views for Stats compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from django.contrib.auth import get_user_model

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.compatibility.roles.models import Role
from zistino_apps.products.models import Product, Brand

User = get_user_model()


@extend_schema(
    tags=['Stats'],
    operation_id='stats_get',
    summary='Get general statistics',
    description='Returns general statistics including counts for products, brands, users, and roles matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='General statistics',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": {
                            "productCount": 29,
                            "brandCount": 4,
                            "userCount": 4,
                            "roleCount": 22,
                            "dataEnterBarChart": [],
                            "productByBrandTypePieChart": None
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class StatsView(APIView):
    """GET /api/v1/stats - Get general statistics"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get general statistics matching old Swagger format."""
        try:
            # Get counts
            product_count = Product.objects.count()
            brand_count = Brand.objects.count()
            user_count = User.objects.count()
            role_count = Role.objects.count()
            
            stats_data = {
                "productCount": product_count,
                "brandCount": brand_count,
                "userCount": user_count,
                "roleCount": role_count,
                "dataEnterBarChart": [],
                "productByBrandTypePieChart": None
            }
            
            return create_success_response(data=stats_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['Stats'],
    operation_id='stats_chart',
    summary='Get statistics for charts',
    description='Returns statistics for chart visualization matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Chart statistics',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "productCount": 0,
                        "brandCount": 0,
                        "userCount": 4,
                        "roleCount": 22,
                        "dataEnterBarChart": [],
                        "productByBrandTypePieChart": None
                    }
                )
            ]
        )
    }
)
class StatsChartView(APIView):
    """GET /api/v1/stats/chart - Get statistics for charts"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get chart statistics matching old Swagger format."""
        try:
            # Get counts (chart endpoint returns 0 for productCount and brandCount)
            user_count = User.objects.count()
            role_count = Role.objects.count()
            
            chart_data = {
                "productCount": 0,
                "brandCount": 0,
                "userCount": user_count,
                "roleCount": role_count,
                "dataEnterBarChart": [],
                "productByBrandTypePieChart": None
            }
            
            # Old Swagger returns data directly (not wrapped in {data, messages, succeeded})
            return Response(chart_data, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
