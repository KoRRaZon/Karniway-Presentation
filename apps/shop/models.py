from django.db import models

from apps.common.models import IsDeletedModel
from apps.common.utils import unique_slugify


class ProductCategory(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField('URL категории', max_length=100, unique=True, null=False, blank=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class ProductTags(models.Model):
    name = models.CharField('Тег', max_length=40)
    slug = models.SlugField('URL тега', max_length=50, unique=True, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег товаров'
        verbose_name_plural = 'Теги товаров'

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class Product(IsDeletedModel):
    name = models.CharField('Название товара', max_length=100)
    slug = models.SlugField('URL товара', max_length=100, unique=True, null=False, blank=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, verbose_name='Категория товара')
    description = models.TextField('Описание', max_length=600)
    quantity = models.PositiveIntegerField('Количество в наличии', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    prom_price = models.DecimalField('Акционная цена', max_digits=10, decimal_places=2, null=True, blank=True)


def product_image_upload_to(instance, filename):
    return f'shop/products/{instance.slug}/{filename}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=product_image_upload_to)
    is_main = models.BooleanField('Обложка', default=False)
    position = models.PositiveSmallIntegerField('Порядок', default=1)

    class Meta:
        ordering = ('position', 'id')
        constraints = [
            # у одного товара только одна обложка
            models.UniqueConstraint(
                fields=['product'],
                condition=models.Q(is_main=True),
                name='unique_main_image_per_product',
            ),
            # уникальный порядок в пределах товара (для удобства)
            models.UniqueConstraint(
                fields=['product', 'position'],
                name='unique_image_position_per_product',
            ),
        ]

    def __str__(self):
        return f"{self.product}'s image {self.position}"









