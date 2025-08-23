from urllib.parse import urljoin
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html
from django.templatetags.static import static

from apps.shop.models import Product, ProductCategory, ProductImage


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 0
    min_num = 0
    can_delete = True
    show_change_link = True
    fields = ('image', 'is_main', 'position')


def media_url(path:str) -> str:
    """
    Формирует абсолютный URL внутри MEDIA_URL.
    Пример: media_url('images/shop/default.jpg') -> '/media/images/shop/default.jpg'
    """
    return urljoin(settings.MEDIA_URL, path.lstrip('/'))

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('preview_image', 'name', 'slug', 'category', 'images_counter', 'quantity', 'price',)
    list_filter = ('category',)
    search_fields = ('name', 'description', 'category__name',)
    autocomplete_fields = ('category',)
    readonly_fields = ('created_at', 'updated_at',)

    fieldsets = (
        ('Основное', {
            'fields': (('name', 'slug', 'category'), ('quantity', 'price', 'prom_price'))
        }),
        ('Детально', {
            'fields': ('description',)
        }),
        ('Дополнительно', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        }),
    )

    inlines = [ProductImageInline]

    def delete_model(self, request, obj):
        obj.hard_delete()

    def get_queryset(self, request):
        return self.model.objects.unfiltered().select_related('category').prefetch_related('images')

    def preview_image(self, obj):
        image = obj.images.filter(is_main=True).first()
        url = getattr(getattr(image, 'image', None), 'url', None)
        if not url:
            url = media_url('shop/default.jpg')

        return format_html(
            '<img src="{}" style="height:60px;width:auto;border-radius:6px;object-fit:cover;"/>', url
        )
    preview_image.short_description = 'Превью'

    def images_counter(self, obj):
        return obj.images.count()


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('image', 'is_main', 'position',)
    list_select_related = ('product',)
    search_fields = ('product__name', 'product__description',)
    autocomplete_fields = ('product',)

