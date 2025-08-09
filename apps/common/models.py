import uuid
from datetime import timezone

from django.db import models

from apps.common.managers import GetOrNoneManager, IsDeletedManager


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = GetOrNoneManager()

    class Meta:
        abstract = True


class IsDeletedModel(BaseModel):
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = IsDeletedManager()

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def delete(self, *args, **kwargs):
        # мягкое удаление
        self.is_deleted=True
        self.deleted_at=timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def hard_delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
