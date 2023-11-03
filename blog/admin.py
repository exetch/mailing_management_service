from django.contrib import admin

from blog.models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'slug', 'is_published', 'views')
    list_filter = ('is_published', 'views')
    search_fields = ('id', 'title', 'slug')
