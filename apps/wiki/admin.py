from django.contrib import admin

from apps.wiki.models import Post


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass
