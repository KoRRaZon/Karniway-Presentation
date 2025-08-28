from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse

from apps.common.models import IsDeletedModel
from apps.common.utils import unique_slugify


class ProductCategory(models.Model):
    name = models.CharField('Категория', max_length=100)
    slug = models.SlugField('URL категории', max_length=100, unique=True, null=False, blank=False)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория товаров'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class ProductTag(models.Model):
    name = models.CharField('Тег', max_length=40)
    slug = models.SlugField('URL тега', max_length=50, unique=True, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег товаров'
        verbose_name_plural = 'Теги товаров'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class Product(IsDeletedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    name = models.CharField('Название товара', max_length=100)
    slug = models.SlugField('URL товара', max_length=100, unique=True, null=False, blank=False)
    category = models.ForeignKey(ProductCategory, on_delete=models.PROTECT, verbose_name='Категория товара')
    tags = models.ManyToManyField(ProductTag, related_name='products', verbose_name='Теги', blank=True, null=True)
    description = models.TextField('Описание', max_length=600)
    quantity = models.PositiveIntegerField('Количество в наличии', default=1)
    price = models.DecimalField('Цена', max_digits=10, decimal_places=2)
    prom_price = models.DecimalField('Акционная цена', max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        constraints = [
            models.CheckConstraint(check=Q(price__gte=0), name='product_price'),
            models.CheckConstraint(check=Q(prom_price__gte=0), name='product_prom_price'),
            models.CheckConstraint(check=Q(quantity__gt=0), name='product_quantity_non_negative'),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('shop:product_detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


def product_image_upload_to(instance, filename):
    return f'shop/products/{instance.product.slug}/{filename}'


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


class ProductVote(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    value = models.SmallIntegerField(choices=[(1, 'up'), (-1, 'down')])

    class Meta:
        ordering = ('pk',)
        verbose_name = 'Оценки товаров'
        verbose_name_plural = 'Оценки товаров'
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_user_vote_for_product'
            )
        ]


class ProductRating(models.Model):
    product = models.OneToOneField(Product, on_delete=models.CASCADE, related_name='rating')
    up_count = models.PositiveIntegerField('Позитивные голоса', default=0)
    down_count = models.PositiveIntegerField('Негативные голоса', default=0)
    rating = models.DecimalField('Рейтинг (1.0-5.0)', max_digits=2, decimal_places=1, default=Decimal('1.0'))
    class Meta:
        ordering = ('rating',)
        verbose_name = 'Рейтинг товаров'
        verbose_name_plural = 'Рейтинги товаров'

    def __str__(self):
        return f"{self.product}'s rating: {self.rating}"

    def recompute(self, save=True):
        total = self.up_count + self.down_count
        if total == 0:
            stars = Decimal('0.0')
        else:
            p = Decimal(self.up_count) / Decimal(total)
            stars = Decimal('1.0') + Decimal('4.0') * p

        # Округление до одной цифры после запятой по "обычным" правилам
        stars = stars.quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)

        # гарантирует диапазон 1.0 - 5.0
        if stars < Decimal('1.0'):
            stars = Decimal('1.0')
        elif stars > Decimal('5.0'):
            stars = Decimal('5.0')

        self.rating = stars
        if save:
            self.save(update_fields=['rating'])
        return self


class ProductReview(IsDeletedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='product_reviews')
    text = models.TextField('Отзыв', max_length=800)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = 'Отзыв на товар'
        verbose_name_plural = 'Отзывы на товары'
        indexes = [
            models.Index(fields=['product', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['product', 'user'],
                name='unique_user_review_per_product',
            )
        ]

    def __str__(self):
        user = self.user and getattr(self.user, 'full_name', None) or 'Гость'
        return f"Отзыв {user} для {self.product}"





