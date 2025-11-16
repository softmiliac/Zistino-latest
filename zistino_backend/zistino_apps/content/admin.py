from django.contrib import admin
from .models import Testimonial, Tag, MenuLink, BlogCategory, BlogTag, BlogPost


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'rate', 'locale', 'created_at']
    list_filter = ['locale', 'rate']
    search_fields = ['name', 'text']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'text', 'locale', 'created_at']
    list_filter = ['locale']
    search_fields = ['text', 'description']


@admin.register(MenuLink)
class MenuLinkAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'link_url', 'parent', 'locale', 'created_at']
    list_filter = ['locale']
    search_fields = ['name', 'link_url']


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'is_active', 'locale', 'created_at']
    list_filter = ['locale', 'is_active']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogTag)
class BlogTagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'slug', 'locale', 'created_at']
    list_filter = ['locale']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'category', 'is_published', 'views_count', 'created_at']
    list_filter = ['is_published', 'locale', 'category', 'created_at']
    search_fields = ['title', 'content', 'excerpt', 'author_name']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    raw_id_fields = ['category']

