"""
Serializers for Testimonials endpoints matching old Swagger format.
"""
from rest_framework import serializers
from zistino_apps.content.models import Testimonial


class TestimonialCreateRequestSerializer(serializers.Serializer):
    """Request serializer for creating testimonial matching old Swagger format."""
    name = serializers.CharField(required=True, max_length=255, help_text='Testimonial name')
    text = serializers.CharField(required=True, help_text='Testimonial text')
    imageUrl = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=500, help_text='Image URL')
    thumbnail = serializers.CharField(required=False, allow_blank=True, allow_null=True, max_length=500, help_text='Thumbnail URL')
    rate = serializers.IntegerField(required=False, default=0, min_value=0, max_value=5, help_text='Rating from 0 to 5')
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Product ID (UUID)')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Exam ID')
    jobId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Job ID')
    blogId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Blog ID')
    locale = serializers.CharField(required=False, allow_blank=True, default='fa', max_length=10, help_text='Locale')


class AdvancedSearchSerializer(serializers.Serializer):
    """Advanced search serializer."""
    fields = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Fields to search in'
    )
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    groupBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Group by fields'
    )


class TestimonialSearchRequestSerializer(serializers.Serializer):
    """Request serializer for searching testimonials matching old Swagger format."""
    advancedSearch = AdvancedSearchSerializer(required=False, allow_null=True, help_text='Advanced search options')
    keyword = serializers.CharField(required=False, allow_blank=True, default='', help_text='Search keyword')
    pageNumber = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page number (0 means 1)')
    pageSize = serializers.IntegerField(required=False, min_value=0, default=0, help_text='Page size (0 means default)')
    orderBy = serializers.ListField(
        child=serializers.CharField(allow_blank=True),
        required=False,
        allow_empty=True,
        default=list,
        help_text='Order by fields'
    )
    productId = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Filter by product ID')
    examId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by exam ID')
    jobId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by job ID')
    blogId = serializers.IntegerField(required=False, allow_null=True, default=0, help_text='Filter by blog ID')
    locale = serializers.CharField(required=False, allow_blank=True, allow_null=True, help_text='Filter by locale')


class TestimonialDetailSerializer(serializers.ModelSerializer):
    """Serializer for testimonial details matching old Swagger format."""
    imageUrl = serializers.CharField(source='image_url', read_only=True, allow_null=True)
    thumbnail = serializers.CharField(source='image_url', read_only=True, allow_null=True)  # Use image_url as thumbnail
    productId = serializers.SerializerMethodField()
    examId = serializers.SerializerMethodField()
    jobId = serializers.SerializerMethodField()
    blogId = serializers.SerializerMethodField()
    
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'text', 'imageUrl', 'thumbnail', 'rate', 'productId', 'examId', 'jobId', 'blogId', 'locale']
        read_only_fields = ['id']
    
    def get_productId(self, obj):
        """Return None as productId is not in the model."""
        return None
    
    def get_examId(self, obj):
        """Return None as examId is not in the model."""
        return None
    
    def get_jobId(self, obj):
        """Return None as jobId is not in the model."""
        return None
    
    def get_blogId(self, obj):
        """Return None as blogId is not in the model."""
        return None
