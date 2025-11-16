from django.contrib import admin
from .models import Notification, Comment


# Temporarily hide notifications from admin by not registering
# @admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for notifications"""
    list_display = ('title', 'user', 'notification_type', 'is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__phone_number', 'user__username')
    readonly_fields = ('id', 'created_at')
    raw_id_fields = ('user',)
    ordering = ('-created_at',)
    list_editable = ('is_read',)
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'title', 'message', 'notification_type', 'is_read')
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


class CommentChildrenInline(admin.TabularInline):
    """Inline for child comments"""
    model = Comment
    fk_name = 'parent'
    extra = 0
    readonly_fields = ('id', 'user', 'product', 'rate', 'created_on')
    fields = ('user', 'text', 'rate', 'is_accepted', 'created_on')
    can_delete = False


# Temporarily hide comments from admin by not registering
# @admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """Admin for product comments"""
    list_display = ('id', 'user', 'product', 'parent', 'rate', 'is_accepted', 'created_on')
    list_filter = ('is_accepted', 'rate', 'created_on')
    search_fields = ('text', 'user__phone_number', 'user__username', 
                     'product__name', 'user_full_name')
    readonly_fields = ('id', 'created_on')
    raw_id_fields = ('user', 'product', 'parent')
    ordering = ('-created_on',)
    inlines = [CommentChildrenInline]
    list_editable = ('is_accepted',)
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('user', 'product', 'parent')
        }),
        ('Content', {
            'fields': ('rate', 'text', 'is_accepted')
        }),
        ('Display Information', {
            'fields': ('user_full_name', 'user_image_url', 'product_image')
        }),
        ('Timestamps', {
            'fields': ('created_on',)
        }),
    )

