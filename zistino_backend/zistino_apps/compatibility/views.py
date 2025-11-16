"""
Compatibility views for Flutter app endpoints.
These views provide backward compatibility by mapping old endpoint patterns to new views.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from drf_spectacular.utils import extend_schema

from zistino_apps.deliveries.models import Delivery
from zistino_apps.deliveries.serializers import DeliverySerializer


@extend_schema(tags=['Compatibility'], deprecated=True)
class DriverDeliveryMyRequestsView(APIView):
    """
    Compatibility view for driverdelivery/myrequests endpoint.
    Returns all deliveries for the authenticated driver.
    Flutter expects: POST /api/v1/driverdelivery/myrequests (with optional filters in body)
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """
        Get all deliveries for the authenticated driver.
        Accepts LazyRQM format with optional filters in request body:
        - pageNumber: page number (0-indexed in Flutter, 1-indexed here)
        - pageSize: number of items per page
        - keyword: search keyword (optional)
        - status: filter by status (optional)
        """
        # Get pagination parameters from request (LazyRQM format)
        page_number = int(request.data.get('pageNumber', 0))
        page_size = int(request.data.get('pageSize', 100))
        keyword = request.data.get('keyword', '')
        status_filter = request.data.get('status')
        
        # Convert 0-indexed pageNumber to 1-indexed page
        page = page_number + 1 if page_number >= 0 else 1
        
        # Calculate offset
        offset = (page - 1) * page_size
        
        # Get deliveries for the driver
        deliveries = Delivery.objects.filter(driver=request.user)
        
        # Apply keyword filter if provided
        if keyword:
            deliveries = deliveries.filter(
                Q(order__user__phone_number__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(order__id__icontains=keyword)
            )
        
        # Apply status filter if provided
        if status_filter is not None:
            deliveries = deliveries.filter(status=status_filter)
        
        # Order by created_at descending
        deliveries = deliveries.order_by('-created_at')
        
        # Apply pagination
        total_count = deliveries.count()
        deliveries = deliveries[offset:offset + page_size]
        
        serializer = DeliverySerializer(deliveries, many=True)
        
        # Return in format that Flutter might expect
        # Flutter apps often expect BaseResponse format
        return Response({
            'items': serializer.data,
            'total': total_count,
            'pageNumber': page_number,
            'pageSize': page_size
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        """GET method also supported for compatibility"""
        return self.post(request)

