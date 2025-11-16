"""
Views for RepairRequests compatibility layer.
Provides all 13 endpoints matching Flutter app expectations.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample, OpenApiResponse
from django.contrib.auth import get_user_model
import random
import string

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.products.models import Product, Problem

from .models import RepairRequest, RepairRequestDetail, RepairRequestStatus, RepairRequestDocument, RepairRequestMessage
from .serializers import (
    RepairRequestSerializer,
    RepairRequestSearchRequestSerializer,
    RepairRequestClientSerializer,
    RepairRequestAnonymousClientSerializer,
    RepairRequestFollowupRequestSerializer,
    RepairRequestMessageRequestSerializer,
    RepairRequestCreateRequestSerializer,
    RepairRequestUpdateRequestSerializer,
    RepairRequestResponseSerializer,
    RepairRequestDetailResponseSerializer,
    RepairRequestStatusResponseSerializer,
    RepairRequestDocumentResponseSerializer,
    ProductResponseSerializer,
    ProblemResponseSerializer,
)

User = get_user_model()


def generate_tracking_code():
    """Generate a unique 8-digit tracking code."""
    while True:
        code = ''.join(random.choices(string.digits, k=8))
        if not RepairRequest.objects.filter(tracking_code=code).exists():
            return code


def serialize_repair_request_response(repair_request):
    """Serialize repair request to match old Swagger response format."""
    # Serialize product
    product_data = None
    if repair_request.product:
        master_image = None
        if repair_request.product.image:
            # Get the full URL or relative path
            try:
                master_image = repair_request.product.image.url
            except:
                master_image = str(repair_request.product.image) if repair_request.product.image else None
        
        product_data = {
            'id': str(repair_request.product.id),
            'name': repair_request.product.name,
            'masterImage': master_image,
            'description': repair_request.product.description or None,
        }
    
    # Serialize repair request details
    details_data = []
    for detail in repair_request.repair_request_details.all():
        problem_data = None
        if detail.problem:
            problem_data = {
                'id': detail.problem.id,
                'title': detail.problem.title,
            }
        
        details_data.append({
            'id': detail.id,
            'price': float(detail.price),
            'startRepairDate': detail.start_repair_date.isoformat() if detail.start_repair_date else None,
            'endRepairDate': detail.end_repair_date.isoformat() if detail.end_repair_date else None,
            'repairRequestId': repair_request.id,
            'problem': problem_data,
            'isCanceled': detail.is_canceled,
            'cancelationDescription': detail.cancelation_description or None,
        })
    
    # Serialize repair request statuses
    statuses_data = []
    for status_obj in repair_request.repair_request_statuses.all():
        statuses_data.append({
            'id': status_obj.id,
            'text': status_obj.text or None,
            'status': status_obj.status,
            'createdOn': status_obj.created_at.isoformat(),
        })
    
    # Serialize repair request documents
    documents_data = []
    for doc in repair_request.repair_request_documents.all():
        document_url = None
        if doc.document:
            try:
                document_url = doc.document.url
            except:
                document_url = str(doc.document) if doc.document else None
        elif doc.document_url:
            document_url = doc.document_url
        
        documents_data.append({
            'id': doc.id,
            'documentUrl': document_url,
            'description': doc.description or None,
        })
    
    return {
        'id': repair_request.id,
        'duration': repair_request.duration,
        'totalPrice': float(repair_request.total_price),
        'trackingCode': repair_request.tracking_code or None,
        'steps': repair_request.steps,
        'deliveryInformation': repair_request.delivery_information or None,
        'note': repair_request.note or None,
        'createRequestDate': repair_request.created_at.isoformat(),
        'userId': str(repair_request.user.id) if repair_request.user else None,
        'product': product_data,
        'email': repair_request.email or None,
        'fullName': repair_request.full_name or None,
        'gender': repair_request.gender,
        'address': repair_request.address or None,
        'zipCode': repair_request.zip_code or None,
        'city': repair_request.city or None,
        'phoneNumber': repair_request.phone_number or None,
        'companyName': repair_request.company_name or None,
        'companyNumber': repair_request.company_number or None,
        'vatNumber': repair_request.vat_number or None,
        'userType': repair_request.user_type,
        'requestType': repair_request.request_type,
        'deliveryMode': repair_request.delivery_mode,
        'deliveryDate': repair_request.delivery_date.isoformat() if repair_request.delivery_date else None,
        'repairRequestDetails': details_data,
        'repairRequestStatuses': statuses_data,
        'repairRequestDocuments': documents_data,
    }


@extend_schema(tags=['RepairRequests'])
class RepairRequestsViewSet(viewsets.ViewSet):
    """
    ViewSet for RepairRequests endpoints.
    
    Note: This is a placeholder until RepairRequest model is created.
    All endpoints return 501 NOT_IMPLEMENTED.
    """
    permission_classes = [IsAuthenticated, IsManager]

    def get_permissions(self):
        """Admin-only for most actions, AllowAny for client/anonymous endpoints."""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'search', 'converttoappointment']:
            return [IsAuthenticated(), IsManager()]
        elif self.action in ['client', 'anonymous_client', 'followup']:
            return [AllowAny()]
        return [IsAuthenticated(), IsManager()]

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_retrieve',
        summary='Retrieve a repair request by ID',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "duration": 0,
                                "totalPrice": 0,
                                "trackingCode": "86437489",
                                "steps": 1,
                                "deliveryInformation": "string",
                                "note": "string",
                                "createRequestDate": "2025-11-11T09:40:39.6189029",
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "product": {
                                    "id": "94860000-b419-c60d-2b41-08dc425c06b1",
                                    "name": "شامپو کلیر",
                                    "masterImage": "/uploads/app/4012b8b383fc43bd808880d292d1deae.webp",
                                    "description": "شامپو کلیر"
                                },
                                "email": "string",
                                "fullName": "string",
                                "gender": 0,
                                "address": "string",
                                "zipCode": "string",
                                "city": "string",
                                "phoneNumber": "string",
                                "companyName": "string",
                                "companyNumber": "string",
                                "vatNumber": "string",
                                "userType": 0,
                                "requestType": 0,
                                "deliveryMode": 0,
                                "deliveryDate": "2025-11-11T06:09:49.156",
                                "repairRequestDetails": [
                                    {
                                        "id": 1,
                                        "price": 0,
                                        "startRepairDate": "2025-11-11T06:09:49.156",
                                        "endRepairDate": "2025-11-11T06:09:49.156",
                                        "repairRequestId": 1,
                                        "problem": {
                                            "id": 1,
                                            "title": "new p"
                                        },
                                        "isCanceled": True,
                                        "cancelationDescription": "string"
                                    }
                                ],
                                "repairRequestStatuses": [
                                    {
                                        "id": 1,
                                        "text": "",
                                        "status": 0,
                                        "createdOn": "2025-11-11T06:10:39.8799143"
                                    }
                                ],
                                "repairRequestDocuments": []
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def retrieve(self, request, pk=None):
        """Retrieve a repair request by ID matching old Swagger format."""
        try:
            repair_request = RepairRequest.objects.prefetch_related(
                'repair_request_details__problem',
                'repair_request_statuses',
                'repair_request_documents'
            ).select_related('product', 'user').get(id=pk)
            
            response_data = serialize_repair_request_response(repair_request)
            return create_success_response(data=response_data, messages=[])
        except RepairRequest.DoesNotExist:
            return create_error_response(
                error_message=f'Repair request with ID "{pk}" not found.',
                status_code=status.HTTP_404_NOT_FOUND,
                errors={'id': [f'Repair request with ID "{pk}" not found.']}
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_update',
        summary='Update a repair request',
        request=RepairRequestUpdateRequestSerializer,
        examples=[
            OpenApiExample(
                'Update repair request',
                value={
                    'duration': 0,
                    'totalPrice': 0,
                    'steps': 0,
                    'deliveryInformation': 'string',
                    'note': 'string',
                    'createRequestDate': '2025-11-12T11:06:49.292Z',
                    'userId': 'string',
                    'productId': 'string',
                    'email': 'string',
                    'fullName': 'string',
                    'gender': 0,
                    'address': 'string',
                    'zipCode': 'string',
                    'city': 'string',
                    'phoneNumber': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'vatNumber': 'string',
                    'userType': 0,
                    'requestType': 0,
                    'deliveryMode': 0,
                    'deliveryDate': '2025-11-12T11:06:49.292Z',
                    'repairRequestDetails': [
                        {
                            'id': 0,
                            'price': 0,
                            'startRepairDate': '2025-11-12T11:06:49.292Z',
                            'endRepairDate': '2025-11-12T11:06:49.292Z',
                            'repairRequestId': 0,
                            'problemId': 0,
                            'isCanceled': True,
                            'cancelationDescription': 'string'
                        }
                    ],
                    'repairRequestStatuses': [
                        {
                            'id': 0,
                            'repairRequestId': 0,
                            'text': 'string',
                            'status': 0
                        }
                    ],
                    'repairRequestDocuments': [
                        {
                            'id': 0,
                            'repairRequestId': 0,
                            'fileUrl': 'string'
                        }
                    ]
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def update(self, request, pk=None):
        """Update a repair request matching old Swagger format."""
        try:
            serializer = RepairRequestUpdateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=pk)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request with ID "{pk}" not found.']}
                )
            
            validated_data = serializer.validated_data
            
            # Update main repair request fields
            if 'duration' in validated_data:
                repair_request.duration = validated_data['duration']
            if 'totalPrice' in validated_data:
                repair_request.total_price = validated_data['totalPrice']
            if 'steps' in validated_data:
                repair_request.steps = validated_data['steps']
            if 'deliveryInformation' in validated_data:
                repair_request.delivery_information = validated_data['deliveryInformation']
            if 'note' in validated_data:
                repair_request.note = validated_data['note']
            if 'email' in validated_data:
                repair_request.email = validated_data['email']
            if 'fullName' in validated_data:
                repair_request.full_name = validated_data['fullName']
            if 'gender' in validated_data:
                repair_request.gender = validated_data['gender']
            if 'address' in validated_data:
                repair_request.address = validated_data['address']
            if 'zipCode' in validated_data:
                repair_request.zip_code = validated_data['zipCode']
            if 'city' in validated_data:
                repair_request.city = validated_data['city']
            if 'phoneNumber' in validated_data:
                repair_request.phone_number = validated_data['phoneNumber']
            if 'companyName' in validated_data:
                repair_request.company_name = validated_data['companyName']
            if 'companyNumber' in validated_data:
                repair_request.company_number = validated_data['companyNumber']
            if 'vatNumber' in validated_data:
                repair_request.vat_number = validated_data['vatNumber']
            if 'userType' in validated_data:
                repair_request.user_type = validated_data['userType']
            if 'requestType' in validated_data:
                repair_request.request_type = validated_data['requestType']
            if 'deliveryMode' in validated_data:
                repair_request.delivery_mode = validated_data['deliveryMode']
            if 'deliveryDate' in validated_data:
                repair_request.delivery_date = validated_data['deliveryDate']
            
            # Update user if provided
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                    repair_request.user = user
                except User.DoesNotExist:
                    pass
            
            # Update product if provided
            if validated_data.get('productId'):
                try:
                    product = Product.objects.get(id=validated_data['productId'])
                    repair_request.product = product
                except Product.DoesNotExist:
                    pass
            
            repair_request.save()
            
            # Update repair request details
            if 'repairRequestDetails' in validated_data:
                details_data = validated_data['repairRequestDetails']
                for detail_data in details_data:
                    detail_id = detail_data.get('id', 0)
                    if detail_id and detail_id > 0:
                        # Update existing detail
                        try:
                            detail = RepairRequestDetail.objects.get(id=detail_id, repair_request=repair_request)
                            if 'price' in detail_data:
                                detail.price = detail_data['price']
                            if 'startRepairDate' in detail_data:
                                detail.start_repair_date = detail_data['startRepairDate']
                            if 'endRepairDate' in detail_data:
                                detail.end_repair_date = detail_data['endRepairDate']
                            if 'problemId' in detail_data and detail_data['problemId']:
                                try:
                                    problem = Problem.objects.get(id=detail_data['problemId'])
                                    detail.problem = problem
                                except Problem.DoesNotExist:
                                    pass
                            if 'isCanceled' in detail_data:
                                detail.is_canceled = detail_data['isCanceled']
                            if 'cancelationDescription' in detail_data:
                                detail.cancelation_description = detail_data['cancelationDescription']
                            detail.save()
                        except RepairRequestDetail.DoesNotExist:
                            pass
                    else:
                        # Create new detail
                        problem = None
                        if detail_data.get('problemId'):
                            try:
                                problem = Problem.objects.get(id=detail_data['problemId'])
                            except Problem.DoesNotExist:
                                pass
                        
                        RepairRequestDetail.objects.create(
                            repair_request=repair_request,
                            problem=problem,
                            price=detail_data.get('price', 0.0),
                            start_repair_date=detail_data.get('startRepairDate'),
                            end_repair_date=detail_data.get('endRepairDate'),
                            is_canceled=detail_data.get('isCanceled', False),
                            cancelation_description=detail_data.get('cancelationDescription')
                        )
            
            # Update repair request statuses
            if 'repairRequestStatuses' in validated_data:
                statuses_data = validated_data['repairRequestStatuses']
                for status_data in statuses_data:
                    status_id = status_data.get('id', 0)
                    if status_id and status_id > 0:
                        # Update existing status
                        try:
                            status_obj = RepairRequestStatus.objects.get(id=status_id, repair_request=repair_request)
                            if 'text' in status_data:
                                status_obj.text = status_data['text']
                            if 'status' in status_data:
                                status_obj.status = status_data['status']
                            status_obj.save()
                        except RepairRequestStatus.DoesNotExist:
                            pass
                    else:
                        # Create new status
                        RepairRequestStatus.objects.create(
                            repair_request=repair_request,
                            text=status_data.get('text', ''),
                            status=status_data.get('status', 0)
                        )
            
            # Update repair request documents
            if 'repairRequestDocuments' in validated_data:
                documents_data = validated_data['repairRequestDocuments']
                for doc_data in documents_data:
                    doc_id = doc_data.get('id', 0)
                    if doc_id and doc_id > 0:
                        # Update existing document
                        try:
                            doc = RepairRequestDocument.objects.get(id=doc_id, repair_request=repair_request)
                            if 'fileUrl' in doc_data:
                                doc.file_url = doc_data['fileUrl']
                            doc.save()
                        except RepairRequestDocument.DoesNotExist:
                            pass
                    else:
                        # Create new document
                        RepairRequestDocument.objects.create(
                            repair_request=repair_request,
                            file_url=doc_data.get('fileUrl', '')
                        )
            
            return create_success_response(data=repair_request.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_destroy',
        summary='Delete a repair request',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def destroy(self, request, pk=None):
        """Delete a repair request matching old Swagger format."""
        try:
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=pk)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request with ID "{pk}" not found.']}
                )
            
            repair_request_id = repair_request.id
            repair_request.delete()
            
            return create_success_response(data=repair_request_id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while deleting repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_create',
        summary='Create a new repair request',
        request=RepairRequestCreateRequestSerializer,
        examples=[
            OpenApiExample(
                'Create Repair Request (default)',
                value={
                    "duration": 0,
                    "totalPrice": 0,
                    "steps": 0,
                    "deliveryInformation": "string",
                    "note": "string",
                    "userId": "string",
                    "productId": "string",
                    "email": "string",
                    "fullName": "string",
                    "gender": 0,
                    "address": "string",
                    "zipCode": "string",
                    "city": "string",
                    "phoneNumber": "string",
                    "companyName": "string",
                    "companyNumber": "string",
                    "vatNumber": "string",
                    "userType": 0,
                    "requestType": 0,
                    "deliveryMode": 0,
                    "deliveryDate": "2025-11-11T06:11:27.784Z",
                    "repairRequestDetails": [
                        {
                            "price": 0,
                            "startRepairDate": "2025-11-11T06:11:27.784Z",
                            "endRepairDate": "2025-11-11T06:11:27.784Z",
                            "repairRequestId": 0,
                            "problemId": 0,
                            "isCanceled": True,
                            "cancelationDescription": "string"
                        }
                    ]
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def create(self, request):
        """Create a new repair request matching old Swagger format."""
        try:
            serializer = RepairRequestCreateRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user (if provided)
            user = None
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                except User.DoesNotExist:
                    # If user not found, continue without user (for anonymous requests)
                    pass
            
            # Get product (if provided)
            product = None
            if validated_data.get('productId'):
                try:
                    product = Product.objects.get(id=validated_data['productId'])
                except Product.DoesNotExist:
                    return create_error_response(
                        error_message=f'Product with ID "{validated_data["productId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'productId': [f'Product with ID "{validated_data["productId"]}" not found.']}
                    )
            
            # Generate tracking code
            tracking_code = generate_tracking_code()
            
            # Create repair request
            repair_request = RepairRequest.objects.create(
                user=user,
                product=product,
                duration=validated_data.get('duration', 0),
                total_price=validated_data.get('totalPrice', 0.0),
                tracking_code=tracking_code,
                steps=validated_data.get('steps', 0),
                delivery_information=validated_data.get('deliveryInformation'),
                note=validated_data.get('note'),
                email=validated_data.get('email'),
                full_name=validated_data.get('fullName'),
                gender=validated_data.get('gender', 0),
                address=validated_data.get('address'),
                zip_code=validated_data.get('zipCode'),
                city=validated_data.get('city'),
                phone_number=validated_data.get('phoneNumber'),
                company_name=validated_data.get('companyName'),
                company_number=validated_data.get('companyNumber'),
                vat_number=validated_data.get('vatNumber'),
                user_type=validated_data.get('userType', 0),
                request_type=validated_data.get('requestType', 0),
                delivery_mode=validated_data.get('deliveryMode', 0),
                delivery_date=validated_data.get('deliveryDate'),
                status='pending'
            )
            
            # Create initial status
            RepairRequestStatus.objects.create(
                repair_request=repair_request,
                text='',
                status=0  # Pending
            )
            
            # Create repair request details
            repair_request_details = validated_data.get('repairRequestDetails', [])
            for detail_data in repair_request_details:
                problem = None
                if detail_data.get('problemId'):
                    try:
                        problem = Problem.objects.get(id=detail_data['problemId'])
                    except Problem.DoesNotExist:
                        # If problem not found, continue without problem
                        pass
                
                RepairRequestDetail.objects.create(
                    repair_request=repair_request,
                    problem=problem,
                    price=detail_data.get('price', 0.0),
                    start_repair_date=detail_data.get('startRepairDate'),
                    end_repair_date=detail_data.get('endRepairDate'),
                    is_canceled=detail_data.get('isCanceled', False),
                    cancelation_description=detail_data.get('cancelationDescription')
                )
            
            return create_success_response(data=repair_request.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_search',
        summary='Search repair requests using available filters',
        request=RepairRequestSearchRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Search results with pagination',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "messages": [],
                            "succeeded": True,
                            "data": [
                                {
                                    "id": 0,
                                    "duration": 0,
                                    "totalPrice": 0,
                                    "trackingCode": "string",
                                    "steps": 0,
                                    "deliveryInformation": "string",
                                    "note": "string",
                                    "createRequestDate": "2025-11-11T06:41:56.275Z",
                                    "userId": "string",
                                    "product": {
                                        "id": "string",
                                        "name": "string",
                                        "masterImage": "string",
                                        "description": "string"
                                    },
                                    "email": "string",
                                    "fullName": "string",
                                    "gender": 0,
                                    "address": "string",
                                    "zipCode": "string",
                                    "city": "string",
                                    "phoneNumber": "string",
                                    "companyName": "string",
                                    "companyNumber": "string",
                                    "vatNumber": "string",
                                    "userType": 0,
                                    "requestType": 0,
                                    "deliveryMode": 0,
                                    "deliveryDate": "2025-11-11T06:41:56.275Z",
                                    "repairRequestDetails": [],
                                    "repairRequestStatuses": [],
                                    "repairRequestDocuments": [
                                        {
                                            "id": 0,
                                            "fileUrl": "string"
                                        }
                                    ]
                                }
                            ],
                            "currentPage": 0,
                            "totalPages": 0,
                            "totalCount": 0,
                            "pageSize": 0,
                            "hasPreviousPage": True,
                            "hasNextPage": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='search')
    def search(self, request):
        """Search repair requests matching old Swagger format."""
        try:
            serializer = RepairRequestSearchRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get pagination parameters
            page_number = validated_data.get('pageNumber', 0)
            page_size = validated_data.get('pageSize', 0)
            
            # Default pagination if not provided
            if page_number == 0:
                page_number = 1
            if page_size == 0:
                page_size = 20
            
            # Get keyword from request or advancedSearch
            keyword = validated_data.get('keyword', '').strip()
            advanced_search = validated_data.get('advancedSearch')
            if advanced_search and not keyword:
                keyword = (advanced_search.get('keyword') or '').strip()
            
            # Start with base queryset
            qs = RepairRequest.objects.all().prefetch_related(
                'repair_request_details__problem',
                'repair_request_statuses',
                'repair_request_documents'
            ).select_related('product', 'user')
            
            # Filter by userId
            user_id = validated_data.get('userId')
            if user_id and user_id.strip():
                try:
                    from uuid import UUID
                    UUID(user_id.strip())
                    qs = qs.filter(user_id=user_id.strip())
                except (ValueError, TypeError):
                    pass
            
            # Filter by productId
            product_id = validated_data.get('productId')
            if product_id and product_id.strip():
                try:
                    from uuid import UUID
                    UUID(product_id.strip())
                    qs = qs.filter(product_id=product_id.strip())
                except (ValueError, TypeError):
                    pass
            
            # Filter by requestType
            request_type = validated_data.get('requestType')
            if request_type is not None:
                qs = qs.filter(request_type=request_type)
            
            # Keyword search (search in multiple fields)
            if keyword:
                from django.db.models import Q
                qs = qs.filter(
                    Q(tracking_code__icontains=keyword) |
                    Q(full_name__icontains=keyword) |
                    Q(email__icontains=keyword) |
                    Q(phone_number__icontains=keyword) |
                    Q(note__icontains=keyword) |
                    Q(delivery_information__icontains=keyword) |
                    Q(address__icontains=keyword) |
                    Q(city__icontains=keyword) |
                    Q(zip_code__icontains=keyword) |
                    Q(company_name__icontains=keyword)
                )
            
            # Order by
            order_by = validated_data.get('orderBy', [])
            if order_by:
                order_fields = []
                for order_field in order_by:
                    if order_field and order_field.strip():
                        field_lower = order_field.lower().strip()
                        # Map common orderBy patterns
                        if 'date' in field_lower or 'created' in field_lower:
                            order_fields.append('-created_at')
                        elif 'price' in field_lower or 'total' in field_lower:
                            order_fields.append('-total_price')
                        elif 'status' in field_lower:
                            order_fields.append('status')
                        elif 'tracking' in field_lower or 'code' in field_lower:
                            order_fields.append('tracking_code')
                        elif 'name' in field_lower:
                            order_fields.append('full_name')
                if order_fields:
                    qs = qs.order_by(*order_fields)
            else:
                qs = qs.order_by('-created_at')
            
            # Get total count before pagination
            total = qs.count()
            
            # Apply pagination
            start = (page_number - 1) * page_size
            end = start + page_size
            items = qs[start:end] if page_size > 0 else qs
            
            # Serialize results (note: search response uses fileUrl instead of documentUrl and only id/fileUrl)
            results = []
            for repair_request in items:
                data = serialize_repair_request_response(repair_request)
                # Update documents format for search response: only id and fileUrl
                if data.get('repairRequestDocuments'):
                    updated_docs = []
                    for doc in data['repairRequestDocuments']:
                        file_url = doc.get('documentUrl') or doc.get('fileUrl')
                        updated_docs.append({
                            'id': doc.get('id'),
                            'fileUrl': file_url
                        })
                    data['repairRequestDocuments'] = updated_docs
                results.append(data)
            
            # Calculate pagination metadata
            total_pages = (total + page_size - 1) // page_size if page_size > 0 else 0
            has_previous_page = page_number > 1
            has_next_page = page_number < total_pages if total_pages > 0 else False
            
            # Create response with pagination (messages should be null for search endpoint)
            response = create_success_response(
                data=results,
                pagination={
                    'currentPage': page_number,
                    'totalPages': total_pages,
                    'totalCount': total,
                    'pageSize': page_size,
                    'hasPreviousPage': has_previous_page,
                    'hasNextPage': has_next_page
                }
            )
            
            return response
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while searching repair requests: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_client',
        summary='Create a repair request (client)',
        request=RepairRequestClientSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": "83944138",
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='client', permission_classes=[AllowAny])
    def client(self, request):
        """Create a repair request for authenticated client matching old Swagger format."""
        try:
            serializer = RepairRequestClientSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get user (if provided, otherwise use authenticated user)
            user = None
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                except User.DoesNotExist:
                    # If user not found, continue without user
                    pass
            elif request.user and request.user.is_authenticated:
                user = request.user
            
            # Get product (if provided)
            product = None
            if validated_data.get('productId'):
                try:
                    product = Product.objects.get(id=validated_data['productId'])
                except Product.DoesNotExist:
                    return create_error_response(
                        error_message=f'Product with ID "{validated_data["productId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'productId': [f'Product with ID "{validated_data["productId"]}" not found.']}
                    )
            
            # Generate tracking code
            tracking_code = generate_tracking_code()
            
            # Create repair request
            repair_request = RepairRequest.objects.create(
                user=user,
                product=product,
                duration=validated_data.get('duration', 0),
                total_price=validated_data.get('totalPrice', 0.0),
                tracking_code=tracking_code,
                steps=validated_data.get('steps', 0),
                delivery_information=validated_data.get('deliveryInformation'),
                note=validated_data.get('note'),
                email=validated_data.get('email'),
                full_name=validated_data.get('fullName'),
                gender=validated_data.get('gender', 0),
                address=validated_data.get('address'),
                zip_code=validated_data.get('zipCode'),
                city=validated_data.get('city'),
                phone_number=validated_data.get('phoneNumber'),
                company_name=validated_data.get('companyName'),
                company_number=validated_data.get('companyNumber'),
                vat_number=validated_data.get('vatNumber'),
                user_type=validated_data.get('userType', 0),
                request_type=validated_data.get('requestType', 0),
                delivery_mode=validated_data.get('deliveryMode', 0),
                delivery_date=validated_data.get('deliveryDate'),
                status='pending'
            )
            
            # Create initial status
            RepairRequestStatus.objects.create(
                repair_request=repair_request,
                text='',
                status=0  # Pending
            )
            
            # Create repair request details (simplified format - only price and problemId)
            repair_request_details = validated_data.get('repairRequestDetails', [])
            for detail_data in repair_request_details:
                problem = None
                if detail_data.get('problemId'):
                    try:
                        problem = Problem.objects.get(id=detail_data['problemId'])
                    except Problem.DoesNotExist:
                        # If problem not found, continue without problem
                        pass
                
                RepairRequestDetail.objects.create(
                    repair_request=repair_request,
                    problem=problem,
                    price=detail_data.get('price', 0.0),
                    start_repair_date=None,
                    end_repair_date=None,
                    is_canceled=False,
                    cancelation_description=None
                )
            
            # Return tracking code as string (not ID)
            return create_success_response(data=tracking_code, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_anonymous_client',
        summary='Create a repair request (anonymous client)',
        request=RepairRequestAnonymousClientSerializer,
        examples=[
            OpenApiExample(
                'Create anonymous repair request',
                value={
                    'duration': 0,
                    'totalPrice': 0,
                    'steps': 0,
                    'deliveryInformation': 'string',
                    'note': 'string',
                    'userId': '5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671',
                    'productId': '94860000-b419-c60d-2b41-08dc425c06b1',
                    'email': None,
                    'fullName': 'string',
                    'gender': 0,
                    'address': 'string',
                    'zipCode': 'string',
                    'city': 'string',
                    'phoneNumber': 'string',
                    'companyName': 'string',
                    'companyNumber': 'string',
                    'vatNumber': 'string',
                    'userType': 0,
                    'requestType': 0,
                    'deliveryMode': 0,
                    'deliveryDate': '2025-11-11T07:06:15.121Z',
                    'repairRequestDetails': [
                        {
                            'price': 0,
                            'problemId': 0
                        }
                    ]
                },
                request_only=True
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": "83944138",
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='anonymous-client', permission_classes=[AllowAny])
    def anonymous_client(self, request):
        """Create a repair request for anonymous client matching old Swagger format."""
        try:
            serializer = RepairRequestAnonymousClientSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get product (required)
            product = None
            if validated_data.get('productId'):
                try:
                    product = Product.objects.get(id=validated_data['productId'])
                except Product.DoesNotExist:
                    return create_error_response(
                        error_message=f'Product with ID "{validated_data["productId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'productId': [f'Product with ID "{validated_data["productId"]}" not found.']}
                    )
            
            # Get user if provided
            user = None
            if validated_data.get('userId'):
                try:
                    user = User.objects.get(id=validated_data['userId'])
                except User.DoesNotExist:
                    pass  # Allow anonymous if user not found
            
            # Generate tracking code
            tracking_code = generate_tracking_code()
            
            # Create repair request for anonymous user
            repair_request = RepairRequest.objects.create(
                user=user,  # Can be None for anonymous
                product=product,
                duration=validated_data.get('duration', 0),
                total_price=validated_data.get('totalPrice', 0.0),
                tracking_code=tracking_code,
                steps=validated_data.get('steps', 0),
                delivery_information=validated_data.get('deliveryInformation'),
                note=validated_data.get('note'),
                email=validated_data.get('email'),
                full_name=validated_data.get('fullName'),
                gender=validated_data.get('gender', 0),
                address=validated_data.get('address'),
                zip_code=validated_data.get('zipCode'),
                city=validated_data.get('city'),
                phone_number=validated_data.get('phoneNumber'),
                company_name=validated_data.get('companyName'),
                company_number=validated_data.get('companyNumber'),
                vat_number=validated_data.get('vatNumber'),
                user_type=validated_data.get('userType', 0),
                request_type=validated_data.get('requestType', 0),
                delivery_mode=validated_data.get('deliveryMode', 0),
                delivery_date=validated_data.get('deliveryDate'),
                status='pending'
            )
            
            # Create initial status
            RepairRequestStatus.objects.create(
                repair_request=repair_request,
                text='',
                status=0  # Pending
            )
            
            # Create repair request details from repairRequestDetails array
            if validated_data.get('repairRequestDetails'):
                for detail_data in validated_data['repairRequestDetails']:
                    problem = None
                    if detail_data.get('problemId'):
                        try:
                            problem = Problem.objects.get(id=detail_data['problemId'])
                        except Problem.DoesNotExist:
                            pass
                    
                    RepairRequestDetail.objects.create(
                        repair_request=repair_request,
                        problem=problem,
                        price=detail_data.get('price', 0.0),
                        start_repair_date=None,
                        end_repair_date=None,
                        is_canceled=False,
                        cancelation_description=None
                    )
            else:
                # Create default detail if none provided
                RepairRequestDetail.objects.create(
                    repair_request=repair_request,
                    problem=None,
                    price=0.0,
                    start_repair_date=None,
                    end_repair_date=None,
                    is_canceled=False,
                    cancelation_description=None
                )
            
            # Return tracking code as string (not ID)
            return create_success_response(data=tracking_code, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_followup',
        summary='Get repair request by tracking code and email',
        request=RepairRequestFollowupRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request details',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 1,
                                "duration": 0,
                                "totalPrice": 0,
                                "trackingCode": "86437489",
                                "steps": 1,
                                "deliveryInformation": "string",
                                "note": "string",
                                "createRequestDate": "2025-11-11T09:40:39.6189029",
                                "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                                "product": {
                                    "id": "94860000-b419-c60d-2b41-08dc425c06b1",
                                    "name": "شامپو کلیر",
                                    "masterImage": "/uploads/app/4012b8b383fc43bd808880d292d1deae.webp",
                                    "description": "شامپو کلیر"
                                },
                                "email": "string",
                                "fullName": "string",
                                "gender": 0,
                                "address": "string",
                                "zipCode": "string",
                                "city": "string",
                                "phoneNumber": "string",
                                "companyName": "string",
                                "companyNumber": "string",
                                "vatNumber": "string",
                                "userType": 0,
                                "requestType": 0,
                                "deliveryMode": 0,
                                "deliveryDate": "2025-11-11T06:09:49.156",
                                "repairRequestDetails": [],
                                "repairRequestStatuses": [],
                                "repairRequestDocuments": []
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='followup', permission_classes=[AllowAny])
    def followup(self, request):
        """Get repair request by tracking code and email matching old Swagger format."""
        try:
            serializer = RepairRequestFollowupRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            tracking_code = validated_data.get('trackingCode', '').strip()
            email = validated_data.get('email', '').strip()
            
            # Find repair request by tracking code and email
            try:
                repair_request = RepairRequest.objects.prefetch_related(
                    'repair_request_details__problem',
                    'repair_request_statuses',
                    'repair_request_documents'
                ).select_related('product', 'user').get(
                    tracking_code=tracking_code,
                    email=email
                )
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message='Repair request not found with the provided tracking code and email.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'trackingCode': ['Repair request not found with the provided tracking code and email.']}
                )
            
            response_data = serialize_repair_request_response(repair_request)
            return create_success_response(data=response_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_converttoappointment',
        summary='Convert repair request to appointment',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Repair request converted to appointment successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 1,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=True, methods=['get'], url_path='converttoappointment')
    def converttoappointment(self, request, pk=None):
        """Convert repair request to appointment matching old Swagger format."""
        try:
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=pk)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request with ID "{pk}" not found.']}
                )
            
            # Update status to indicate conversion (or create appointment record)
            # For now, we'll just update the status to 'completed' as conversion
            # In a full implementation, you might create an Appointment record
            repair_request.status = 'completed'
            repair_request.save()
            
            # Create status record for conversion
            RepairRequestStatus.objects.create(
                repair_request=repair_request,
                text='Converted to appointment',
                status=2  # Completed
            )
            
            # Return the ID
            return create_success_response(data=repair_request.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while converting repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RepairRequests'],
        operation_id='repairrequests_repairrequestmessage',
        summary='Add repair request message',
        request=RepairRequestMessageRequestSerializer,
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Message added successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 2,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['post'], url_path='repairrequestmessage', permission_classes=[AllowAny])
    def repairrequestmessage(self, request):
        """Add repair request message matching old Swagger format."""
        try:
            serializer = RepairRequestMessageRequestSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            repair_request_id = validated_data.get('repairRequestId')
            message_text = validated_data.get('message')
            message_type = validated_data.get('type', 0)
            
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=repair_request_id)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{repair_request_id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'repairRequestId': [f'Repair request with ID "{repair_request_id}" not found.']}
                )
            
            # Determine if message is from admin based on user permissions or type
            is_admin = False
            if request.user and request.user.is_authenticated:
                # Check if user is admin/manager
                if hasattr(request.user, 'is_staff') and request.user.is_staff:
                    is_admin = True
                elif message_type == 1:  # Admin message type
                    is_admin = True
            
            # Get user (if authenticated)
            user = request.user if request.user and request.user.is_authenticated else None
            
            # Create message
            repair_message = RepairRequestMessage.objects.create(
                repair_request=repair_request,
                user=user,
                message=message_text,
                type=message_type,
                is_admin=is_admin
            )
            
            # Return message ID
            return create_success_response(data=repair_message.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while adding message: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['RepairRequests'],
    operation_id='repairrequests_dapper',
    summary='Get repair requests in dapper context',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.QUERY, required=False, description='Repair Request ID (optional)')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Dapper response',
            examples=[
                OpenApiExample(
                    'Success Response (no id)',
                    value={
                        "data": None,
                        "messages": [],
                        "succeeded": True
                    }
                ),
                OpenApiExample(
                    'Success Response (with id)',
                    value={
                        "data": {
                            "id": 1,
                            "duration": 0,
                            "totalPrice": 0,
                            "trackingCode": "86437489",
                            "steps": 1,
                            "deliveryInformation": "string",
                            "note": "string",
                            "createRequestDate": "2025-11-11T09:40:39.6189029",
                            "userId": "5f4915ca-d4c1-4e5b-8a55-7ac7cd74d671",
                            "product": {
                                "id": "94860000-b419-c60d-2b41-08dc425c06b1",
                                "name": "شامپو کلیر",
                                "masterImage": "/uploads/app/4012b8b383fc43bd808880d292d1deae.webp",
                                "description": "شامپو کلیر"
                            },
                            "email": "string",
                            "fullName": "string",
                            "gender": 0,
                            "address": "string",
                            "zipCode": "string",
                            "city": "string",
                            "phoneNumber": "string",
                            "companyName": "string",
                            "companyNumber": "string",
                            "vatNumber": "string",
                            "userType": 0,
                            "requestType": 0,
                            "deliveryMode": 0,
                            "deliveryDate": "2025-11-11T06:09:49.156",
                            "repairRequestDetails": [],
                            "repairRequestStatuses": [],
                            "repairRequestDocuments": []
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RepairRequestsDapperView(APIView):
    """GET /api/v1/repairrequests/dapper"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get repair requests in dapper context. Accepts optional id parameter."""
        try:
            repair_request_id = request.query_params.get('id')
            
            if repair_request_id:
                # Return specific repair request
                try:
                    repair_request = RepairRequest.objects.prefetch_related(
                        'repair_request_details__problem',
                        'repair_request_statuses',
                        'repair_request_documents'
                    ).select_related('product', 'user').get(id=repair_request_id)
                    
                    response_data = serialize_repair_request_response(repair_request)
                    return create_success_response(data=response_data, messages=[])
                except RepairRequest.DoesNotExist:
                    return create_error_response(
                        error_message=f'Repair request with ID "{repair_request_id}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'id': [f'Repair request with ID "{repair_request_id}" not found.']}
                    )
            else:
                # Return null data as per old Swagger format
                return create_success_response(data=None, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['RepairRequests'],
    operation_id='repairrequests_repairrequestmessagesbyrepairid',
    summary='Get repair request messages by repair ID',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Repair Request ID')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Repair request messages',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": [],
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RepairRequestMessagesByRepairIdView(APIView):
    """GET /api/v1/repairrequests/repairrequestmessagesbyrepairid/{id}"""
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        """Get repair request messages by repair ID matching old Swagger format."""
        try:
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=id)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request with ID "{id}" not found.']}
                )
            
            # Get all messages for this repair request
            messages = RepairRequestMessage.objects.filter(repair_request=repair_request).order_by('-created_at')
            
            # Serialize messages
            messages_data = []
            for msg in messages:
                messages_data.append({
                    'id': msg.id,
                    'message': msg.message,
                    'type': msg.type,
                    'isAdmin': msg.is_admin,
                    'userId': str(msg.user.id) if msg.user else None,
                    'createdAt': msg.created_at.isoformat(),
                })
            
            return create_success_response(data=messages_data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while retrieving messages: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['RepairRequests'],
    operation_id='repairrequests_archiveasync',
    summary='Archive a repair request',
    parameters=[
        OpenApiParameter(name='id', type=int, location=OpenApiParameter.PATH, description='Repair Request ID')
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Repair request archived successfully',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": 1,
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RepairRequestArchiveAsyncView(APIView):
    """GET /api/v1/repairrequests/archiveasync/{id}"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, id):
        """Archive a repair request matching old Swagger format."""
        try:
            # Get repair request
            try:
                repair_request = RepairRequest.objects.get(id=id)
            except RepairRequest.DoesNotExist:
                return create_error_response(
                    error_message=f'Repair request with ID "{id}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Repair request with ID "{id}" not found.']}
                )
            
            # Archive the repair request
            repair_request.is_archived = True
            repair_request.save()
            
            # Return the ID
            return create_success_response(data=repair_request.id, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while archiving repair request: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

