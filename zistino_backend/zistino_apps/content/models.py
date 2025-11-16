from django.db import models
import uuid


class Testimonial(models.Model):
    """Testimonial model for customer reviews."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    text = models.TextField()
    image_url = models.CharField(max_length=500, blank=True)
    rate = models.IntegerField(default=0, help_text='Rating from 0 to 5')
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'testimonials'
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering = ['-rate', '-created_at']

    def __str__(self):
        return f"{self.name} ({self.rate})"


class Tag(models.Model):
    """Tag model for product/c content tagging."""
    id = models.AutoField(primary_key=True)
    text = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tags'
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['text']

    def __str__(self):
        return self.text


class MenuLink(models.Model):
    """MenuLink model for navigation menus."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    link_url = models.CharField(max_length=500)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    image_url = models.CharField(max_length=500, blank=True, null=True)
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'menu_links'
        verbose_name = 'Menu Link'
        verbose_name_plural = 'Menu Links'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    """Blog category model."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    image_url = models.CharField(max_length=500, blank=True)
    locale = models.CharField(max_length=10, default='fa')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_categories'
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    """Blog tag model."""
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_tags'
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'
        ordering = ['name']

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    """Blog post model."""
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    content = models.TextField()
    excerpt = models.TextField(blank=True)
    featured_image = models.CharField(max_length=500, blank=True)
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='posts')
    tags = models.ManyToManyField(BlogTag, blank=True, related_name='posts')
    author_name = models.CharField(max_length=255, blank=True)
    is_published = models.BooleanField(default=False)
    published_at = models.DateTimeField(blank=True, null=True)
    views_count = models.IntegerField(default=0)
    locale = models.CharField(max_length=10, default='fa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'blog_posts'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

