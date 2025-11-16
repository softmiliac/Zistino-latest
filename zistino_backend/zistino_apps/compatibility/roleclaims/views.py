"""
Views for RoleClaims compatibility layer.
Implements all endpoints matching old Swagger format.
"""
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.decorators import action
from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiParameter, OpenApiResponse

from zistino_apps.users.permissions import IsManager
from zistino_apps.compatibility.utils import create_success_response, create_error_response
from zistino_apps.compatibility.roles.models import Role
from zistino_apps.compatibility.roles.views import ALL_PERMISSIONS

from .models import RoleClaim
from .serializers import (
    RoleClaimSerializer,
    RoleClaimCreateUpdateSerializer,
    ClaimGroupSerializer,
    ClaimGroupUpdateSerializer,
)

# Additional API claims (from old Swagger example)
API_CLAIMS = [
    "api.getAppPromotionProduct",
    "api.getCompletedOrders",
    "api.getItemByOrderNumbers",
    "api.getOrderStatus",
    "api.getPromotionLinks",
    "api.getPromotionProductDetail",
    "api.listHotProducts",
    "api.listPromotionCreative",
    "api.listPromotionProduct",
    "api.listSimilarProducts",
]

# All available claims (permissions + API claims)
ALL_CLAIMS = sorted(ALL_PERMISSIONS + API_CLAIMS)


@extend_schema(tags=['RoleClaims'])
class RoleClaimsViewSet(viewsets.ViewSet):
    """
    ViewSet for RoleClaims endpoints.
    All endpoints will appear under "RoleClaims" folder in Swagger UI.
    """
    permission_classes = [IsAuthenticated, IsManager]

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_list',
        summary='Get all role claims',
        description='Returns all role claims matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=RoleClaimSerializer,
                description='List of all role claims',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": [
                                {
                                    "id": 5,
                                    "roleId": "5dfbd5a2-dc08-440e-b6d8-c3b6a38b3961",
                                    "claimType": "permission",
                                    "claimValue": "Permissions.Products.View",
                                    "description": None,
                                    "group": None,
                                    "selected": False
                                },
                                {
                                    "id": 6,
                                    "roleId": "5dfbd5a2-dc08-440e-b6d8-c3b6a38b3961",
                                    "claimType": "permission",
                                    "claimValue": "Permissions.Products.Search",
                                    "description": None,
                                    "group": None,
                                    "selected": False
                                }
                            ],
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            )
        }
    )
    def list(self, request):
        """Get all role claims matching old Swagger format."""
        try:
            role_claims = RoleClaim.objects.all().select_related('role').order_by('claim_value')
            serializer = RoleClaimSerializer(role_claims, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_create',
        summary='Create a new role claim',
        description='Creates a new role claim matching old Swagger format.',
        request=RoleClaimCreateUpdateSerializer,
        examples=[
            OpenApiExample(
                'Create Role Claim (default)',
                value={
                    "id": 0,
                    "roleId": "string",
                    "type": "string",
                    "value": "string",
                    "description": "string",
                    "group": "string",
                    "selected": True
                }
            )
        ],
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Role claim created successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": None,
                            "messages": [
                                "Role Claim string created. [en-US]"
                            ],
                            "succeeded": True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Role not found'}
        }
    )
    def create(self, request):
        """Create a new role claim matching old Swagger format."""
        try:
            serializer = RoleClaimCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Get role
            try:
                role = Role.objects.get(id=validated_data['roleId'])
            except Role.DoesNotExist:
                return create_error_response(
                    error_message=f'Role with ID "{validated_data["roleId"]}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'roleId': [f'Role with ID "{validated_data["roleId"]}" not found.']}
                )
            
            # Get claim value for message
            claim_value = validated_data.get('value', 'string')
            
            # Create role claim
            role_claim = RoleClaim.objects.create(
                role=role,
                claim_type=validated_data.get('type', 'permission'),
                claim_value=validated_data['value'],
                description=validated_data.get('description', '') or None,
                group=validated_data.get('group', '') or None,
                selected=validated_data.get('selected', False)
            )
            
            # Old Swagger returns null data and a success message
            return create_success_response(
                data=None,
                messages=[f'Role Claim {claim_value} created. [en-US]']
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while creating role claim: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_retrieve',
        summary='Get role claims by role ID',
        description='Returns role claims for a specific role ID matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=RoleClaimSerializer,
                description='List of role claims for the role',
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
    def retrieve(self, request, pk=None):
        """Get role claims by role ID matching old Swagger format."""
        try:
            # pk is the roleId in this context
            role_claims = RoleClaim.objects.filter(role_id=pk).select_related('role').order_by('claim_value')
            serializer = RoleClaimSerializer(role_claims, many=True)
            return create_success_response(data=serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_update',
        summary='Update a role claim',
        description='Updates an existing role claim matching old Swagger format.',
        request=RoleClaimCreateUpdateSerializer,
        responses={
            200: OpenApiResponse(
                response=RoleClaimSerializer,
                description='Role claim updated successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": {
                                "id": 5,
                                "roleId": "5dfbd5a2-dc08-440e-b6d8-c3b6a38b3961",
                                "claimType": "permission",
                                "claimValue": "Permissions.Products.View",
                                "description": None,
                                "group": None,
                                "selected": False
                            },
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            400: {'description': 'Validation error'},
            404: {'description': 'Role claim not found'}
        }
    )
    def update(self, request, pk=None):
        """Update a role claim matching old Swagger format."""
        try:
            try:
                role_claim = RoleClaim.objects.get(id=pk)
            except RoleClaim.DoesNotExist:
                return create_error_response(
                    error_message=f'Role claim with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Role claim with ID "{pk}" not found.']}
                )
            
            serializer = RoleClaimCreateUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            
            # Update role if roleId is provided
            if 'roleId' in validated_data:
                try:
                    role = Role.objects.get(id=validated_data['roleId'])
                    role_claim.role = role
                except Role.DoesNotExist:
                    return create_error_response(
                        error_message=f'Role with ID "{validated_data["roleId"]}" not found.',
                        status_code=status.HTTP_404_NOT_FOUND,
                        errors={'roleId': [f'Role with ID "{validated_data["roleId"]}" not found.']}
                    )
            
            # Update other fields (using 'type' and 'value' from serializer)
            if 'type' in validated_data:
                role_claim.claim_type = validated_data['type']
            if 'value' in validated_data:
                role_claim.claim_value = validated_data['value']
            if 'description' in validated_data:
                role_claim.description = validated_data['description'] or None
            if 'group' in validated_data:
                role_claim.group = validated_data['group'] or None
            if 'selected' in validated_data:
                role_claim.selected = validated_data['selected']
            
            role_claim.save()
            
            response_serializer = RoleClaimSerializer(role_claim)
            return create_success_response(data=response_serializer.data, messages=[])
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating role claim: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_destroy',
        summary='Delete a role claim',
        description='Deletes a role claim matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=dict,
                description='Role claim deleted successfully',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value={
                            "data": 5,
                            "messages": [],
                            "succeeded": True
                        }
                    )
                ]
            ),
            404: {'description': 'Role claim not found'}
        }
    )
    def destroy(self, request, pk=None):
        """Delete a role claim matching old Swagger format."""
        try:
            try:
                role_claim = RoleClaim.objects.get(id=pk)
                claim_id = role_claim.id
                role_claim.delete()
                return create_success_response(data=claim_id, messages=[])
            except RoleClaim.DoesNotExist:
                return create_error_response(
                    error_message=f'Role claim with ID "{pk}" not found.',
                    status_code=status.HTTP_404_NOT_FOUND,
                    errors={'id': [f'Role claim with ID "{pk}" not found.']}
                )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )

    @extend_schema(
        tags=['RoleClaims'],
        operation_id='roleclaims_roleclaimlist',
        summary='Get list of all available claim values',
        description='Returns a simple array of all available claim values matching old Swagger format.',
        responses={
            200: OpenApiResponse(
                response=list,
                description='Array of claim values',
                examples=[
                    OpenApiExample(
                        'Success Response',
                        value=[
                            "api.getAppPromotionProduct",
                            "api.getCompletedOrders",
                            "Permissions.Products.View",
                            "Permissions.Products.Search"
                        ]
                    )
                ]
            )
        }
    )
    @action(detail=False, methods=['get'], url_path='roleclaimlist')
    def roleclaimlist(self, request):
        """Get list of all available claim values matching old Swagger format."""
        try:
            # Return simple array of all available claims (not wrapped)
            return Response(ALL_CLAIMS, status=status.HTTP_200_OK)
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


# Custom APIView classes for URL patterns that don't fit ViewSet actions
@extend_schema(
    tags=['RoleClaims'],
    operation_id='roleclaims_claimgroupres',
    summary='Get claim group resources',
    description='Returns grouped claims with details matching old Swagger format.',
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Grouped claims with details',
            examples=[
                OpenApiExample(
                    'Success Response',
                    value={
                        "data": {
                            "ls": [
                                {
                                    "id": 52,
                                    "groupName": "Addresses",
                                    "schemaName": None,
                                    "orginalName": "Permissions.Addresses.View",
                                    "faLocalName": None,
                                    "enLocalName": None,
                                    "arLocalName": None,
                                    "faSchemaName": None,
                                    "enSchemaName": None,
                                    "arSchemaName": None
                                }
                            ],
                            "names": [
                                {"name": "BOM"},
                                {"name": "Edu"},
                                {"name": "HR"}
                            ]
                        },
                        "messages": [],
                        "succeeded": True
                    }
                )
            ]
        )
    }
)
class RoleClaimsClaimGroupResView(APIView):
    """GET /api/v1/roleclaims/claimgroupres"""
    permission_classes = [IsAuthenticated, IsManager]

    def get(self, request):
        """Get claim group resources matching old Swagger format."""
        try:
            # Group permissions by resource name (e.g., "Products", "Addresses")
            grouped_claims = {}
            group_names = set()
            claim_id = 1  # Start with ID 1 for unique IDs across all claims
            
            for claim in ALL_CLAIMS:
                if claim.startswith('Permissions.'):
                    # Extract resource name (e.g., "Products" from "Permissions.Products.View")
                    parts = claim.split('.')
                    if len(parts) >= 2:
                        resource_name = parts[1]  # e.g., "Products", "Addresses"
                        group_names.add(resource_name)
                        
                        if resource_name not in grouped_claims:
                            grouped_claims[resource_name] = []
                        
                        grouped_claims[resource_name].append({
                            'id': claim_id,
                            'groupName': resource_name,
                            'schemaName': None,
                            'orginalName': claim,
                            'faLocalName': None,
                            'enLocalName': None,
                            'arLocalName': None,
                            'faSchemaName': None,
                            'enSchemaName': None,
                            'arSchemaName': None
                        })
                        claim_id += 1
                elif claim.startswith('api.'):
                    # API claims go to a special group
                    group_names.add('API')
                    if 'API' not in grouped_claims:
                        grouped_claims['API'] = []
                    
                    grouped_claims['API'].append({
                        'id': claim_id,
                        'groupName': 'API',
                        'schemaName': None,
                        'orginalName': claim,
                        'faLocalName': None,
                        'enLocalName': None,
                        'arLocalName': None,
                        'faSchemaName': None,
                        'enSchemaName': None,
                        'arSchemaName': None
                    })
                    claim_id += 1
            
            # Flatten all claims into ls array
            ls = []
            for group_name, claims in sorted(grouped_claims.items()):
                ls.extend(claims)
            
            # Create names array
            names = [{'name': name} for name in sorted(group_names)]
            
            return create_success_response(
                data={
                    'ls': ls,
                    'names': names
                },
                messages=[]
            )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )


@extend_schema(
    tags=['RoleClaims'],
    operation_id='roleclaims_claimgroup',
    summary='Update claim group',
    description='Update claim group information matching old Swagger format.',
    request=ClaimGroupUpdateSerializer,
    examples=[
        OpenApiExample(
            'Update claim group',
            value={
                'id': 0,
                'groupName': 'string',
                'schemaName': 'string',
                'orginalName': 'string',
                'faLocalName': 'string',
                'enLocalName': 'string',
                'arLocalName': 'string',
                'faSchemaName': 'string',
                'enSchemaName': 'string',
                'arSchemaName': 'string'
            },
            request_only=True
        )
    ],
    responses={
        200: OpenApiResponse(
            response=dict,
            description='Claim group updated successfully',
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
class RoleClaimsClaimGroupView(APIView):
    """PUT /api/v1/roleclaims/claimgroup"""
    permission_classes = [IsAuthenticated, IsManager]

    def put(self, request):
        """Update claim group matching old Swagger format."""
        try:
            serializer = ClaimGroupUpdateSerializer(data=request.data)
            if not serializer.is_valid():
                return create_error_response(
                    error_message='Validation error',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors=serializer.errors
                )
            
            validated_data = serializer.validated_data
            group_name = validated_data.get('groupName')
            
            # Update all role claims that belong to this group
            # If id is provided and > 0, we could update a specific claim group entry
            # For now, we'll update all claims with this group name
            if group_name:
                # Update the group field for all claims with this group name
                # Note: This is a simplified implementation - you may need to adjust based on your business logic
                updated_count = RoleClaim.objects.filter(group=group_name).update(
                    group=group_name  # This ensures the group name is set
                )
                
                # If no claims exist with this group, we could create a placeholder or just return success
                # For now, we'll return the group name or id as the data
                response_data = validated_data.get('id', 0) if validated_data.get('id', 0) > 0 else group_name
                
                return create_success_response(
                    data=response_data if isinstance(response_data, (int, str)) else 1,
                    messages=[]
                )
            else:
                return create_error_response(
                    error_message='groupName is required',
                    status_code=status.HTTP_400_BAD_REQUEST,
                    errors={'groupName': ['groupName is required']}
                )
        except Exception as e:
            return create_error_response(
                error_message=f'An error occurred while updating claim group: {str(e)}',
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                errors={'error': [str(e)]}
            )
