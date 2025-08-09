from django.db import models

from apps.accounts.models import CustomUser
from apps.common.models import IsDeletedModel
from apps.common.utils import unique_slugify


class PostCategory(models.Model):
    name = models.CharField(max_length=50)


class Post(IsDeletedModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    text = models.TextField()
    image = models.ImageField(upload_to='post_images/', null=True, blank=True)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.FloatField(default=0, editable=False)

    class Meta:
        ordering = ('-title',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.title, self.slug)
        super().save(*args, **kwargs)


class CreatureCategory(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='creature_category_images/', null=True, blank=True)


class Creature(IsDeletedModel):
    name = models.CharField(max_length=50)
    description = models.TextField()
    category = models.ForeignKey(CreatureCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class CreatureAttack(models.Model):
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='attacks')
    name = models.CharField('Название', max_length=20)
    text = models.TextField('Описание', max_length=200)

    def __str__(self):
        return self.name

class CreaturePassive(models.Model):
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='passives')
    name = models.CharField('Название', max_length=30)
    text = models.TextField('Описание', max_length=300)

    def __str__(self):
        return self.name







