import os
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

from .models import Creature


# Creature: предотвращение накопления ненужных / устаревших изображений


def _delete_file(path):
    try:
        if path and os.path.exists(path):
            os.remove(path)
    except OSError:
        pass

# удаление изображения после удаления существа
@receiver(post_delete, sender=Creature, dispatch_uid='wiki.creature.delete_image_on_delete')
def delete_image_on_delete(sender, instance, **kwargs):
    if instance.image and instance.image.path:
        _delete_file(instance.image.path)


# удаление изображения в случае замены другим через редактирование существа
@receiver(pre_save, sender=Creature, dispatch_uid='wiki.creature.delete_old_image_on_change')
def delete_old_image_on_change(sender, instance, **kwargs):
    if not instance.image:
        return
    try:
        old = Creature.objects.get(pk=instance.pk)
    except Creature.DoesNotExist:
        return

    # удаление старого файла в случае изменения пути
    if old.image and old.image.path and old.image != instance.image:
        _delete_file(old.image.path)










