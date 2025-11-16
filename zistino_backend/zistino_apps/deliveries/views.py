from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from zistino_apps.users.permissions import IsManager
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from zistino_apps.orders.models import Order

from .models import Delivery, Trip, LocationUpdate, DeliverySurvey, DeliveryItem, WeightShortfall, SurveyQuestion, SurveyAnswer
from .serializers import (
    DeliverySerializer, TripSerializer, LocationUpdateSerializer, 
    DeliveryFollowupRequestSerializer, DeliverySearchRequestSerializer,
    DeliveryTransferRequestSerializer, DeliveryDenyRequestSerializer,
    DeliverySurveySerializer, DeliverySurveyRequestSerializer,
    DeliveryLicensePlateRequestSerializer, DeliveryNonDeliveryRequestSerializer,
    DeliveryItemSerializer, DeliveryItemsBulkRequestSerializer,
    ManagerTelephoneRequestSerializer, WeightShortfallSerializer,
    WeightRangeMinimumConfigSerializer, SurveyQuestionSerializer,
    SurveyQuestionCreateSerializer, SurveyQuestionUpdateSerializer,
    ManagerDriverSatisfactionRequestSerializer
)
from .tasks import check_and_send_delivery_reminders


@extend_schema(tags=['Driver'], exclude=True)  # Excluded: using compatibility layer instead
class DeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for managing deliveries"""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Delivery.objects.filter(driver=self.request.user)

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_today_pending',
        summary="Get today's pending deliveries for driver",
        description='Returns all pending deliveries (assigned or in_progress) scheduled for today for the authenticated driver. '
                     'Includes address details, time slot formatting, and navigation URLs for each delivery.',
        responses={
            200: {
                'description': "Today's pending deliveries",
                'content': {
                    'application/json': {
                        'examples': {
                            'with_deliveries': {
                                'summary': 'Driver has pending deliveries today',
                                'value': {
                                    'count': 3,
                                    'deliveries': [
                                        {
                                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'driver': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'driver_name': 'John Doe',
                                            'order': 'order-uuid',
                                            'order_id': 'order-uuid',
                                            'status': 'assigned',
                                            'latitude': '35.6892',
                                            'longitude': '51.3890',
                                            'address': 'No. 10, Example Street, Tehran',
                                            'phone_number': '+989121234567',
                                            'delivery_date': '2024-01-15T10:30:00Z',
                                            'time_slot_formatted': '8 AM to 12 PM',
                                            'navigation_url': 'https://www.google.com/maps/dir/?api=1&destination=35.6892,51.3890',
                                            'delivered_weight': '0.00',
                                            'reminder_sms_sent': False,
                                            'description': '',
                                            'created_at': '2024-01-15T08:00:00Z',
                                            'updated_at': '2024-01-15T08:00:00Z'
                                        },
                                        {
                                            'id': '46e818ce-0518-4c64-8438-27bc7163a707',
                                            'driver': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'driver_name': 'John Doe',
                                            'order': 'order-uuid-2',
                                            'order_id': 'order-uuid-2',
                                            'status': 'in_progress',
                                            'latitude': '35.6893',
                                            'longitude': '51.3891',
                                            'address': 'No. 20, Another Street, Tehran',
                                            'phone_number': '+989121234568',
                                            'delivery_date': '2024-01-15T14:00:00Z',
                                            'time_slot_formatted': '12 PM to 4 PM',
                                            'navigation_url': 'https://www.google.com/maps/dir/?api=1&destination=35.6893,51.3891',
                                            'delivered_weight': '0.00',
                                            'reminder_sms_sent': True,
                                            'description': 'Customer requested morning delivery',
                                            'created_at': '2024-01-15T07:00:00Z',
                                            'updated_at': '2024-01-15T08:30:00Z'
                                        }
                                    ]
                                }
                            },
                            'no_deliveries': {
                                'summary': 'No pending deliveries today',
                                'value': {
                                    'count': 0,
                                    'deliveries': []
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='today-pending')
    def today_pending(self, request):
        """
        Get today's pending deliveries for the authenticated driver.
        Returns deliveries with status 'assigned' or 'in_progress' scheduled for today.
        """
        now = timezone.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Filter: driver's deliveries, today's date, pending status (assigned or in_progress)
        qs = Delivery.objects.filter(
            driver=request.user,
            delivery_date__gte=today_start,
            delivery_date__lt=today_end,
            status__in=['assigned', 'in_progress']
        ).select_related('driver', 'order').order_by('delivery_date')
        
        serializer = DeliverySerializer(qs, many=True)
        return Response({
            'count': qs.count(),
            'deliveries': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(tags=['Customer'], operation_id='delivery_myrequests')
    @action(detail=False, methods=['get'], url_path='myrequests', permission_classes=[IsAuthenticated])
    def my_requests(self, request):
        qs = Delivery.objects.filter(order__user=request.user).order_by('-created_at')[:100]
        return Response(DeliverySerializer(qs, many=True).data)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_followup',
        request=DeliveryFollowupRequestSerializer,
        examples=[
            OpenApiExample(
                'Followup delivery',
                value={
                    "id": 1,
                    "orderId": 123,
                    "deliveryDate": "2024-01-15T10:30:00Z",
                    "description": "Customer requested follow-up on delivery status",
                    "status": 1,
                    "latitude": 35.6892,
                    "longitude": 51.3890
                }
            )
        ]
    )
    @action(detail=False, methods=['post'], url_path='followup', permission_classes=[IsAuthenticated])
    def follow_up(self, request):
        """Update delivery followup status or information."""
        serializer = DeliveryFollowupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Find delivery by order if orderId provided
        if 'order_id' in data and data['order_id']:
            try:
                order = Order.objects.get(id=data['order_id'], user=request.user)
                delivery = Delivery.objects.filter(order=order).first()
                if delivery:
                    # Update delivery fields
                    if 'delivery_date' in data and data['delivery_date']:
                        delivery.delivery_date = data['delivery_date']
                    if 'description' in data:
                        delivery.description = data.get('description', '')
                    if 'latitude' in data and data['latitude']:
                        delivery.latitude = data['latitude']
                    if 'longitude' in data and data['longitude']:
                        delivery.longitude = data['longitude']
                    delivery.save()
                    return Response({
                        'message': 'Delivery follow-up updated successfully',
                        'delivery': DeliverySerializer(delivery).data
                    }, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                pass
        
        return Response({
            'message': 'Follow-up received',
            'status': 'processed'
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_pending_confirmation',
        summary='Get deliveries pending customer confirmation',
        description='Get list of deliveries that are waiting for customer confirmation. These are deliveries that have been marked as completed by the driver but not yet confirmed or denied by the customer. The delivered cargo amount will not be recorded until customer confirms.',
        responses={
            200: {
                'description': 'List of deliveries pending confirmation',
                'content': {
                    'application/json': {
                        'examples': {
                            'with_pending_deliveries': {
                                'summary': 'Customer has pending deliveries',
                                'value': {
                                    'count': 2,
                                    'deliveries': [
                                        {
                                            'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                            'order_id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'delivered_weight': '15.50',
                                            'delivery_date': '2024-01-15T14:30:00Z',
                                            'time_slot_formatted': '12 PM to 4 PM',
                                            'license_plate_number': '12ABC345',
                                            'customer_confirmation_status': 'pending',
                                            'address': 'No. 10, Example Street, Tehran',
                                            'driver_name': 'John Doe'
                                        },
                                        {
                                            'id': '46e818ce-0518-4c64-8438-27bc7163a707',
                                            'order_id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                            'delivered_weight': '8.25',
                                            'delivery_date': '2024-01-14T10:15:00Z',
                                            'time_slot_formatted': '8 AM to 12 PM',
                                            'license_plate_number': '98XYZ123',
                                            'customer_confirmation_status': 'pending',
                                            'address': 'No. 20, Another Street, Tehran',
                                            'driver_name': 'Jane Smith'
                                        }
                                    ]
                                }
                            },
                            'no_pending_deliveries': {
                                'summary': 'No pending deliveries',
                                'value': {
                                    'count': 0,
                                    'deliveries': []
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_survey_questions',
        summary='Get active survey questions',
        description='Get all active survey questions that customers should answer when submitting a survey.',
        responses={
            200: {
                'description': 'List of active survey questions',
                'content': {
                    'application/json': {
                        'examples': {
                            'questions': {
                                'summary': 'Active survey questions',
                                'value': {
                                    'items': [
                                        {
                                            'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                            'questionText': 'How was the driver\'s service?',
                                            'questionType': 'rating',
                                            'options': None,
                                            'isRequired': True,
                                            'order': 1
                                        },
                                        {
                                            'questionId': 'xyz98765-4321-0abc-defghijklmnop',
                                            'questionText': 'Was the driver on time?',
                                            'questionType': 'yes_no',
                                            'options': None,
                                            'isRequired': False,
                                            'order': 2
                                        }
                                    ],
                                    'total': 2
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=False, methods=['get'], url_path='survey-questions', permission_classes=[IsAuthenticated])
    def survey_questions(self, request):
        """Get active survey questions for customers."""
        questions = SurveyQuestion.objects.filter(is_active=True).order_by('order', 'created_at')
        serializer = SurveyQuestionSerializer(questions, many=True)
        return Response({
            'items': serializer.data,
            'total': questions.count()
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='pending-confirmation', permission_classes=[IsAuthenticated])
    def pending_confirmation(self, request):
        """Get deliveries waiting for customer confirmation."""
        qs = Delivery.objects.filter(
            order__user=request.user,
            status='completed',
            customer_confirmation_status='pending'
        ).select_related('order', 'driver').order_by('-delivery_date')
        
        serializer = DeliverySerializer(qs, many=True)
        return Response({
            'count': qs.count(),
            'deliveries': serializer.data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_confirm',
        summary='Confirm delivery',
        description='Customer confirms a delivery. After confirmation, the delivered cargo amount will be recorded in the customer\'s application. A survey menu will be displayed after confirmation. Only deliveries with status "completed" and confirmation_status "pending" can be confirmed.',
        request=None,
        responses={
            200: {
                'description': 'Delivery confirmed successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'confirmed': {
                                'summary': 'Delivery confirmed',
                                'value': {
                                    'message': 'Delivery confirmed successfully. Please complete the survey.',
                                    'delivery': {
                                        'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                        'customer_confirmation_status': 'confirmed',
                                        'confirmed_at': '2024-01-15T15:30:00Z',
                                        'delivered_weight': '15.50'
                                    },
                                    'showSurvey': True
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request - delivery cannot be confirmed',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery is not in a state that can be confirmed. Only deliveries with status "completed" and confirmation_status "pending" can be confirmed.'
                        }
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery not found or does not belong to you'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='confirm', permission_classes=[IsAuthenticated])
    def confirm(self, request, pk=None):
        """Customer confirms a delivery."""
        delivery = self.get_object()
        
        # Verify delivery belongs to customer
        if delivery.order.user != request.user:
            return Response(
                {'detail': 'Delivery not found or does not belong to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if delivery can be confirmed
        if delivery.status != 'completed' or delivery.customer_confirmation_status != 'pending':
            return Response(
                {'detail': 'Delivery is not in a state that can be confirmed. Only deliveries with status "completed" and confirmation_status "pending" can be confirmed.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update confirmation status
        delivery.customer_confirmation_status = 'confirmed'
        delivery.confirmed_at = timezone.now()
        delivery.save()
        
        return Response({
            'message': 'Delivery confirmed successfully. Please complete the survey.',
            'delivery': DeliverySerializer(delivery).data,
            'showSurvey': True
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_cancel',
        summary='Cancel a pending delivery',
        description='Customer cancels a delivery that is awaiting delivery (status assigned or in_progress). Only allowed when confirmation_status is pending. Cancellation sets status to "cancelled" and optionally saves a reason.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {
                        'type': 'string',
                        'description': 'Optional reason for cancellation'
                    }
                }
            }
        },
        examples=[
            OpenApiExample(
                'Cancel delivery with reason',
                value={
                    'reason': 'Plans changed, not available at the scheduled time'
                }
            ),
            OpenApiExample(
                'Cancel delivery without reason',
                value={}
            )
        ],
        responses={
            200: {
                'description': 'Delivery cancelled successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Delivery cancelled successfully.',
                            'delivery': {
                                'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                'status': 'cancelled',
                                'cancel_reason': 'Plans changed, not available at the scheduled time'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request - cannot cancel',
                'content': {
                    'application/json': {
                        'examples': {
                            'already_completed': {
                                'summary': 'Already completed',
                                'value': {
                                    'detail': 'Cannot cancel a delivery that is completed or cancelled.'
                                }
                            },
                            'not_pending': {
                                'summary': 'Confirmation not pending',
                                'value': {
                                    'detail': 'Cannot cancel when confirmation is not pending.'
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery not found or does not belong to you'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='cancel', permission_classes=[IsAuthenticated])
    def cancel(self, request, pk=None):
        """Customer cancels a delivery awaiting delivery."""
        delivery = self.get_object()
        
        # Verify delivery belongs to customer
        if delivery.order.user != request.user:
            return Response(
                {'detail': 'Delivery not found or does not belong to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Only allow cancel if assigned or in_progress, and confirmation is pending
        if delivery.status not in ['assigned', 'in_progress']:
            return Response(
                {'detail': 'Cannot cancel a delivery that is completed or cancelled.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if delivery.customer_confirmation_status != 'pending':
            return Response(
                {'detail': 'Cannot cancel when confirmation is not pending.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save optional reason
        reason = request.data.get('reason', '').strip() if isinstance(request.data, dict) else ''
        if reason:
            delivery.cancel_reason = reason
        
        delivery.status = 'cancelled'
        delivery.save()
        
        return Response({
            'message': 'Delivery cancelled successfully.',
            'delivery': DeliverySerializer(delivery).data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_deny',
        summary='Deny delivery',
        description='Customer denies a delivery with a reason. If delivery is denied, a menu will be displayed where customer can type the reason for disapproval. The delivered cargo amount will not be recorded. Only deliveries with status "completed" and confirmation_status "pending" can be denied.',
        request=DeliveryDenyRequestSerializer,
        examples=[
            OpenApiExample(
                'Deny delivery with reason',
                value={
                    'denial_reason': 'Delivered weight does not match expected amount'
                }
            ),
            OpenApiExample(
                'Deny delivery - wrong items',
                value={
                    'denial_reason': 'Wrong items were delivered. Expected plastic but received paper.'
                }
            ),
            OpenApiExample(
                'Deny delivery - damage',
                value={
                    'denial_reason': 'Items were damaged during delivery'
                }
            )
        ],
        responses={
            200: {
                'description': 'Delivery denied successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'denied': {
                                'summary': 'Delivery denied',
                                'value': {
                                    'message': 'Delivery denied successfully.',
                                    'delivery': {
                                        'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                        'customer_confirmation_status': 'denied',
                                        'denial_reason': 'Delivered weight does not match expected amount',
                                        'delivered_weight': '15.50'
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'cannot_deny': {
                                'summary': 'Delivery cannot be denied',
                                'value': {
                                    'detail': 'Delivery is not in a state that can be denied. Only deliveries with status "completed" and confirmation_status "pending" can be denied.'
                                }
                            },
                            'missing_reason': {
                                'summary': 'Denial reason required',
                                'value': {
                                    'denial_reason': ['This field is required.']
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery not found or does not belong to you'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='deny', permission_classes=[IsAuthenticated])
    def deny(self, request, pk=None):
        """Customer denies a delivery with reason."""
        delivery = self.get_object()
        
        # Verify delivery belongs to customer
        if delivery.order.user != request.user:
            return Response(
                {'detail': 'Delivery not found or does not belong to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if delivery can be denied
        if delivery.status != 'completed' or delivery.customer_confirmation_status != 'pending':
            return Response(
                {'detail': 'Delivery is not in a state that can be denied. Only deliveries with status "completed" and confirmation_status "pending" can be denied.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate denial reason
        serializer = DeliveryDenyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        denial_reason = serializer.validated_data['denial_reason']
        
        # Update confirmation status
        delivery.customer_confirmation_status = 'denied'
        delivery.denial_reason = denial_reason
        delivery.save()
        
        return Response({
            'message': 'Delivery denied successfully.',
            'delivery': DeliverySerializer(delivery).data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Customer'],
        operation_id='delivery_survey',
        summary='Submit delivery survey',
        description='Submit survey/feedback after confirming a delivery. Survey includes a rating (1-5), optional comment, and answers to survey questions. Survey can only be submitted for deliveries that have been confirmed by the customer.',
        request=DeliverySurveyRequestSerializer,
        examples=[
            OpenApiExample(
                'Submit survey with rating and comment',
                value={
                    'rating': 5,
                    'comment': 'Excellent service! Driver was on time and professional.'
                }
            ),
            OpenApiExample(
                'Submit survey with rating only',
                value={
                    'rating': 4
                }
            ),
            OpenApiExample(
                'Submit survey with question answers',
                value={
                    'rating': 5,
                    'comment': 'Great service!',
                    'answers': [
                        {
                            'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                            'answerValue': '5'
                        },
                        {
                            'questionId': 'xyz98765-4321-0abc-defghijklmnop',
                            'answerValue': 'Yes'
                        }
                    ]
                }
            )
        ],
        responses={
            201: {
                'description': 'Survey submitted successfully',
                'content': {
                    'application/json': {
                        'examples': {
                            'survey_created': {
                                'summary': 'Survey submitted',
                                'value': {
                                    'message': 'Survey submitted successfully.',
                                    'survey': {
                                        'id': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                        'delivery_id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                        'driver_id': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                        'driver_phone': '+989056761466',
                                        'rating': 5,
                                        'comment': 'Excellent service! Driver was on time and professional.',
                                        'answers': [
                                            {
                                                'id': 'answer123-4567-890a-bcde-fghijklmnop',
                                                'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                                'questionText': 'How was the driver\'s service?',
                                                'questionType': 'rating',
                                                'answerValue': '5',
                                                'createdAt': '2024-01-15T15:35:00Z'
                                            }
                                        ],
                                        'created_at': '2024-01-15T15:35:00Z',
                                        'updated_at': '2024-01-15T15:35:00Z'
                                    }
                                }
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'delivery_not_confirmed': {
                                'summary': 'Delivery not confirmed',
                                'value': {
                                    'detail': 'Survey can only be submitted for confirmed deliveries. Please confirm the delivery first.'
                                }
                            },
                            'survey_exists': {
                                'summary': 'Survey already exists',
                                'value': {
                                    'detail': 'Survey already exists for this delivery.'
                                }
                            },
                            'invalid_rating': {
                                'summary': 'Invalid rating',
                                'value': {
                                    'rating': ['Ensure this value is between 1 and 5.']
                                }
                            }
                        }
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery not found or does not belong to you'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='survey', permission_classes=[IsAuthenticated])
    def survey(self, request, pk=None):
        """Submit survey after confirming delivery."""
        delivery = self.get_object()
        
        # Verify delivery belongs to customer
        if delivery.order.user != request.user:
            return Response(
                {'detail': 'Delivery not found or does not belong to you'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if delivery is confirmed
        if delivery.customer_confirmation_status != 'confirmed':
            return Response(
                {'detail': 'Survey can only be submitted for confirmed deliveries. Please confirm the delivery first.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if survey already exists
        if hasattr(delivery, 'survey'):
            return Response(
                {'detail': 'Survey already exists for this delivery.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate survey data
        serializer = DeliverySurveyRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create survey
        survey = DeliverySurvey.objects.create(
            delivery=delivery,
            user=request.user,
            rating=serializer.validated_data['rating'],
            comment=serializer.validated_data.get('comment', '')
        )
        
        # Save question answers if provided
        answers_data = serializer.validated_data.get('answers', [])
        if answers_data:
            for answer_data in answers_data:
                try:
                    question = SurveyQuestion.objects.get(id=answer_data['questionId'])
                    # Only save answers for active questions
                    if question.is_active:
                        SurveyAnswer.objects.create(
                            survey=survey,
                            question=question,
                            answer_value=str(answer_data['answerValue'])
                        )
                except SurveyQuestion.DoesNotExist:
                    # Skip invalid question IDs
                    continue
        
        return Response({
            'message': 'Survey submitted successfully.',
            'survey': DeliverySurveySerializer(survey).data
        }, status=status.HTTP_201_CREATED)

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_set_license_plate',
        summary='Set license plate number',
        description='Driver sets license plate number when completing/registering a delivery. This license plate number will be displayed to the customer for confirmation.',
        request=DeliveryLicensePlateRequestSerializer,
        examples=[
            OpenApiExample(
                'Set license plate',
                value={
                    'license_plate_number': '12ABC345'
                }
            )
        ],
        responses={
            200: {
                'description': 'License plate number set successfully',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'License plate number set successfully.',
                            'delivery': {
                                'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                'license_plate_number': '12ABC345'
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Forbidden - not the assigned driver',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'You are not the assigned driver for this delivery'
                        }
                    }
                }
            },
            404: {
                'description': 'Delivery not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery not found'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='set-license-plate', permission_classes=[IsAuthenticated])
    def set_license_plate(self, request, pk=None):
        """Driver sets license plate number for delivery."""
        delivery = self.get_object()
        
        # Verify driver is assigned to this delivery
        if delivery.driver != request.user:
            return Response(
                {'detail': 'You are not the assigned driver for this delivery'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validate license plate
        serializer = DeliveryLicensePlateRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update license plate
        delivery.license_plate_number = serializer.validated_data['license_plate_number']
        delivery.save()
        
        return Response({
            'message': 'License plate number set successfully.',
            'delivery': DeliverySerializer(delivery).data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_items_list',
        summary='List per-group weights for a delivery',
        description='Driver lists recorded weights by waste group/category for this delivery.',
        responses={
            200: {
                'description': 'Items list',
                'content': {
                    'application/json': {
                        'example': {
                            'items': [
                                {'id': 'item-uuid', 'category_id': 'cat-uuid', 'category_name': 'Plastic', 'weight': '12.50'},
                                {'id': 'item-uuid-2', 'category_id': 'cat-uuid-2', 'category_name': 'Paper', 'weight': '8.00'}
                            ],
                            'totalWeight': '20.50'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['get'], url_path='items', permission_classes=[IsAuthenticated])
    def list_items(self, request, pk=None):
        delivery = self.get_object()
        if delivery.driver != request.user:
            return Response({'detail': 'You are not the assigned driver for this delivery'}, status=status.HTTP_403_FORBIDDEN)
        items = DeliveryItem.objects.filter(delivery=delivery).select_related('category')
        data = DeliveryItemSerializer(items, many=True).data
        # compute total
        total = sum([float(i['weight']) for i in data]) if data else 0.0
        return Response({'items': data, 'totalWeight': f"{total:.2f}"})

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_items_bulk_set',
        summary='Bulk set per-group weights for a delivery',
        description='Replace all existing items with provided list. Recalculates delivery.delivered_weight as the sum.',
        request=DeliveryItemsBulkRequestSerializer,
        examples=[
            OpenApiExample(
                'Set items by category',
                value={
                    'items': [
                        { 'categoryId': '46e818ce-0518-4c64-8438-27bc7163a706', 'weight': '12.50' },
                        { 'categoryId': '0641067f-df76-416c-98cd-6f89e43d3b3f', 'weight': '8.00' }
                    ]
                }
            )
        ],
        responses={
            200: {
                'description': 'Items updated',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Delivery items updated',
                            'delivery': {
                                'id': 'delivery-uuid',
                                'delivered_weight': '20.50'
                            },
                            'items': [
                                {'category_id': 'cat-uuid', 'category_name': 'Plastic', 'weight': '12.50'},
                                {'category_id': 'cat-uuid-2', 'category_name': 'Paper', 'weight': '8.00'}
                            ]
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='items/bulk-set', permission_classes=[IsAuthenticated])
    def bulk_set_items(self, request, pk=None):
        delivery = self.get_object()
        if delivery.driver != request.user:
            return Response({'detail': 'You are not the assigned driver for this delivery'}, status=status.HTTP_403_FORBIDDEN)
        # Validate payload
        serializer = DeliveryItemsBulkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_payload = serializer.validated_data['items']

        # Load categories and validate
        from zistino_apps.products.models import Category
        cat_ids = [str(i['categoryId']) for i in items_payload]
        categories = {str(c.id): c for c in Category.objects.filter(id__in=cat_ids)}
        for i in items_payload:
            if str(i['categoryId']) not in categories:
                return Response({'detail': f"Category not found: {i['categoryId']}"}, status=status.HTTP_400_BAD_REQUEST)

        # Replace existing items
        DeliveryItem.objects.filter(delivery=delivery).delete()
        new_items = []
        for i in items_payload:
            new_items.append(DeliveryItem(
                delivery=delivery,
                category=categories[str(i['categoryId'])],
                weight=i['weight']
            ))
        DeliveryItem.objects.bulk_create(new_items)

        # Recalculate total and update delivery.delivered_weight
        total_weight = sum([float(i.weight) for i in new_items])
        delivery.delivered_weight = total_weight
        delivery.save(update_fields=['delivered_weight'])

        # Response
        response_items = DeliveryItemSerializer(DeliveryItem.objects.filter(delivery=delivery).select_related('category'), many=True).data
        return Response({
            'message': 'Delivery items updated',
            'delivery': {'id': str(delivery.id), 'delivered_weight': f"{total_weight:.2f}"},
            'items': response_items
        })

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_center_confirm',
        summary='Driver confirms cargo received at center',
        description='After center registers cargo, driver confirms the received amount. This will credit the customer wallet based on total cargo weight and configured rate.\n\nNo request body is required — send an empty JSON object {}.',
        request=None,
        examples=[
            OpenApiExample(
                'Empty request body',
                summary='No body required',
                description='Send an empty JSON body. Authorization header required.',
                value={},
                request_only=True,
            ),
        ],
        responses={
            200: {
                'description': 'Center confirmation successful and wallet credited',
                'content': {
                    'application/json': {
                        'examples': {
                            'with_credit': {
                                'summary': 'Rate configured, wallet credited',
                                'value': {
                                    'message': 'Center confirmation recorded. Wallet credited.',
                                    'creditedAmount': '205000.00',
                                    'driverPayout': '2050.00',
                                    'visitCount': 5,
                                    'currency': 'Rials',
                                    'delivery': {
                                        'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                        'delivered_weight': '20.50'
                                    }
                                }
                            },
                            'no_rate_configured': {
                                'summary': 'No rate configured, no credit applied',
                                'value': {
                                    'message': 'Center confirmation recorded. No rate configured, wallet not credited.',
                                    'creditedAmount': '0.00',
                                    'currency': 'Rials',
                                    'delivery': {
                                        'id': '46e818ce-0518-4c64-8438-27bc7163a706',
                                        'delivered_weight': '20.50'
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='center-confirm', permission_classes=[IsAuthenticated])
    def center_confirm(self, request, pk=None):
        """Driver confirms cargo at center; credit customer's wallet."""
        from django.db import transaction as db_transaction
        from decimal import Decimal
        from zistino_apps.payments.models import Wallet, Transaction
        # Optional rate from configuration
        try:
            from zistino_apps.configurations.models import Configuration
            cfg = Configuration.objects.filter(name__icontains='waste_price_per_kg', is_active=True).first()
            rate = Decimal('0')
            currency = 'Rials'
            if cfg and cfg.value is not None:
                val = cfg.value
                # Handle dict, stringified JSON, or plain number
                if isinstance(val, dict):
                    r = val.get('rate', None)
                    c = val.get('currency', None)
                elif isinstance(val, str):
                    import json
                    try:
                        parsed = json.loads(val)
                        r = parsed.get('rate', None) if isinstance(parsed, dict) else parsed
                        c = parsed.get('currency', None) if isinstance(parsed, dict) else None
                    except Exception:
                        # If it's a plain numeric string
                        r = val
                        c = None
                else:
                    # Numeric or other type
                    r = val
                    c = None

                if r is not None and str(r) != '':
                    rate = Decimal(str(r))
                if c:
                    currency = str(c)
        except Exception:
            rate = Decimal('0')
            currency = 'Rials'

        delivery = self.get_object()
        # Only assigned driver can confirm
        if delivery.driver != request.user:
            return Response({'detail': 'You are not the assigned driver for this delivery'}, status=status.HTTP_403_FORBIDDEN)

        # Determine total weight: prefer per-group items sum, fallback to delivered_weight
        items_qs = DeliveryItem.objects.filter(delivery=delivery)
        if items_qs.exists():
            total_weight = sum([Decimal(i.weight) for i in items_qs])
        else:
            total_weight = Decimal(str(delivery.delivered_weight or 0))

        # Check for weight shortfall (if order has estimated_weight_range)
        shortfall_amount = Decimal('0.00')
        shortfall_created = None
        minimum_weight = None
        order = delivery.order
        if order.estimated_weight_range:
            # Get minimum weight for this range from configuration
            try:
                min_cfg = Configuration.objects.filter(name__icontains='weight_range_minimum', is_active=True).first()
                if min_cfg and min_cfg.value and isinstance(min_cfg.value, list):
                    # Find matching range: [{"value": "5-10", "min": 5}, ...]
                    for range_item in min_cfg.value:
                        if isinstance(range_item, dict) and range_item.get('value') == order.estimated_weight_range:
                            minimum_weight = Decimal(str(range_item.get('min', 0)))
                            if total_weight < minimum_weight:
                                shortfall_amount = total_weight - minimum_weight  # Negative value
                                break
            except Exception as e:
                # Log error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error calculating shortfall: {e}")
                pass

        # Get existing undeducted shortfalls for this customer
        existing_shortfalls = WeightShortfall.objects.filter(
            user=delivery.order.user,
            is_deducted=False
        ).order_by('created_at')

        # Calculate total shortfall to deduct
        total_shortfall_to_deduct = sum([abs(s.shortfall_amount) for s in existing_shortfalls])
        
        # Calculate amount with shortfall deduction
        base_amount = (total_weight * rate).quantize(Decimal('0.01')) if rate else Decimal('0.00')
        shortfall_deduction = (total_shortfall_to_deduct * rate).quantize(Decimal('0.01')) if rate else Decimal('0.00')
        amount = base_amount - shortfall_deduction
        if amount < 0:
            amount = Decimal('0.00')  # Don't go negative

        # Calculate driver payout based on visit count tier
        customer = delivery.order.user
        # Count confirmed deliveries for this customer (visit count)
        visit_count = Delivery.objects.filter(
            order__user=customer,
            customer_confirmation_status='confirmed',
            status='completed'
        ).exclude(id=delivery.id).count() + 1  # +1 includes current delivery

        # Get driver payout tiers from configuration
        driver_payout_rate = Decimal('0')
        try:
            payout_cfg = Configuration.objects.filter(name__icontains='driver_payout_tiers', is_active=True).first()
            if payout_cfg and payout_cfg.value:
                tiers = payout_cfg.value if isinstance(payout_cfg.value, list) else []
                # Find matching tier: [{"min":1,"max":10,"rate":100},{"min":11,"max":20,"rate":200},...]
                for tier in tiers:
                    if isinstance(tier, dict):
                        min_visits = int(tier.get('min', 0))
                        max_visits = tier.get('max')
                        tier_rate = Decimal(str(tier.get('rate', 0)))
                        if max_visits is None:
                            # Open-ended tier (e.g., 21+)
                            if visit_count >= min_visits:
                                driver_payout_rate = tier_rate
                                break
                        else:
                            if min_visits <= visit_count <= int(max_visits):
                                driver_payout_rate = tier_rate
                                break
        except Exception:
            driver_payout_rate = Decimal('0')

        driver_payout_amount = (total_weight * driver_payout_rate).quantize(Decimal('0.01')) if driver_payout_rate else Decimal('0.00')

        # Credit customer's wallet and driver's wallet atomically
        with db_transaction.atomic():
            # Create shortfall record if delivered weight < minimum
            if shortfall_amount < 0 and minimum_weight is not None:
                shortfall_created = WeightShortfall.objects.create(
                    user=delivery.order.user,
                    delivery=delivery,
                    estimated_range=order.estimated_weight_range,
                    minimum_weight=minimum_weight,
                    delivered_weight=total_weight,
                    shortfall_amount=shortfall_amount
                )
            
            # Mark existing shortfalls as deducted
            if existing_shortfalls.exists():
                from django.utils import timezone as tz
                now = tz.now()
                existing_shortfalls.update(
                    is_deducted=True,
                    deducted_from_delivery=delivery,
                    deducted_at=now
                )
            
            # Credit customer
            wallet, _ = Wallet.objects.get_or_create(user=delivery.order.user, defaults={'balance': Decimal('0.00')})
            if amount > 0:
                wallet.balance = (wallet.balance or Decimal('0.00')) + amount
                wallet.save(update_fields=['balance'])
                desc = f'Cargo credit for delivery {delivery.id}'
                if shortfall_deduction > 0:
                    desc += f' (deducted {shortfall_deduction:.2f} for previous shortfall)'
                Transaction.objects.create(
                    wallet=wallet,
                    amount=amount,
                    transaction_type='credit',
                    status='completed',
                    description=desc,
                    reference_id=str(delivery.id)
                )

            # Credit driver
            driver_wallet, _ = Wallet.objects.get_or_create(user=delivery.driver, defaults={'balance': Decimal('0.00')})
            if driver_payout_amount > 0:
                driver_wallet.balance = (driver_wallet.balance or Decimal('0.00')) + driver_payout_amount
                driver_wallet.save(update_fields=['balance'])
                Transaction.objects.create(
                    wallet=driver_wallet,
                    amount=driver_payout_amount,
                    transaction_type='credit',
                    status='completed',
                    description=f'Driver payout for delivery {delivery.id} (visit #{visit_count}, {total_weight}kg @ {driver_payout_rate}/kg)',
                    reference_id=str(delivery.id)
                )

        response_data = {
            'message': 'Center confirmation recorded. Wallet credited.' if amount > 0 else 'Center confirmation recorded. No rate configured, wallet not credited.',
            'creditedAmount': f"{amount:.2f}",
            'driverPayout': f"{driver_payout_amount:.2f}",
            'visitCount': visit_count,
            'currency': currency,
            'delivery': {
                'id': str(delivery.id),
                'delivered_weight': f"{total_weight:.2f}"
            }
        }
        
        # Add shortfall information if applicable
        if shortfall_amount < 0 and minimum_weight is not None:
            response_data['shortfall'] = {
                'amount': f"{abs(shortfall_amount):.2f}",
                'minimumWeight': f"{minimum_weight:.2f}",
                'estimatedRange': order.estimated_weight_range
            }
        
        if shortfall_deduction > 0:
            response_data['shortfallDeduction'] = f"{shortfall_deduction:.2f}"
            response_data['baseAmount'] = f"{base_amount:.2f}"
        
        return Response(response_data, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_center_deny',
        summary='Driver denies cargo at center',
        description='Driver denies the cargo amount registered at center and provides a reason.',
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'reason': {'type': 'string', 'description': 'Reason for denying the center-registered cargo'}
                }
            }
        },
        examples=[
            OpenApiExample('Deny example', value={'reason': 'Mismatch with measured weights'})
        ],
        responses={
            200: {
                'description': 'Denial recorded',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Center denial recorded.',
                            'reason': 'Mismatch with measured weights'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='center-deny', permission_classes=[IsAuthenticated])
    def center_deny(self, request, pk=None):
        """Driver denies the center-registered cargo amount with a reason."""
        delivery = self.get_object()
        if delivery.driver != request.user:
            return Response({'detail': 'You are not the assigned driver for this delivery'}, status=status.HTTP_403_FORBIDDEN)
        reason = (request.data or {}).get('reason', '').strip()
        if reason:
            # reuse cancel_reason field to persist driver-center denial rationale without schema change
            delivery.cancel_reason = reason
            delivery.save(update_fields=['cancel_reason'])
        return Response({'message': 'Center denial recorded.', 'reason': reason}, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Driver'],
        operation_id='delivery_non_delivery',
        summary='Record non-delivery with reason',
        description='Driver marks a delivery as not delivered and records the reason. Allowed only when delivery status is assigned or in_progress.',
        request=DeliveryNonDeliveryRequestSerializer,
        examples=[
            OpenApiExample('Customer unavailable', value={'reason': 'Customer unavailable at the address'}),
            OpenApiExample('Wrong address', value={'reason': 'Address not found / wrong address provided'})
        ],
        responses={
            200: {
                'description': 'Non-delivery recorded',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Non-delivery recorded.',
                            'delivery': {
                                'id': 'delivery-uuid',
                                'status': 'cancelled',
                                'cancel_reason': 'Customer unavailable at the address'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request',
                'content': {
                    'application/json': {
                        'examples': {
                            'invalid_status': {
                                'summary': 'Delivery already completed or cancelled',
                                'value': {'detail': 'Cannot mark non-delivery when status is completed or cancelled.'}
                            }
                        }
                    }
                }
            },
            403: {
                'description': 'Forbidden - not the assigned driver'
            },
            404: {
                'description': 'Delivery not found'
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='non-delivery', permission_classes=[IsAuthenticated])
    def non_delivery(self, request, pk=None):
        """Driver records non-delivery with a reason and cancels the delivery."""
        delivery = self.get_object()
        if delivery.driver != request.user:
            return Response({'detail': 'You are not the assigned driver for this delivery'}, status=status.HTTP_403_FORBIDDEN)

        # Only allow if still pending execution
        if delivery.status not in ['assigned', 'in_progress']:
            return Response({'detail': 'Cannot mark non-delivery when status is completed or cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        # Validate reason
        serializer = DeliveryNonDeliveryRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reason = serializer.validated_data['reason']

        delivery.status = 'cancelled'
        delivery.cancel_reason = reason
        delivery.save(update_fields=['status', 'cancel_reason'])

        return Response({
            'message': 'Non-delivery recorded.',
            'delivery': {
                'id': str(delivery.id),
                'status': delivery.status,
                'cancel_reason': delivery.cancel_reason
            }
        }, status=status.HTTP_200_OK)


@extend_schema(tags=['Deliveries'])
class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Trip.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(tags=['Deliveries'])
class LocationUpdateViewSet(viewsets.ModelViewSet):
    queryset = LocationUpdate.objects.all()
    serializer_class = LocationUpdateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return LocationUpdate.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@extend_schema(
    tags=['Customer'],
    operation_id='driverdelivery_followup',
    request=DeliveryFollowupRequestSerializer,
    examples=[
        OpenApiExample(
            'Followup delivery',
            description='Request follow-up for a delivery. All fields are optional. orderId must be a UUID string.',
            value={
                "id": 1,
                "orderId": "46e818ce-0518-4c64-8438-27bc7163a706",
                "deliveryDate": "2024-01-15T10:30:00Z",
                "description": "Customer requested follow-up on delivery status",
                "status": 1,
                "latitude": 35.6892,
                "longitude": 51.3890
            }
        ),
        OpenApiExample(
            'Simple followup',
            description='Minimal follow-up request with UUID order ID',
            value={
                "orderId": "46e818ce-0518-4c64-8438-27bc7163a706"
            }
        )
    ]
)
class DriverDeliveryFollowupView(APIView):
    """Follow-up endpoint for driver deliveries - matches driverdelivery/followup path."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Handle delivery follow-up request."""
        serializer = DeliveryFollowupRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        
        # Find delivery by order if orderId provided
        if 'order_id' in data and data['order_id']:
            order_id_str = str(data['order_id']).strip()
            if not order_id_str:
                return Response({
                    'detail': 'orderId cannot be empty',
                    'hint': 'Please provide a valid order ID (UUID format)'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Try to get order by UUID (Order.id is UUIDField)
                order = Order.objects.get(id=order_id_str, user=request.user)
                delivery = Delivery.objects.filter(order=order).first()
                
                if delivery:
                    # Update delivery fields
                    if 'delivery_date' in data and data['delivery_date']:
                        delivery.delivery_date = data['delivery_date']
                    if 'description' in data:
                        delivery.description = data.get('description', '')
                    if 'latitude' in data and data['latitude']:
                        delivery.latitude = data['latitude']
                    if 'longitude' in data and data['longitude']:
                        delivery.longitude = data['longitude']
                    delivery.save()
                    return Response({
                        'message': 'Delivery follow-up updated successfully',
                        'delivery': DeliverySerializer(delivery).data
                    }, status=status.HTTP_200_OK)
                else:
                    # Order exists but no delivery created yet
                    return Response({
                        'detail': f'Order {order_id_str} found but no delivery exists yet',
                        'hint': 'Delivery will be created when a driver is assigned',
                        'order_id': str(order.id),
                        'order_status': order.status
                    }, status=status.HTTP_404_NOT_FOUND)
                    
            except Order.DoesNotExist:
                # Check if order exists but belongs to different user
                order_exists = Order.objects.filter(id=order_id_str).exists()
                if order_exists:
                    return Response({
                        'detail': f'Order {order_id_str} exists but does not belong to you',
                        'hint': 'You can only follow up on your own orders'
                    }, status=status.HTTP_403_FORBIDDEN)
                else:
                    # Get user's orders to help them find the correct ID
                    user_orders = Order.objects.filter(user=request.user).values_list('id', flat=True)[:5]
                    return Response({
                        'detail': f'Order {order_id_str} not found',
                        'hint': 'Make sure you are using the correct order ID (UUID format)',
                        'your_recent_orders': [str(oid) for oid in user_orders] if user_orders else [],
                        'tip': 'Use GET /api/v1/orders/client/search to see your orders'
                    }, status=status.HTTP_404_NOT_FOUND)
            except ValueError as e:
                return Response({
                    'detail': f'Invalid order ID format: {order_id_str}',
                    'hint': 'Order ID must be a valid UUID format (e.g., "46e818ce-0518-4c64-8438-27bc7163a706")',
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({
            'message': 'Follow-up received',
            'status': 'processed',
            'note': 'No orderId provided, so no delivery was updated'
        }, status=status.HTTP_200_OK)


# ============================================
# MANAGER ENDPOINTS - Separated for clarity
# ============================================
# These endpoints are for managers only (is_staff=True)
# They provide admin-level access to all resources
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='manager_telephone_requests_create',
    summary='Create telephone request (order + optional delivery)',
    description='Manager records a telephone request by customer phone. Finds or creates the customer, creates an order with optional items and location, and optionally creates a delivery record.',
    request=ManagerTelephoneRequestSerializer,
    examples=[
        OpenApiExample(
            'Minimal telephone request',
            value={
                'phoneNumber': '+989121234567',
                'fullName': 'John Doe',
                'address': 'No. 10, Example Street, Tehran'
            }
        ),
        OpenApiExample(
            'With items and preferred delivery',
            value={
                'phoneNumber': '+989121234567',
                'fullName': 'John Doe',
                'address': 'No. 10, Example Street, Tehran',
                'latitude': 35.6892,
                'longitude': 51.3890,
                'preferredDeliveryDate': '2025-11-03T14:00:00Z',
                'createDelivery': True,
                'items': [
                    { 'productName': 'Plastic', 'weight': '8.50', 'quantity': 1 },
                    { 'productName': 'Paper', 'weight': '4.00', 'quantity': 1 }
                ]
            }
        )
    ],
    responses={
        201: {
            'description': 'Telephone request created',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Telephone request created',
                        'userId': 'user-uuid',
                        'orderId': 'order-uuid',
                        'deliveryId': 'delivery-uuid'
                    }
                }
            }
        }
    }
)
class ManagerTelephoneRequestView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        from django.contrib.auth import get_user_model
        from zistino_apps.orders.models import Order, OrderItem
        from zistino_apps.deliveries.models import Delivery

        serializer = ManagerTelephoneRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        phone = data['phoneNumber']
        full_name = data.get('fullName', '').strip()
        address = data.get('address', '')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        preferred_date = data.get('preferredDeliveryDate')
        create_delivery = data.get('createDelivery', True)
        items = data.get('items') or []

        # Find-or-create user by phone
        User = get_user_model()
        user, created = User.objects.get_or_create(phone_number=phone, defaults={
            'username': phone,
            'is_active': True
        })
        # Update names if provided
        if full_name and (not user.first_name and not user.last_name):
            parts = full_name.split(' ', 1)
            user.first_name = parts[0]
            if len(parts) > 1:
                user.last_name = parts[1]
            user.save(update_fields=['first_name', 'last_name'])

        # Create order
        order = Order.objects.create(
            user=user,
            status=0,
            total_price=0,
            address1=address or '',
            latitude=latitude,
            longitude=longitude,
            user_full_name=full_name or user.get_full_name() or '',
            user_phone_number=phone
        )

        # Create order items
        bulk_items = []
        for it in items:
            bulk_items.append(OrderItem(
                order=order,
                product_name=it['productName'],
                quantity=it.get('quantity') or 1,
                unit_price=0,
                total_price=0,
                weight=it.get('weight')
            ))
        if bulk_items:
            OrderItem.objects.bulk_create(bulk_items)

        # Optionally create delivery
        delivery_id = None
        if create_delivery:
            # Note: manager may not be a driver; this assigns manager as driver only if appropriate
            delivery = Delivery.objects.create(
                driver=request.user,
                order=order,
                status='assigned',
                address=address or '',
                phone_number=phone,
                delivery_date=preferred_date
            )
            delivery_id = str(delivery.id)

        return Response({
            'message': 'Telephone request created',
            'userId': str(user.id),
            'orderId': str(order.id),
            'deliveryId': delivery_id
        }, status=status.HTTP_201_CREATED)

@extend_schema(tags=['Admin'])
class ManagerDeliveryViewSet(viewsets.ModelViewSet):
    """ViewSet for managers to manage all deliveries - Manager-only."""
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all deliveries (no filtering by driver)."""
        return Delivery.objects.all().select_related('driver', 'order').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create delivery - manager can assign to any driver."""
        serializer.save()  # Driver is set in request data
    
    @extend_schema(
        tags=['Admin'],
        operation_id='delivery_transfer',
        summary='Transfer delivery to another driver',
        description='Manually transfer a delivery from current driver to another driver. Only works for deliveries with status "assigned" or "in_progress".',
        request=DeliveryTransferRequestSerializer,
        examples=[
            OpenApiExample(
                'Transfer delivery to another driver',
                description='Transfer a delivery to a different driver. Get driver IDs from /api/v1/drivers/byzone endpoint.',
                value={
                    'driverId': '0641067f-df76-416c-98cd-6f89e43d3b3f'
                }
            ),
            OpenApiExample(
                'Transfer delivery example 2',
                value={
                    'driverId': '46e818ce-0518-4c64-8438-27bc7163a706'
                }
            )
        ],
        responses={
            200: {
                'description': 'Delivery successfully transferred',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Delivery successfully transferred from +989121234567 to +989121234568',
                            'delivery': {
                                'id': 'delivery-uuid',
                                'driver': 'new-driver-uuid',
                                'order': 'order-uuid',
                                'status': 'assigned',
                                'address': 'Test Address',
                                'phone_number': '+989121234567'
                            }
                        }
                    }
                }
            },
            400: {
                'description': 'Bad request - delivery cannot be transferred',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Cannot transfer delivery with status: completed. Only "assigned" or "in_progress" deliveries can be transferred.'
                        }
                    }
                }
            },
            404: {
                'description': 'Driver not found',
                'content': {
                    'application/json': {
                        'example': {
                            'detail': 'Driver not found or not active'
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='transfer')
    def transfer(self, request, pk=None):
        """
        Manually transfer a delivery from current driver to another driver.
        Only allowed if delivery status is 'assigned' or 'in_progress'.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        delivery = self.get_object()
        new_driver_id = request.data.get('driverId')
        
        if not new_driver_id:
            return Response(
                {'detail': 'driverId is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if delivery can be transferred (only assigned or in_progress)
        if delivery.status not in ['assigned', 'in_progress']:
            return Response(
                {'detail': f'Cannot transfer delivery with status: {delivery.status}. Only "assigned" or "in_progress" deliveries can be transferred.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get new driver
        try:
            new_driver = User.objects.get(id=new_driver_id, is_driver=True, is_active=True)
        except User.DoesNotExist:
            return Response(
                {'detail': 'Driver not found or not active'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update delivery driver
        old_driver = delivery.driver
        delivery.driver = new_driver
        delivery.save()
        
        return Response({
            'detail': f'Delivery successfully transferred from {old_driver.phone_number} to {new_driver.phone_number}',
            'delivery': DeliverySerializer(delivery).data
        }, status=status.HTTP_200_OK)

    @extend_schema(
        tags=['Admin'],
        operation_id='manager_delivery_items_bulk_set',
        summary='Set per-group weights for a delivery (manager)',
        description='Manager records/overrides weights by category for a delivery. Replaces existing items and recalculates delivered_weight.',
        request=DeliveryItemsBulkRequestSerializer,
        examples=[
            OpenApiExample(
                'Set items by category (manager)',
                value={
                    'items': [
                        { 'categoryId': '46e818ce-0518-4c64-8438-27bc7163a706', 'weight': '12.50' },
                        { 'categoryId': '0641067f-df76-416c-98cd-6f89e43d3b3f', 'weight': '8.00' }
                    ]
                }
            )
        ],
        responses={
            200: {
                'description': 'Items updated',
                'content': {
                    'application/json': {
                        'example': {
                            'message': 'Delivery items updated (manager)',
                            'delivery': {
                                'id': 'delivery-uuid',
                                'delivered_weight': '20.50'
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['post'], url_path='items/bulk-set')
    def items_bulk_set(self, request, pk=None):
        """Manager sets per-category weights for a delivery (authoritative)."""
        delivery = self.get_object()
        # Validate payload
        serializer = DeliveryItemsBulkRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        items_payload = serializer.validated_data['items']

        # Load categories and validate
        from zistino_apps.products.models import Category
        from zistino_apps.deliveries.models import DeliveryItem
        cat_ids = [str(i['categoryId']) for i in items_payload]
        categories = {str(c.id): c for c in Category.objects.filter(id__in=cat_ids)}
        for i in items_payload:
            if str(i['categoryId']) not in categories:
                return Response({'detail': f"Category not found: {i['categoryId']}"}, status=status.HTTP_400_BAD_REQUEST)

        # Replace existing items
        DeliveryItem.objects.filter(delivery=delivery).delete()
        new_items = []
        for i in items_payload:
            new_items.append(DeliveryItem(
                delivery=delivery,
                category=categories[str(i['categoryId'])],
                weight=i['weight']
            ))
        DeliveryItem.objects.bulk_create(new_items)

        # Recalculate total and update delivery.delivered_weight
        total_weight = sum([float(i.weight) for i in new_items])
        delivery.delivered_weight = total_weight
        delivery.save(update_fields=['delivered_weight'])

        return Response({
            'message': 'Delivery items updated (manager)',
            'delivery': {'id': str(delivery.id), 'delivered_weight': f"{total_weight:.2f}"}
        })

    @extend_schema(
        tags=['Admin'],
        operation_id='delivery_price_by_category',
        summary='Calculate delivery price by category rates',
        description='Calculates total price for a delivery as the sum of (weight per category × rate per kg), using Configuration name contains "category_rates_per_kg". If no items or category rate missing, falls back to global rate (waste_price_per_kg).',
        responses={
            200: {
                'description': 'Calculated price',
                'content': {
                    'application/json': {
                        'examples': {
                            'with_category_rates': {
                                'summary': 'Category rates applied',
                                'value': {
                                    'deliveryId': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'currency': 'Rials',
                                    'breakdown': [
                                        {'categoryId': 'cat-plastic', 'categoryName': 'Plastic', 'weight': '12.50', 'rate': '10000.00', 'amount': '125000.00'},
                                        {'categoryId': 'cat-paper', 'categoryName': 'Paper', 'weight': '8.00', 'rate': '15000.00', 'amount': '120000.00'}
                                    ],
                                    'totalWeight': '20.50',
                                    'totalAmount': '245000.00',
                                    'rateSource': 'category_rates_per_kg'
                                }
                            },
                            'fallback_global_rate': {
                                'summary': 'Fallback to global rate',
                                'value': {
                                    'deliveryId': '46e818ce-0518-4c64-8438-27bc7163a706',
                                    'currency': 'Rials',
                                    'breakdown': [],
                                    'totalWeight': '20.50',
                                    'totalAmount': '205000.00',
                                    'rateSource': 'waste_price_per_kg'
                                }
                            }
                        }
                    }
                }
            }
        }
    )
    @action(detail=True, methods=['get'], url_path='price')
    def price(self, request, pk=None):
        """Calculate per-delivery price based on category rates configuration."""
        from decimal import Decimal
        import json
        delivery = self.get_object()

        # Load category rates from configuration
        currency = 'Rials'
        category_rates = {}
        global_rate = Decimal('0')
        try:
            from zistino_apps.configurations.models import Configuration
            # Category rates config: list of {categoryId, rate, currency} or single dict
            cat_cfg = Configuration.objects.filter(name__icontains='category_rates_per_kg', is_active=True).first()
            if cat_cfg and cat_cfg.value:
                val = cat_cfg.value
                # Handle both list and single dict
                if isinstance(val, dict):
                    # Single category rate
                    try:
                        cid = str(val.get('categoryId'))
                        rate = Decimal(str(val.get('rate', 0)))
                        if cid and rate:
                            category_rates[cid] = rate
                        if val.get('currency'):
                            currency = str(val.get('currency'))
                    except Exception:
                        pass
                elif isinstance(val, list):
                    # List of category rates
                    for e in val:
                        try:
                            cid = str(e.get('categoryId'))
                            rate = Decimal(str(e.get('rate', 0)))
                            if cid and rate:
                                category_rates[cid] = rate
                            if e.get('currency'):
                                currency = str(e.get('currency'))
                        except Exception:
                            continue
            # Global fallback
            glob_cfg = Configuration.objects.filter(name__icontains='waste_price_per_kg', is_active=True).first()
            if glob_cfg and glob_cfg.value is not None:
                g = glob_cfg.value
                if isinstance(g, dict):
                    if g.get('currency'):
                        currency = str(g.get('currency'))
                    if g.get('rate') is not None:
                        global_rate = Decimal(str(g.get('rate')))
                elif isinstance(g, (int, float, str)):
                    try:
                        global_rate = Decimal(str(g))
                    except Exception:
                        pass
        except Exception:
            pass

        # Build breakdown using DeliveryItems if available
        from zistino_apps.deliveries.models import DeliveryItem
        items = DeliveryItem.objects.filter(delivery=delivery).select_related('category')
        breakdown = []
        total_weight = Decimal('0.00')
        total_amount = Decimal('0.00')
        rate_source = 'category_rates_per_kg'
        if items.exists() and category_rates:
            for it in items:
                w = Decimal(str(it.weight or 0))
                total_weight += w
                cid = str(it.category.id)
                rate = category_rates.get(cid, None)
                if rate is None:
                    # if category rate missing, fall back to global
                    rate = global_rate
                    rate_source = 'mixed_with_global'
                amount = (w * (rate or Decimal('0'))).quantize(Decimal('0.01'))
                total_amount += amount
                breakdown.append({
                    'categoryId': cid,
                    'categoryName': it.category.name,
                    'weight': f"{w:.2f}",
                    'rate': f"{(rate or Decimal('0')):.2f}",
                    'amount': f"{amount:.2f}"
                })
        else:
            # Fallback: use delivered_weight and global rate
            total_weight = Decimal(str(delivery.delivered_weight or 0))
            total_amount = (total_weight * (global_rate or Decimal('0'))).quantize(Decimal('0.01'))
            breakdown = []
            rate_source = 'waste_price_per_kg'

        return Response({
            'deliveryId': str(delivery.id),
            'currency': currency,
            'breakdown': breakdown,
            'totalWeight': f"{total_weight:.2f}",
            'totalAmount': f"{total_amount:.2f}",
            'rateSource': rate_source
        })


# ============================================
# ADMIN ENDPOINTS - Separated for clarity
# ============================================
# These endpoints are for admin panel (is_staff=True)
# They provide admin-level access with search/pagination
# ============================================

@extend_schema(
    tags=['Admin'],
    operation_id='manager_disapprovals',
    summary='View disapprovals and explanations',
    description='Manager view of all disapprovals: customer delivery denials, driver non-deliveries, and center denials with explanations.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 20},
                'type': {'type': 'string', 'enum': ['customer_denial', 'driver_non_delivery', 'center_denial', 'all'], 'default': 'all'},
                'dateFrom': {'type': 'string', 'format': 'date-time'},
                'dateTo': {'type': 'string', 'format': 'date-time'}
            }
        }
    },
    examples=[
        OpenApiExample('All disapprovals', value={'pageNumber': 1, 'pageSize': 20, 'type': 'all'}),
        OpenApiExample('Customer denials only', value={'pageNumber': 1, 'pageSize': 20, 'type': 'customer_denial'}),
        OpenApiExample('Driver non-deliveries only', value={'pageNumber': 1, 'pageSize': 20, 'type': 'driver_non_delivery'})
    ],
    responses={
        200: {
            'description': 'Disapprovals list',
            'content': {
                'application/json': {
                    'example': {
                        'items': [
                            {
                                'deliveryId': 'delivery-uuid',
                                'type': 'customer_denial',
                                'customerPhone': '+989121234567',
                                'driverPhone': '+989121234568',
                                'deliveryDate': '2025-11-03T14:00:00Z',
                                'explanation': 'Delivered weight does not match expected amount',
                                'createdAt': '2025-11-03T15:00:00Z'
                            },
                            {
                                'deliveryId': 'delivery-uuid-2',
                                'type': 'driver_non_delivery',
                                'customerPhone': '+989121234567',
                                'driverPhone': '+989121234568',
                                'deliveryDate': '2025-11-03T14:00:00Z',
                                'explanation': 'Customer unavailable at the address',
                                'createdAt': '2025-11-03T14:30:00Z'
                            }
                        ],
                        'total': 50,
                        'pageNumber': 1,
                        'pageSize': 20
                    }
                }
            }
        }
    }
)
class ManagerDisapprovalsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        from django.utils.dateparse import parse_datetime
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        disapproval_type = request.data.get('type', 'all')
        date_from = request.data.get('dateFrom')
        date_to = request.data.get('dateTo')

        # Build query for customer denials
        customer_denials = Delivery.objects.filter(customer_confirmation_status='denied', denial_reason__isnull=False).exclude(denial_reason='')
        if date_from:
            dt_from = parse_datetime(date_from)
            if dt_from:
                customer_denials = customer_denials.filter(updated_at__gte=dt_from)
        if date_to:
            dt_to = parse_datetime(date_to)
            if dt_to:
                customer_denials = customer_denials.filter(updated_at__lte=dt_to)

        # Build query for driver non-deliveries (cancelled by driver)
        driver_non_deliveries = Delivery.objects.filter(status='cancelled', cancel_reason__isnull=False).exclude(cancel_reason='')
        if date_from:
            dt_from = parse_datetime(date_from)
            if dt_from:
                driver_non_deliveries = driver_non_deliveries.filter(updated_at__gte=dt_from)
        if date_to:
            dt_to = parse_datetime(date_to)
            if dt_to:
                driver_non_deliveries = driver_non_deliveries.filter(updated_at__lte=dt_to)

        # Combine based on type filter
        items = []
        if disapproval_type in ['all', 'customer_denial']:
            for d in customer_denials.select_related('order__user', 'driver'):
                items.append({
                    'deliveryId': str(d.id),
                    'type': 'customer_denial',
                    'customerPhone': d.order.user.phone_number if d.order and d.order.user else 'N/A',
                    'driverPhone': d.driver.phone_number if d.driver else 'N/A',
                    'deliveryDate': d.delivery_date.isoformat() if d.delivery_date else None,
                    'explanation': d.denial_reason,
                    'createdAt': d.updated_at.isoformat()
                })

        if disapproval_type in ['all', 'driver_non_delivery']:
            for d in driver_non_deliveries.select_related('order__user', 'driver'):
                items.append({
                    'deliveryId': str(d.id),
                    'type': 'driver_non_delivery',
                    'customerPhone': d.order.user.phone_number if d.order and d.order.user else 'N/A',
                    'driverPhone': d.driver.phone_number if d.driver else 'N/A',
                    'deliveryDate': d.delivery_date.isoformat() if d.delivery_date else None,
                    'explanation': d.cancel_reason,
                    'createdAt': d.updated_at.isoformat()
                })

        # Sort by createdAt (most recent first)
        items.sort(key=lambda x: x['createdAt'], reverse=True)

        # Pagination
        total = len(items)
        start = (page_number - 1) * page_size
        end = start + page_size
        paginated_items = items[start:end]

        return Response({
            'items': paginated_items,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_driver_routes',
    summary='View driver routes with pickup locations and dwell times',
    description='Manager view of driver navigation routes for a specific date. Shows routes traveled, pickup locations (where cargo was collected), and time spent at each pickup location. Analyzes existing Trip, LocationUpdate, and Delivery data without modifying models.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'date': {'type': 'string', 'format': 'date', 'description': 'Date to analyze routes (YYYY-MM-DD). Defaults to today if not provided.'},
            }
        }
    },
    examples=[
        OpenApiExample('Routes for specific date', value={'date': '2025-11-03'}),
        OpenApiExample('Routes for today', value={})
    ],
    responses={
        200: {
            'description': 'Driver routes and pickup locations',
            'content': {
                'application/json': {
                    'example': {
                        'driverId': 'driver-uuid',
                        'driverPhone': '+989121234567',
                        'date': '2025-11-03',
                        'trips': [
                            {
                                'tripId': 1,
                                'startTime': '2025-11-03T08:00:00Z',
                                'endTime': '2025-11-03T14:30:00Z',
                                'distance': 45.5,
                                'duration': 23400,
                                'averageSpeed': 35.2,
                                'routePoints': [
                                    {'latitude': 35.6892, 'longitude': 51.3890, 'timestamp': '2025-11-03T08:00:00Z', 'speed': 0},
                                    {'latitude': 35.6900, 'longitude': 51.3900, 'timestamp': '2025-11-03T08:05:00Z', 'speed': 45}
                                ],
                                'pickupLocations': [
                                    {
                                        'deliveryId': 'delivery-uuid-1',
                                        'customerAddress': 'No. 10, Example Street',
                                        'customerPhone': '+989121234567',
                                        'latitude': 35.6892,
                                        'longitude': 51.3890,
                                        'arrivalTime': '2025-11-03T08:15:00Z',
                                        'departureTime': '2025-11-03T08:25:00Z',
                                        'timeSpentSeconds': 600,
                                        'timeSpentFormatted': '10 minutes',
                                        'deliveredWeight': '12.50'
                                    }
                                ]
                            }
                        ],
                        'summary': {
                            'totalTrips': 1,
                            'totalDistance': 45.5,
                            'totalDuration': 23400,
                            'totalPickups': 3,
                            'averageTimePerPickup': 600
                        }
                    }
                }
            }
        }
    }
)
class ManagerDriverRouteView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request, driver_id):
        from django.contrib.auth import get_user_model
        from django.utils.dateparse import parse_date
        from datetime import datetime, timedelta

        User = get_user_model()
        
        # Get driver
        try:
            driver = User.objects.get(id=driver_id, is_driver=True)
        except User.DoesNotExist:
            return Response({'detail': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Parse date (default to today)
        from django.utils import timezone
        date_str = request.data.get('date')
        if date_str:
            target_date = parse_date(date_str)
            if not target_date:
                return Response({'detail': 'Invalid date format. Use YYYY-MM-DD'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            target_date = timezone.now().date()

        # Date range for the day (timezone-aware)
        date_start = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
        date_end = timezone.make_aware(datetime.combine(target_date, datetime.max.time()))

        # Get trips for this driver on this date
        trips = Trip.objects.filter(
            user=driver,
            created_at__gte=date_start,
            created_at__lte=date_end
        ).order_by('created_at')

        # Get deliveries for this driver on this date
        deliveries = Delivery.objects.filter(
            driver=driver,
            delivery_date__gte=date_start,
            delivery_date__lte=date_end
        ).select_related('order', 'order__user')

        # Build response
        trips_data = []
        total_distance = 0
        total_duration = 0
        total_pickups = 0
        total_pickup_time = 0
        matched_deliveries = set()  # Track deliveries already matched to avoid duplicates

        for trip in trips:
            # Get location updates for this trip
            locations = LocationUpdate.objects.filter(
                trip=trip
            ).order_by('created_at')

            route_points = []
            for loc in locations:
                route_points.append({
                    'latitude': float(loc.latitude),
                    'longitude': float(loc.longitude),
                    'timestamp': loc.created_at.isoformat(),
                    'speed': loc.speed
                })

            # Find pickup locations by matching deliveries to location updates
            pickup_locations = []
            for delivery in deliveries:
                if not delivery.latitude or not delivery.longitude:
                    continue
                
                # Skip if already matched to another trip
                if delivery.id in matched_deliveries:
                    continue

                # Find location updates where driver stopped near delivery location
                # Threshold: within 100 meters (approx 0.001 degrees)
                delivery_lat = float(delivery.latitude)
                delivery_lng = float(delivery.longitude)
                threshold = 0.001  # ~100 meters

                pickup_locs = []
                for loc in locations:
                    lat_diff = abs(float(loc.latitude) - delivery_lat)
                    lng_diff = abs(float(loc.longitude) - delivery_lng)
                    
                    # If stopped near delivery location (speed < 5 km/h or 0)
                    if lat_diff < threshold and lng_diff < threshold and loc.speed < 5:
                        pickup_locs.append(loc)

                if pickup_locs:
                    # Mark as matched
                    matched_deliveries.add(delivery.id)
                    
                    # Calculate arrival and departure times
                    arrival = min(pickup_locs, key=lambda x: x.created_at)
                    departure = max(pickup_locs, key=lambda x: x.created_at)
                    
                    time_spent = (departure.created_at - arrival.created_at).total_seconds()
                    
                    # Format time spent
                    minutes = int(time_spent // 60)
                    seconds = int(time_spent % 60)
                    if minutes > 0:
                        time_formatted = f"{minutes} minute{'s' if minutes != 1 else ''}"
                        if seconds > 0:
                            time_formatted += f" {seconds} second{'s' if seconds != 1 else ''}"
                    else:
                        time_formatted = f"{seconds} second{'s' if seconds != 1 else ''}"

                    pickup_locations.append({
                        'deliveryId': str(delivery.id),
                        'customerAddress': delivery.address,
                        'customerPhone': delivery.phone_number,
                        'latitude': delivery_lat,
                        'longitude': delivery_lng,
                        'arrivalTime': arrival.created_at.isoformat(),
                        'departureTime': departure.created_at.isoformat(),
                        'timeSpentSeconds': int(time_spent),
                        'timeSpentFormatted': time_formatted,
                        'deliveredWeight': f"{delivery.delivered_weight:.2f}" if delivery.delivered_weight else "0.00"
                    })
                    
                    total_pickup_time += time_spent
                    total_pickups += 1

            trips_data.append({
                'tripId': trip.id,
                'startTime': trip.created_at.isoformat(),
                'endTime': (trip.created_at + timedelta(seconds=trip.duration)).isoformat() if trip.duration else None,
                'distance': float(trip.distance / 1000) if trip.distance else 0.0,  # Convert to km
                'duration': trip.duration,
                'averageSpeed': float(trip.average_speed) if trip.average_speed else 0.0,
                'routePoints': route_points,
                'pickupLocations': pickup_locations
            })

            total_distance += float(trip.distance / 1000) if trip.distance else 0.0
            total_duration += trip.duration or 0

        # Calculate summary
        avg_pickup_time = total_pickup_time / total_pickups if total_pickups > 0 else 0

        return Response({
            'driverId': str(driver.id),
            'driverPhone': driver.phone_number,
            'date': target_date.isoformat(),
            'trips': trips_data,
            'summary': {
                'totalTrips': len(trips_data),
                'totalDistance': round(total_distance, 2),
                'totalDuration': total_duration,
                'totalPickups': total_pickups,
                'averageTimePerPickup': int(avg_pickup_time)
            }
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_weight_range_minimums',
    summary='Configure minimum weights per weight range',
    description='Manager endpoint to set minimum weights for each weight range. When delivered weight is less than minimum, a shortfall is created and deducted from next delivery.',
    request=WeightRangeMinimumConfigSerializer,
    examples=[
        OpenApiExample(
            'Set minimum weights',
            value={
                'ranges': [
                    {'value': '2-5', 'min': 2},
                    {'value': '5-10', 'min': 5},
                    {'value': '10-20', 'min': 10},
                    {'value': '20-50', 'min': 20},
                    {'value': '50+', 'min': 50}
                ]
            }
        )
    ],
    responses={
        200: {
            'description': 'Configuration saved',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Weight range minimums configured',
                        'ranges': [
                            {'value': '2-5', 'min': 2},
                            {'value': '5-10', 'min': 5}
                        ]
                    }
                }
            }
        }
    }
)
class ManagerWeightRangeMinimumsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        from zistino_apps.configurations.models import Configuration
        serializer = WeightRangeMinimumConfigSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ranges = serializer.validated_data['ranges']

        # Save to Configuration
        config, created = Configuration.objects.get_or_create(
            name='weight_range_minimum',
            defaults={'value': ranges, 'is_active': True}
        )
        if not created:
            config.value = ranges
            config.is_active = True
            config.save()

        return Response({
            'message': 'Weight range minimums configured',
            'ranges': ranges
        }, status=status.HTTP_200_OK)

    def get(self, request):
        """Get current minimum weight configuration."""
        from zistino_apps.configurations.models import Configuration
        config = Configuration.objects.filter(name__icontains='weight_range_minimum', is_active=True).first()
        
        if config and config.value:
            return Response({
                'ranges': config.value if isinstance(config.value, list) else []
            })
        
        return Response({
            'ranges': [],
            'message': 'No minimum weight configuration found'
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_weight_shortfalls',
    summary='View weight shortfalls',
    description='Manager view of all weight shortfalls with filtering by customer, date range, and deduction status.',
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'pageNumber': {'type': 'integer', 'default': 1},
                'pageSize': {'type': 'integer', 'default': 20},
                'userId': {'type': 'string', 'format': 'uuid', 'description': 'Filter by customer UUID'},
                'isDeducted': {'type': 'boolean', 'description': 'Filter by deduction status'},
                'dateFrom': {'type': 'string', 'format': 'date-time'},
                'dateTo': {'type': 'string', 'format': 'date-time'}
            }
        }
    },
    examples=[
        OpenApiExample('All shortfalls', value={'pageNumber': 1, 'pageSize': 20}),
        OpenApiExample('Undeducted only', value={'pageNumber': 1, 'pageSize': 20, 'isDeducted': False}),
        OpenApiExample('By customer', value={'pageNumber': 1, 'pageSize': 20, 'userId': 'user-uuid'})
    ],
    responses={
        200: {
            'description': 'Shortfalls list',
            'content': {
                'application/json': {
                    'example': {
                        'items': [
                            {
                                'id': 'shortfall-uuid',
                                'userId': 'user-uuid',
                                'userPhone': '+989121234567',
                                'deliveryId': 'delivery-uuid',
                                'estimated_range': '5-10',
                                'minimum_weight': '5.00',
                                'delivered_weight': '3.50',
                                'shortfallAmount': '-1.50',
                                'is_deducted': False,
                                'deductedFromDeliveryId': None,
                                'createdAt': '2025-11-03T10:00:00Z'
                            }
                        ],
                        'total': 50,
                        'pageNumber': 1,
                        'pageSize': 20
                    }
                }
            }
        }
    }
)
class ManagerWeightShortfallsView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        from django.utils.dateparse import parse_datetime
        
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        user_id = request.data.get('userId')
        is_deducted = request.data.get('isDeducted')
        date_from = request.data.get('dateFrom')
        date_to = request.data.get('dateTo')

        qs = WeightShortfall.objects.all().select_related('user', 'delivery', 'deducted_from_delivery')

        # Filters
        if user_id:
            qs = qs.filter(user_id=user_id)
        if is_deducted is not None:
            qs = qs.filter(is_deducted=is_deducted)
        if date_from:
            dt_from = parse_datetime(date_from)
            if dt_from:
                qs = qs.filter(created_at__gte=dt_from)
        if date_to:
            dt_to = parse_datetime(date_to)
            if dt_to:
                qs = qs.filter(created_at__lte=dt_to)

        # Pagination
        total = qs.count()
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]

        return Response({
            'items': WeightShortfallSerializer(items, many=True).data,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size
        })


@extend_schema(
    tags=['Admin'],
    operation_id='manager_driver_available_dates',
    summary='List dates with trips/deliveries data for a driver',
    description='Manager view to find which dates have trip and delivery data for a specific driver. Helps identify dates to query for route tracking.',
    request=None,
    responses={
        200: {
            'description': 'Available dates with data counts',
            'content': {
                'application/json': {
                    'example': {
                        'driverId': 'driver-uuid',
                        'driverPhone': '+989121234567',
                        'availableDates': [
                            {
                                'date': '2025-11-03',
                                'tripCount': 2,
                                'deliveryCount': 5,
                                'locationUpdateCount': 120
                            },
                            {
                                'date': '2025-11-02',
                                'tripCount': 1,
                                'deliveryCount': 3,
                                'locationUpdateCount': 85
                            }
                        ],
                        'total': 2
                    }
                }
            }
        }
    }
)
class ManagerDriverAvailableDatesView(APIView):
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request, driver_id):
        from django.contrib.auth import get_user_model
        from django.db.models import Count

        User = get_user_model()
        
        # Get driver
        try:
            driver = User.objects.get(id=driver_id, is_driver=True)
        except User.DoesNotExist:
            return Response({'detail': 'Driver not found'}, status=status.HTTP_404_NOT_FOUND)

        # Get all trip dates
        trips = Trip.objects.filter(user=driver).values('created_at__date').annotate(
            trip_count=Count('id')
        ).order_by('-created_at__date')

        # Get all delivery dates
        deliveries = Delivery.objects.filter(
            driver=driver,
            delivery_date__isnull=False
        ).values('delivery_date__date').annotate(
            delivery_count=Count('id')
        ).order_by('-delivery_date__date')

        # Get all location update dates (from trips)
        location_updates = LocationUpdate.objects.filter(
            user=driver
        ).values('created_at__date').annotate(
            location_count=Count('id')
        ).order_by('-created_at__date')

        # Combine into a dictionary
        dates_dict = {}
        
        # Add trip dates
        for trip in trips:
            date_str = trip['created_at__date'].isoformat() if trip['created_at__date'] else None
            if date_str:
                if date_str not in dates_dict:
                    dates_dict[date_str] = {
                        'date': date_str,
                        'tripCount': 0,
                        'deliveryCount': 0,
                        'locationUpdateCount': 0
                    }
                dates_dict[date_str]['tripCount'] = trip['trip_count']
        
        # Add delivery dates
        for delivery in deliveries:
            date_str = delivery['delivery_date__date'].isoformat() if delivery['delivery_date__date'] else None
            if date_str:
                if date_str not in dates_dict:
                    dates_dict[date_str] = {
                        'date': date_str,
                        'tripCount': 0,
                        'deliveryCount': 0,
                        'locationUpdateCount': 0
                    }
                dates_dict[date_str]['deliveryCount'] = delivery['delivery_count']
        
        # Add location update dates
        for loc in location_updates:
            date_str = loc['created_at__date'].isoformat() if loc['created_at__date'] else None
            if date_str:
                if date_str not in dates_dict:
                    dates_dict[date_str] = {
                        'date': date_str,
                        'tripCount': 0,
                        'deliveryCount': 0,
                        'locationUpdateCount': 0
                    }
                dates_dict[date_str]['locationUpdateCount'] = loc['location_count']

        # Convert to sorted list (most recent first)
        available_dates = sorted(dates_dict.values(), key=lambda x: x['date'], reverse=True)

        return Response({
            'driverId': str(driver.id),
            'driverPhone': driver.phone_number,
            'availableDates': available_dates,
            'total': len(available_dates)
        })


@extend_schema(
    tags=['Admin'],
    operation_id='driverdelivery_search',
    request=DeliverySearchRequestSerializer,
    examples=[
        OpenApiExample(
            'Search all deliveries',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'status': None
            }
        ),
        OpenApiExample(
            'Search by keyword',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'pending',
                'status': None
            }
        ),
        OpenApiExample(
            'Search by status',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': '',
                'status': 1
            }
        ),
        OpenApiExample(
            'Search with keyword and status',
            value={
                'pageNumber': 1,
                'pageSize': 20,
                'keyword': 'John',
                'status': 0
            }
        )
    ]
)
class AdminDeliverySearchView(APIView):
    """Admin search endpoint for deliveries with pagination and status filter."""
    permission_classes = [IsAuthenticated, IsManager]

    def post(self, request):
        """Search deliveries with pagination and filters."""
        page_number = int(request.data.get('pageNumber') or 1)
        page_size = int(request.data.get('pageSize') or 20)
        keyword = (request.data.get('keyword') or '').strip()
        status_filter = request.data.get('status')
        
        qs = Delivery.objects.all().select_related('driver', 'order').order_by('-created_at')
        
        # Filter by status if provided
        if status_filter is not None:
            qs = qs.filter(status=status_filter)
        
        # Filter by keyword (search in driver name, order ID, address, phone, description)
        if keyword:
            qs = qs.filter(
                Q(driver__first_name__icontains=keyword) |
                Q(driver__last_name__icontains=keyword) |
                Q(driver__phone_number__icontains=keyword) |
                Q(order__id__icontains=keyword) |
                Q(address__icontains=keyword) |
                Q(phone_number__icontains=keyword) |
                Q(description__icontains=keyword)
            )
        
        start = (page_number - 1) * page_size
        end = start + page_size
        items = qs[start:end]
        
        return Response({
            'items': DeliverySerializer(items, many=True).data,
            'pageNumber': page_number,
            'pageSize': page_size,
            'total': qs.count(),
        })


@extend_schema(tags=['Manager'])
class ManagerTripViewSet(viewsets.ModelViewSet):
    """ViewSet for managers to manage all trips - Manager-only."""
    queryset = Trip.objects.all()
    serializer_class = TripSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all trips (no filtering by user)."""
        return Trip.objects.all().select_related('user').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create trip - manager can create for any user."""
        serializer.save()  # User is set in request data
    
    @action(detail=True, methods=['put', 'patch'], url_path='end')
    @extend_schema(operation_id='manager_end_trip')
    def end_trip(self, request, pk=None):
        """End a trip - update trip with end location and final stats."""
        trip = self.get_object()
        serializer = self.get_serializer(trip, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@extend_schema(tags=['Manager'])
class ManagerLocationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for managers to view all location updates - Manager-only."""
    queryset = LocationUpdate.objects.all()
    serializer_class = LocationUpdateSerializer
    permission_classes = [IsAuthenticated, IsManager]
    
    def get_queryset(self):
        """Return all location updates (no filtering by user)."""
        return LocationUpdate.objects.all().select_related('user', 'trip').order_by('-created_at')


@extend_schema(
    tags=['Admin'],
    operation_id='manager_survey_questions_list',
    summary='List all survey questions',
    description='Manager endpoint to list all survey questions (active and inactive).',
    responses={
        200: {
            'description': 'List of survey questions',
            'content': {
                'application/json': {
                    'examples': {
                        'questions': {
                            'summary': 'Survey questions list',
                            'value': {
                                'items': [
                                    {
                                        'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                        'questionText': 'How was the driver\'s service?',
                                        'questionType': 'rating',
                                        'options': None,
                                        'isActive': True,
                                        'isRequired': True,
                                        'order': 1,
                                        'createdAt': '2025-01-15T10:00:00Z',
                                        'updatedAt': '2025-01-15T10:00:00Z'
                                    },
                                    {
                                        'questionId': 'xyz98765-4321-0abc-defghijklmnop',
                                        'questionText': 'Was the driver on time?',
                                        'questionType': 'yes_no',
                                        'options': None,
                                        'isActive': True,
                                        'isRequired': False,
                                        'order': 2,
                                        'createdAt': '2025-01-15T10:05:00Z',
                                        'updatedAt': '2025-01-15T10:05:00Z'
                                    }
                                ],
                                'total': 2
                            }
                        }
                    }
                }
            }
        }
    }
)
class ManagerSurveyQuestionsListView(APIView):
    """Manager endpoint to list all survey questions."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def get(self, request):
        """List all survey questions."""
        questions = SurveyQuestion.objects.all().order_by('order', 'created_at')
        serializer = SurveyQuestionSerializer(questions, many=True)
        return Response({
            'items': serializer.data,
            'total': questions.count()
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin'],
    operation_id='manager_survey_question_create',
    summary='Create survey question',
    description='Manager endpoint to create a new survey question.',
    request=SurveyQuestionCreateSerializer,
    examples=[
        OpenApiExample(
            'Create rating question',
            value={
                'questionText': 'How would you rate the driver\'s service?',
                'questionType': 'rating',
                'isActive': True,
                'isRequired': True,
                'order': 1
            }
        ),
        OpenApiExample(
            'Create yes/no question',
            value={
                'questionText': 'Was the driver on time?',
                'questionType': 'yes_no',
                'isActive': True,
                'isRequired': False,
                'order': 2
            }
        ),
        OpenApiExample(
            'Create multiple choice question',
            value={
                'questionText': 'How did you hear about us?',
                'questionType': 'multiple_choice',
                'options': ['Friend', 'Social Media', 'Advertisement', 'Other'],
                'isActive': True,
                'isRequired': False,
                'order': 3
            }
        ),
        OpenApiExample(
            'Create text question',
            value={
                'questionText': 'Any additional comments?',
                'questionType': 'text',
                'isActive': True,
                'isRequired': False,
                'order': 4
            }
        )
    ],
    responses={
        201: {
            'description': 'Survey question created successfully',
            'content': {
                'application/json': {
                    'examples': {
                        'created': {
                            'summary': 'Question created',
                            'value': {
                                'message': 'Survey question created successfully.',
                                'question': {
                                    'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                    'questionText': 'How would you rate the driver\'s service?',
                                    'questionType': 'rating',
                                    'options': None,
                                    'isActive': True,
                                    'isRequired': True,
                                    'order': 1,
                                    'createdAt': '2025-01-15T10:00:00Z',
                                    'updatedAt': '2025-01-15T10:00:00Z'
                                }
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Bad request',
            'content': {
                'application/json': {
                    'example': {
                        'questionText': ['This field is required.'],
                        'questionType': ['Invalid choice.']
                    }
                }
            }
        }
    }
)
class ManagerSurveyQuestionCreateView(APIView):
    """Manager endpoint to create a survey question."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def post(self, request):
        """Create a new survey question."""
        serializer = SurveyQuestionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        question = SurveyQuestion.objects.create(
            question_text=serializer.validated_data['questionText'],
            question_type=serializer.validated_data['questionType'],
            options=serializer.validated_data.get('options'),
            is_active=serializer.validated_data.get('isActive', True),
            is_required=serializer.validated_data.get('isRequired', False),
            order=serializer.validated_data.get('order', 0)
        )
        
        return Response({
            'message': 'Survey question created successfully.',
            'question': SurveyQuestionSerializer(question).data
        }, status=status.HTTP_201_CREATED)


@extend_schema(
    tags=['Admin'],
    operation_id='manager_survey_question_update',
    summary='Update survey question',
    description='Manager endpoint to update an existing survey question.',
    request=SurveyQuestionUpdateSerializer,
    examples=[
        OpenApiExample(
            'Update question text',
            value={
                'questionText': 'How satisfied were you with the delivery?',
                'isActive': True
            }
        ),
        OpenApiExample(
            'Deactivate question',
            value={
                'isActive': False
            }
        ),
        OpenApiExample(
            'Update order',
            value={
                'order': 5
            }
        )
    ],
    responses={
        200: {
            'description': 'Survey question updated successfully',
            'content': {
                'application/json': {
                    'examples': {
                        'updated': {
                            'summary': 'Question updated',
                            'value': {
                                'message': 'Survey question updated successfully.',
                                'question': {
                                    'questionId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                    'questionText': 'How satisfied were you with the delivery?',
                                    'questionType': 'rating',
                                    'options': None,
                                    'isActive': True,
                                    'isRequired': True,
                                    'order': 1,
                                    'createdAt': '2025-01-15T10:00:00Z',
                                    'updatedAt': '2025-01-15T10:30:00Z'
                                }
                            }
                        }
                    }
                }
            }
        },
        404: {
            'description': 'Question not found',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Survey question not found'
                    }
                }
            }
        }
    }
)
class ManagerSurveyQuestionUpdateView(APIView):
    """Manager endpoint to update a survey question."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def put(self, request, question_id):
        """Update a survey question."""
        try:
            question = SurveyQuestion.objects.get(id=question_id)
        except SurveyQuestion.DoesNotExist:
            return Response(
                {'detail': 'Survey question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = SurveyQuestionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Update fields if provided
        if 'questionText' in serializer.validated_data:
            question.question_text = serializer.validated_data['questionText']
        if 'questionType' in serializer.validated_data:
            question.question_type = serializer.validated_data['questionType']
        if 'options' in serializer.validated_data:
            question.options = serializer.validated_data['options']
        if 'isActive' in serializer.validated_data:
            question.is_active = serializer.validated_data['isActive']
        if 'isRequired' in serializer.validated_data:
            question.is_required = serializer.validated_data['isRequired']
        if 'order' in serializer.validated_data:
            question.order = serializer.validated_data['order']
        
        question.save()
        
        return Response({
            'message': 'Survey question updated successfully.',
            'question': SurveyQuestionSerializer(question).data
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin'],
    operation_id='manager_survey_question_delete',
    summary='Delete survey question',
    description='Manager endpoint to delete a survey question.',
    responses={
        200: {
            'description': 'Survey question deleted successfully',
            'content': {
                'application/json': {
                    'example': {
                        'message': 'Survey question deleted successfully.'
                    }
                }
            }
        },
        404: {
            'description': 'Question not found',
            'content': {
                'application/json': {
                    'example': {
                        'detail': 'Survey question not found'
                    }
                }
            }
        }
    }
)
class ManagerSurveyQuestionDeleteView(APIView):
    """Manager endpoint to delete a survey question."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def delete(self, request, question_id):
        """Delete a survey question."""
        try:
            question = SurveyQuestion.objects.get(id=question_id)
            question.delete()
            return Response(
                {'message': 'Survey question deleted successfully.'},
                status=status.HTTP_200_OK
            )
        except SurveyQuestion.DoesNotExist:
            return Response(
                {'detail': 'Survey question not found'},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema(
    tags=['Admin'],
    operation_id='manager_driver_satisfaction',
    summary='View driver satisfaction ratings',
    description='Manager endpoint to view customer satisfaction with each driver based on survey ratings. Shows aggregated statistics and individual survey details.',
    request=ManagerDriverSatisfactionRequestSerializer,
    examples=[
        OpenApiExample(
            'View all drivers',
            value={
                'pageNumber': 1,
                'pageSize': 20
            }
        ),
        OpenApiExample(
            'Filter by driver',
            value={
                'driverId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                'pageNumber': 1,
                'pageSize': 20
            }
        ),
        OpenApiExample(
            'Filter by date range',
            value={
                'startDate': '2025-01-01',
                'endDate': '2025-01-31',
                'pageNumber': 1,
                'pageSize': 20
            }
        )
    ],
    responses={
        200: {
            'description': 'Driver satisfaction data',
            'content': {
                'application/json': {
                    'examples': {
                        'satisfaction': {
                            'summary': 'Driver satisfaction report',
                            'value': {
                                'items': [
                                    {
                                        'driverId': '0641067f-df76-416c-98cd-6f89e43d3b3f',
                                        'driverPhone': '+989056761466',
                                        'driverName': 'John Doe',
                                        'totalSurveys': 25,
                                        'averageRating': 4.6,
                                        'ratingDistribution': {
                                            '1': 0,
                                            '2': 1,
                                            '3': 2,
                                            '4': 8,
                                            '5': 14
                                        },
                                        'totalDeliveries': 30,
                                        'surveyCompletionRate': 83.33,
                                        'recentSurveys': [
                                            {
                                                'surveyId': 'abc12345-def6-7890-ghij-klmnopqrstuv',
                                                'deliveryId': 'fe0e0a41-d626-46c7-ba3a-c506fbd2024b',
                                                'rating': 5,
                                                'comment': 'Excellent service!',
                                                'createdAt': '2025-01-15T10:00:00Z'
                                            }
                                        ]
                                    }
                                ],
                                'total': 1,
                                'pageNumber': 1,
                                'pageSize': 20,
                                'totalPages': 1
                            }
                        }
                    }
                }
            }
        }
    }
)
class ManagerDriverSatisfactionView(APIView):
    """Manager endpoint to view driver satisfaction ratings."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def post(self, request):
        """View driver satisfaction based on survey ratings."""
        serializer = ManagerDriverSatisfactionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        driver_id = serializer.validated_data.get('driverId')
        start_date = serializer.validated_data.get('startDate')
        end_date = serializer.validated_data.get('endDate')
        page_number = serializer.validated_data.get('pageNumber', 1)
        page_size = serializer.validated_data.get('pageSize', 20)
        
        # Get surveys with ratings
        surveys_query = DeliverySurvey.objects.select_related('delivery__driver', 'user').all()
        
        # Filter by driver
        if driver_id:
            surveys_query = surveys_query.filter(delivery__driver_id=driver_id)
        
        # Filter by date range
        if start_date:
            surveys_query = surveys_query.filter(created_at__date__gte=start_date)
        if end_date:
            surveys_query = surveys_query.filter(created_at__date__lte=end_date)
        
        # Group by driver
        from django.contrib.auth import get_user_model
        from django.db.models import Count, Avg, Q
        User = get_user_model()
        
        drivers_with_surveys = User.objects.filter(
            deliveries__survey__isnull=False
        ).distinct()
        
        if driver_id:
            drivers_with_surveys = drivers_with_surveys.filter(id=driver_id)
        
        driver_stats = []
        for driver in drivers_with_surveys:
            driver_surveys = surveys_query.filter(delivery__driver=driver)
            
            if start_date:
                driver_surveys = driver_surveys.filter(created_at__date__gte=start_date)
            if end_date:
                driver_surveys = driver_surveys.filter(created_at__date__lte=end_date)
            
            total_surveys = driver_surveys.count()
            if total_surveys == 0:
                continue
            
            avg_rating = driver_surveys.aggregate(avg=Avg('rating'))['avg'] or 0
            
            # Rating distribution
            rating_dist = {
                '1': driver_surveys.filter(rating=1).count(),
                '2': driver_surveys.filter(rating=2).count(),
                '3': driver_surveys.filter(rating=3).count(),
                '4': driver_surveys.filter(rating=4).count(),
                '5': driver_surveys.filter(rating=5).count()
            }
            
            # Total deliveries (regardless of survey)
            total_deliveries = Delivery.objects.filter(driver=driver).count()
            if start_date or end_date:
                delivery_filter = Q()
                if start_date:
                    delivery_filter &= Q(created_at__date__gte=start_date)
                if end_date:
                    delivery_filter &= Q(created_at__date__lte=end_date)
                total_deliveries = Delivery.objects.filter(driver=driver).filter(delivery_filter).count()
            
            survey_completion_rate = (total_surveys / total_deliveries * 100) if total_deliveries > 0 else 0
            
            # Recent surveys (last 5)
            recent_surveys = driver_surveys.select_related('delivery').order_by('-created_at')[:5]
            recent_surveys_data = [
                {
                    'surveyId': str(survey.id),
                    'deliveryId': str(survey.delivery.id),
                    'rating': survey.rating,
                    'comment': survey.comment,
                    'createdAt': survey.created_at.isoformat()
                }
                for survey in recent_surveys
            ]
            
            driver_stats.append({
                'driverId': str(driver.id),
                'driverPhone': driver.phone_number,
                'driverName': driver.get_full_name() or driver.username,
                'totalSurveys': total_surveys,
                'averageRating': round(avg_rating, 2),
                'ratingDistribution': rating_dist,
                'totalDeliveries': total_deliveries,
                'surveyCompletionRate': round(survey_completion_rate, 2),
                'recentSurveys': recent_surveys_data
            })
        
        # Sort by average rating (descending)
        driver_stats.sort(key=lambda x: x['averageRating'], reverse=True)
        
        # Pagination
        total = len(driver_stats)
        start_idx = (page_number - 1) * page_size
        end_idx = start_idx + page_size
        paginated_items = driver_stats[start_idx:end_idx]
        total_pages = (total + page_size - 1) // page_size
        
        return Response({
            'items': paginated_items,
            'total': total,
            'pageNumber': page_number,
            'pageSize': page_size,
            'totalPages': total_pages
        }, status=status.HTTP_200_OK)


@extend_schema(
    tags=['Admin'],
    operation_id='manager_delivery_reminder_check',
    summary='Manually trigger delivery reminder SMS check',
    description='Manager endpoint to manually trigger the task that checks for deliveries needing reminder SMS and sends them. '
                'The automatic task runs every 15 minutes via Celery Beat.\n\n'
                '**No request body required** - this endpoint only needs Authorization header.',
    request=None,  # No request body
    examples=[
        OpenApiExample(
            'Success Response',
            value={
                'message': 'Delivery reminder check completed successfully',
                'checked': 5,
                'sent': 3,
                'failed': 0,
                'timestamp': '2025-01-15T10:30:00.123456Z'
            },
            response_only=True,
        ),
        OpenApiExample(
            'No Deliveries Found',
            value={
                'message': 'Delivery reminder check completed successfully',
                'checked': 0,
                'sent': 0,
                'failed': 0,
                'timestamp': '2025-01-15T10:30:00.123456Z'
            },
            response_only=True,
        ),
        OpenApiExample(
            'Error Response',
            value={
                'message': 'Delivery reminder check failed',
                'error': 'Error message here',
                'timestamp': '2025-01-15T10:30:00.123456Z'
            },
            response_only=True,
        ),
    ]
)
class DeliveryReminderCheckView(APIView):
    """API endpoint to manually trigger delivery reminder SMS check."""
    permission_classes = [IsAuthenticated, IsManager]
    
    def post(self, request):
        """
        Manually trigger the delivery reminder check task.
        
        This will:
        - Find deliveries scheduled between 45-75 minutes from now
        - Send reminder SMS to customers
        - Mark deliveries as having reminder sent
        
        Returns task execution results.
        """
        try:
            # Run the task synchronously (for testing/manual trigger)
            result = check_and_send_delivery_reminders()
            
            if result.get('success'):
                return Response({
                    'message': 'Delivery reminder check completed successfully',
                    'checked': result.get('checked', 0),
                    'sent': result.get('sent', 0),
                    'failed': result.get('failed', 0),
                    'timestamp': result.get('timestamp')
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'message': 'Delivery reminder check failed',
                    'error': result.get('error', 'Unknown error'),
                    'timestamp': result.get('timestamp')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            return Response({
                'message': 'Error triggering delivery reminder check',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
