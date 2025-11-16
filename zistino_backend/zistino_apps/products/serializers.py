from rest_framework import serializers
from .models import Category, Product, Color, Price, Specification, Warranty, FAQ, ProductSection, Problem, ProductCode
from zistino_apps.notifications.models import Comment
import requests
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.files import File
from django.conf import settings
from io import BytesIO
import mimetypes
import os
from urllib.parse import urlparse


class URLImageField(serializers.ImageField):
    """
    Custom ImageField that accepts:
    1. File uploads (multipart/form-data)
    2. HTTP/HTTPS URLs (downloads the image)
    3. Local file paths (relative to MEDIA_ROOT or absolute paths)
    """
    def to_internal_value(self, data):
        # If it's already a file, use parent behavior
        if hasattr(data, 'read'):
            return super().to_internal_value(data)
        
        # If it's a string, check if it's a URL or local path
        if isinstance(data, str):
            # Handle HTTP/HTTPS URLs
            if data.startswith('http://') or data.startswith('https://'):
                try:
                    # Download the image
                    response = requests.get(data, timeout=10, stream=True)
                    response.raise_for_status()
                    
                    # Get content type
                    content_type = response.headers.get('content-type', 'image/jpeg')
                    if not content_type.startswith('image/'):
                        raise serializers.ValidationError('URL does not point to an image file.')
                    
                    # Get file extension from URL or content type
                    parsed_url = urlparse(data)
                    path = parsed_url.path
                    ext = mimetypes.guess_extension(content_type) or '.jpg'
                    
                    # Create a file-like object
                    image_data = BytesIO(response.content)
                    image_file = InMemoryUploadedFile(
                        image_data,
                        None,
                        f'image{ext}',
                        content_type,
                        len(response.content),
                        None
                    )
                    
                    # Use parent behavior with the downloaded file
                    return super().to_internal_value(image_file)
                except requests.RequestException as e:
                    raise serializers.ValidationError(f'Failed to download image from URL: {str(e)}')
                except Exception as e:
                    raise serializers.ValidationError(f'Error processing image URL: {str(e)}')
            
            # Handle local file paths
            else:
                try:
                    # Try as absolute path first
                    if os.path.isabs(data):
                        file_path = data
                    else:
                        # Try relative to MEDIA_ROOT
                        if hasattr(settings, 'MEDIA_ROOT') and settings.MEDIA_ROOT:
                            # Remove 'media/' prefix if present (it's already in MEDIA_ROOT)
                            path = data.replace('media/', '').lstrip('/')
                            file_path = os.path.join(settings.MEDIA_ROOT, path)
                        else:
                            # Fallback: try relative to project root
                            from django.conf import settings as django_settings
                            base_dir = getattr(django_settings, 'BASE_DIR', None)
                            if base_dir:
                                file_path = os.path.join(base_dir, data)
                            else:
                                file_path = data
                    
                    # Check if file exists
                    if not os.path.exists(file_path):
                        raise serializers.ValidationError(f'Image file not found: {data}')
                    
                    # Check if it's a file (not a directory)
                    if not os.path.isfile(file_path):
                        raise serializers.ValidationError(f'Path is not a file: {data}')
                    
                    # Open the file
                    with open(file_path, 'rb') as f:
                        # Get file name and extension
                        file_name = os.path.basename(file_path)
                        ext = os.path.splitext(file_name)[1] or '.jpg'
                        
                        # Guess content type
                        content_type, _ = mimetypes.guess_type(file_path)
                        if not content_type or not content_type.startswith('image/'):
                            content_type = 'image/jpeg'
                        
                        # Read file content
                        file_content = f.read()
                        
                        # Create a file-like object
                        image_data = BytesIO(file_content)
                        image_file = InMemoryUploadedFile(
                            image_data,
                            None,
                            file_name,
                            content_type,
                            len(file_content),
                            None
                        )
                        
                        # Use parent behavior with the file
                        return super().to_internal_value(image_file)
                except FileNotFoundError:
                    raise serializers.ValidationError(f'Image file not found: {data}')
                except PermissionError:
                    raise serializers.ValidationError(f'Permission denied accessing file: {data}')
                except Exception as e:
                    raise serializers.ValidationError(f'Error processing image file: {str(e)}')
        
        # If it's empty or None, allow it (optional field)
        if not data or data == '':
            return None
        
        # Otherwise, use parent behavior
        return super().to_internal_value(data)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    image = URLImageField(required=False, allow_null=True)

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'category', 'category_name',
            'price_per_unit', 'unit', 'image', 'is_active', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'name', 'code', 'locale']
        read_only_fields = ['id']


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = ['id', 'product', 'price', 'locale']
        read_only_fields = ['id']


class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ['id', 'product', 'size', 'level']
        read_only_fields = ['id']


class WarrantySerializer(serializers.ModelSerializer):
    class Meta:
        model = Warranty
        fields = ['id', 'product', 'name', 'image_url', 'description', 'locale']
        read_only_fields = ['id']


class FAQSerializer(serializers.ModelSerializer):
    class Meta:
        model = FAQ
        fields = ['id', 'question', 'answer', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProductCommentSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_full_name = serializers.SerializerMethodField()
    user_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'product', 'user_id', 'user_full_name', 'user_image_url', 'text', 'rate', 'is_accepted', 'created_on']
        read_only_fields = ['id', 'user_id', 'user_full_name', 'user_image_url', 'created_on']
    
    def get_user_full_name(self, obj):
        """Get user's full name"""
        if obj.user:
            name_parts = [obj.user.first_name, obj.user.last_name]
            return ' '.join(filter(None, name_parts)) or obj.user.username or obj.user.phone_number
        return None
    
    def get_user_image_url(self, obj):
        """Get user's profile image URL"""
        if obj.user and hasattr(obj.user, 'image_url') and obj.user.image_url:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.user.image_url.url)
            return str(obj.user.image_url)
        return None


class ProductIdRequestSerializer(serializers.Serializer):
    """Explicit request schema for comments-by-product endpoint (docs show productId)."""
    productId = serializers.UUIDField(required=True)


class ProductSearchRequestSerializer(serializers.Serializer):
    """Request schema for products client/search and admin search endpoints."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")
    orderBy = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        allow_null=True,
        help_text="List of field names to order by (e.g., ['name'], ['-created_at'])"
    )


class FAQSearchRequestSerializer(serializers.Serializer):
    """Request serializer for FAQ search (admin endpoint)."""
    pass  # Empty request body - panel sends empty object


class WarrantySearchRequestSerializer(serializers.Serializer):
    """Request serializer for warranty search (admin endpoint)."""
    pass  # Empty request body - panel sends empty object


class SpecificationSearchRequestSerializer(serializers.Serializer):
    """Request serializer for specification search (admin endpoint)."""
    pass  # Empty request body - panel sends empty object


class ProductSectionSearchRequestSerializer(serializers.Serializer):
    """Request serializer for product section search (admin endpoint)."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)
    keyword = serializers.CharField(required=False, allow_blank=True, default="")


class ProblemSerializer(serializers.ModelSerializer):
    """Serializer for Problem model."""
    parentId = serializers.IntegerField(source='parent_id', allow_null=True, required=False, read_only=True)
    iconUrl = serializers.CharField(source='icon_url', allow_blank=True, required=False)
    productId = serializers.CharField(write_only=True, required=True, help_text='Product UUID')
    productIdReadOnly = serializers.CharField(source='product_id', read_only=True)
    repairDuration = serializers.IntegerField(source='repair_duration')
    createdAt = serializers.DateTimeField(source='created_at', read_only=True)

    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'description', 'iconUrl', 'parentId', 'repairDuration',
            'price', 'productId', 'productIdReadOnly', 'priority', 'locale', 'createdAt'
        ]
        read_only_fields = ['id', 'createdAt', 'productIdReadOnly']

    def to_representation(self, instance):
        """Return productId in response instead of productIdReadOnly."""
        data = super().to_representation(instance)
        # Rename productIdReadOnly to productId for response
        if 'productIdReadOnly' in data:
            data['productId'] = data.pop('productIdReadOnly')
        return data

    def create(self, validated_data):
        """Handle productId assignment during creation."""
        product_id = validated_data.pop('productId', None)
        if not product_id:
            raise serializers.ValidationError({'productId': 'This field is required'})
        
        from .models import Product
        try:
            product = Product.objects.get(id=product_id)
            validated_data['product'] = product
        except Product.DoesNotExist:
            raise serializers.ValidationError({'productId': 'Product not found'})
        except Exception as e:
            raise serializers.ValidationError({'productId': f'Invalid product ID: {str(e)}'})
        
        return super().create(validated_data)

    def update(self, instance, validated_data):
        """Handle productId assignment during update."""
        product_id = validated_data.pop('productId', None)
        if product_id:
            from .models import Product
            try:
                product = Product.objects.get(id=product_id)
                validated_data['product'] = product
            except Product.DoesNotExist:
                raise serializers.ValidationError({'productId': 'Product not found'})
            except Exception as e:
                raise serializers.ValidationError({'productId': f'Invalid product ID: {str(e)}'})
        
        return super().update(instance, validated_data)


class ProblemSearchRequestSerializer(serializers.Serializer):
    """Request serializer for problem search."""
    pageNumber = serializers.IntegerField(required=False, min_value=1, default=1)
    pageSize = serializers.IntegerField(required=False, min_value=1, default=20)


class ProductSectionSerializer(serializers.ModelSerializer):
    """CMS ProductSection serializer - matches ProductSectionModel structure."""
    productId = serializers.CharField(source='product.id', read_only=True, allow_null=True)
    groupName = serializers.CharField(source='group_name', read_only=True)
    imagePath = serializers.CharField(source='image_path', read_only=True)
    linkUrl = serializers.CharField(source='link_url', read_only=True)
    setting = serializers.SerializerMethodField()
    extraValues = serializers.SerializerMethodField()

    class Meta:
        model = ProductSection
        fields = [
            'id', 'name', 'page', 'groupName', 'version', 'productId',
            'imagePath', 'setting', 'description', 'linkUrl', 'locale', 'extraValues'
        ]
        read_only_fields = ['id']

    def get_setting(self, obj):
        """Return setting as dict matching Flutter structure."""
        return {
            'type': obj.setting_type,
            'expireDate': obj.expire_date.isoformat() if obj.expire_date else None
        }

    def get_extraValues(self, obj):
        """Return product data if product is linked."""
        if obj.product:
            return ProductSerializer(obj.product).data
        return None


class ProductCodeSerializer(serializers.ModelSerializer):
    productName = serializers.CharField(source='product.name', read_only=True)
    class Meta:
        model = ProductCode
        fields = ['id', 'product', 'productName', 'code', 'status', 'assigned_to', 'assigned_at', 'used_at', 'created_at']
        read_only_fields = ['id', 'assigned_to', 'assigned_at', 'used_at', 'created_at']


class ProductCodeBulkImportSerializer(serializers.Serializer):
    codes = serializers.ListField(child=serializers.CharField(max_length=255), allow_empty=False)
