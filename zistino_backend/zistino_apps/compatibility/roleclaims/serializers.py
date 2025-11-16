"""
Serializers for RoleClaims endpoints matching old Swagger format.
"""
from rest_framework import serializers
from .models import RoleClaim


class RoleClaimSerializer(serializers.ModelSerializer):
    """Serializer for RoleClaim matching old Swagger format."""
    roleId = serializers.UUIDField(source='role.id', read_only=True)
    claimType = serializers.CharField(source='claim_type', read_only=True)
    claimValue = serializers.CharField(source='claim_value', read_only=True)
    
    class Meta:
        model = RoleClaim
        fields = ['id', 'roleId', 'claimType', 'claimValue', 'description', 'group', 'selected']
        read_only_fields = ['id']


class RoleClaimCreateUpdateSerializer(serializers.Serializer):
    """Request serializer for creating/updating role claim matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Role claim ID (0 for new, existing ID for update)')
    roleId = serializers.UUIDField(required=True, help_text='Role ID (UUID)')
    type = serializers.CharField(required=False, default='permission', help_text='Type of claim')
    value = serializers.CharField(required=True, max_length=255, help_text='Claim value')
    description = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='', help_text='Claim description')
    group = serializers.CharField(required=False, allow_blank=True, allow_null=True, default='', help_text='Claim group name')
    selected = serializers.BooleanField(required=False, default=False, help_text='Whether this claim is selected')


class ClaimGroupSerializer(serializers.Serializer):
    """Serializer for claim group operations."""
    groupName = serializers.CharField(required=True, max_length=255)
    claims = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text='List of claims in this group'
    )


class ClaimGroupUpdateSerializer(serializers.Serializer):
    """Serializer for updating claim group matching old Swagger format."""
    id = serializers.IntegerField(required=False, default=0, help_text='Claim group ID (0 for new, existing ID for update)')
    groupName = serializers.CharField(required=True, max_length=255, help_text='Group name')
    schemaName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Schema name')
    orginalName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Original name')
    faLocalName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Farsi local name')
    enLocalName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='English local name')
    arLocalName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Arabic local name')
    faSchemaName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Farsi schema name')
    enSchemaName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='English schema name')
    arSchemaName = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Arabic schema name')