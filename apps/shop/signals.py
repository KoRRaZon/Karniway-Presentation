import os
import shutil
from pathlib import Path

from django.conf import settings
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from apps.shop.models import ProductImage, Product


def _delete_file(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass
    
# удаление изображения из media в случае удаления объекта
@receiver(post_delete, sender=ProductImage, dispatch_uid='shop.productimage.delete_image_on_delete')
def delete_image_on_delete(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        _delete_file(instance.image.path)
            

# удаление изображения в случае замены другим через редактирование существа
@receiver(pre_save, sender=ProductImage, dispatch_uid='shop.productimage.delete_old_image_on_change')
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.image:
        return
    try:
        old = ProductImage.objects.get(pk=instance.pk)
    except ProductImage.DoesNotExist:
        return

    if old.image and old.image.path and old.image != instance.image:
        _delete_file(old.image.path)


# удаление media-directory, при удалении товара
@receiver(post_delete, sender=Product, dispatch_uid='shop.product.delete>product_dir_on_delete')
def delete_product_dir_on_delete(sender, instance, **kwargs):
    base = Path(settings.MEDIA_ROOT) / 'shop' / 'products' / instance.slug
    shutil.rmtree(str(base), ignore_errors=True)