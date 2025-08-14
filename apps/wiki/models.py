from django.db import models
from django.db.models import PositiveIntegerField

from apps.accounts.models import CustomUser
from apps.common.models import IsDeletedModel
from apps.common.utils import unique_slugify


# ПОСТЫ: Категории, Посты

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


# СУЩЕСТВА: Категории, существа, атаки, пассивные особенности

class CreatureCategory(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='creature_category_images/', null=True, blank=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Категория существ'
        verbose_name_plural = 'Категории существ'

    def __str__(self):
        return self.name

CREATURE_SIZE_CHOICES = [
    ('tiny', 'Tiny'),
    ('small', 'Small'),
    ('medium', 'Medium'),
    ('large', 'Large'),
    ('giant', 'Giant'),
]

class Creature(IsDeletedModel):
    name = models.CharField('Название существа', max_length=50, unique=True)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    description = models.TextField('Описание существа', max_length=1000)
    image = models.ImageField(upload_to='wiki/creature_images/', null=True, blank=True)
    category = models.ForeignKey(CreatureCategory, on_delete=models.CASCADE)

    # characteristic fields
    health = models.PositiveIntegerField('Хиты', default=0)
    armor_class = models.PositiveIntegerField('КД', default=0)
    mastery = models.PositiveIntegerField('Бонус мастерства', choices=((i, f'+{i}') for i in range(1, 11)), default=10)
    speed = models.PositiveIntegerField('Скорость', default=0)
    size = models.CharField(choices=CREATURE_SIZE_CHOICES, default='')
    saving_throws = models.CharField('Спасброски', max_length=500, default='')
    skills = models.CharField('Навыки', max_length=500, default='')
    dangerous_level = models.PositiveIntegerField('Опасность', choices=((i,i) for i in range(1,21)), default=0)

    # stats fields
    strength = models.PositiveIntegerField('Сила', choices=((i, i) for i in range(20, 0, -1)), default=10)
    dexterity = models.PositiveIntegerField('Ловкость', choices=((i, i) for i in range(20, 0, -1)), default=10)
    body_condition = models.PositiveIntegerField('Телосложение', choices=((i, i) for i in range(20, 0, -1)), default=10)
    intelligence = models.PositiveIntegerField('Интеллект', choices=((i, i) for i in range(20, 0, -1)), default=10)
    wisdom = models.PositiveIntegerField('Мудрость', choices=((i, i) for i in range(20, 0, -1)), default=10)
    charisma = models.PositiveIntegerField('Харизма', choices=((i, i) for i in range(20, 0, -1)), default=10)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Существо'
        verbose_name_plural = 'Существа'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class CreatureAttack(models.Model):
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='attacks')
    name = models.CharField('Название', max_length=20)
    text = models.TextField('Описание', max_length=200)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Атака существа'
        verbose_name_plural = 'Атаки существ'

    def __str__(self):
        return self.name


class CreaturePassive(models.Model):
    creature = models.ForeignKey(Creature, on_delete=models.CASCADE, related_name='passives')
    name = models.CharField('Название', max_length=30)
    text = models.TextField('Описание', max_length=300)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Особенность существа'
        verbose_name_plural = 'Особенности существ'


    def __str__(self):
        return self.name




# ЗАКЛИНАНИЯ: Категории, заклинания, эффекты


class SpellCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)
    image = models.ImageField(upload_to='wiki/spell_category_images/', null=True, blank=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)

class SpellEffect(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=60, unique=True, null=True, blank=True)
    text = models.TextField(max_length=500)

    class Meta:
        ordering = ('name',)
        verbose_name = 'Эффект заклинания'
        verbose_name_plural = 'Эффекты заклинания'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)


class SpellEffectLink(models.Model):
    spell = models.ForeignKey('Spell', on_delete=models.CASCADE)
    effect = models.ForeignKey(SpellEffect, on_delete=models.PROTECT)
    note = models.TextField(max_length=500, null=True, blank=True)

    class Meta:
        unique_together = ('spell', 'effect')
        ordering = ('id',)

    def save(self, *args, **kwargs):
        self.note = self.effect.text
        super().save(*args, **kwargs)


class Spell(IsDeletedModel):
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', max_length=100, unique=True, null=True, blank=True)
    category = models.ForeignKey(SpellCategory, on_delete=models.CASCADE, related_name='spells')
    description = models.TextField('Описание', max_length=1000)
    image = models.ImageField(upload_to='wiki/spell_images/', null=True, blank=True)
    effects = models.ManyToManyField(SpellEffect, through='SpellEffectLink', related_name='spells', blank=True)

    # Аспекты заклинания
    casting_time = models.CharField('Время накладывания', max_length=100, null=True, blank=True)
    distance = models.CharField('Дистанция', max_length=100, null=True, blank=True, help_text='На себя/10 футов/30 футов')
    duration = models.CharField('Длительность', max_length=100, null=True, blank=True)
    requirements = models.CharField('Требования', max_length=300, default='отсутствуют')
    special_components = models.CharField('Особые компоненты', max_length=300, default='отсутствуют')
    spell_level = models.CharField('Уровень заклинания', max_length=100, choices=(
        ('заговор', 'Заговор'),
        ('1', '1'),
        ('2', '2'),
        ('3', '3'),
        ('4', '4'),
        ('5', '5'),
        ('6', '6'),
    ))

    class Meta:
        ordering = ('name',)
        verbose_name = 'Заклинание'
        verbose_name_plural = 'Заклинания'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = unique_slugify(self, self.name, self.slug)
        super().save(*args, **kwargs)









