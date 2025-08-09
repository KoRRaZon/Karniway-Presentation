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


CREATURE_SIZE_CHOICES = [
    ('tiny', 'Tiny'),
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
    ('giant', 'Giant'),
]

class Creature(IsDeletedModel):
    name = models.CharField('Название существа', max_length=50, unique=True)
    description = models.TextField('Описание существа', max_length=1000)
    image = models.ImageField(upload_to='wiki/creature_images/', null=True, blank=True)
    category = models.ForeignKey(CreatureCategory, on_delete=models.CASCADE)

    # characteristic fields
    health = models.PositiveIntegerField('Хиты', default=0)
    armor_class = models.PositiveIntegerField('КД', default=0)
    speed = models.PositiveIntegerField('Скорость')
    size = models.CharField(choices=CREATURE_SIZE_CHOICES)
    saving_throws = models.CharField('Спасброски', max_length=500)
    skills = models.CharField('Навыки', max_length=500)
    dangerous_level = models.PositiveIntegerField('Опасность', choices=((i,i) for i in range(1,21)))

    # stats fields
    mastery = models.PositiveIntegerField('Бонус мастерства', choices=((i, f'+{i}') for i in range(1,11)))
    strength = models.PositiveIntegerField('Сила', choices=((i, i) for i in range(20, 0, -1)))
    dexterity = models.PositiveIntegerField('Ловкость', choices=((i, i) for i in range(20, 0, -1)))
    body_condition = models.PositiveIntegerField('Телосложение', choices=((i, i) for i in range(20, 0, -1)))
    intelligence = models.PositiveIntegerField('Интеллект', choices=((i, i) for i in range(20, 0, -1)))
    wisdom = models.PositiveIntegerField('Мудрость', choices=((i, i) for i in range(20, 0, -1)))
    charisma = models.PositiveIntegerField('Харизма', choices=((i, i) for i in range(20, 0, -1)))

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







