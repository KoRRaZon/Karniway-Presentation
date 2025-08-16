from django.contrib import admin
from django.contrib.admin.widgets import AdminTextareaWidget
from django.db import models
from django import forms
from django.db.models import Count
from django.forms import Textarea
from django.utils.safestring import mark_safe

from apps.wiki.models import Post, Creature, CreatureAttack, CreaturePassive, CreatureCategory, Spell, SpellEffect, \
    SpellCategory, SpellEffectLink, PostCategory, News


@admin.register(PostCategory)
class PostCategoryForm(admin.ModelAdmin):
    list_display = ("name", "slug")

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'text', 'created_at')
    search_fields = ('title', 'text')
    list_filter = ('author', 'is_deleted')

    fieldsets = (
        ('Основное', {
            'fields': (('title', 'slug'), 'author', 'image')
        }),
        ('Текст статьи', {
            'fields': ('text',)
        }),
        ('Дополнительно', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        })
    )


    readonly_fields = ('created_at', 'updated_at', 'is_deleted', 'deleted_at')

    def get_queryset(self, request):
        return self.model.objects.unfiltered().select_related("category")



@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'created_at')
    search_fields = ('title', 'text')
    readonly_fields = ('created_at', 'updated_at', 'is_deleted', 'deleted_at')

    fieldsets = (
        ('Основное', {
            'fields': (('title', 'slug'),)
        }),
        ('Текст статьи', {
            'fields': ('text',)
        }),
        ('Дополнительно', {
            'classes': ('collapse',),
            'fields': ('created_at', 'updated_at', 'is_deleted', 'deleted_at')
        })
    )

    def get_queryset(self, request):
        return self.model.objects.unfiltered()



# CREATURE
@admin.register(CreatureCategory)
class CreatureCategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)

# Виджет для компактности записи
CompactTextarea = lambda rows=2: forms.Textarea(attrs={'rows': rows, 'style': 'width:100%'})


#TabularInline для атак с небольшим текстовым наполнением
class CreatureAttackInline(admin.TabularInline):
    model = CreatureAttack
    extra = 0  # не показывать пустые формы заранее
    min_num = 0  # минимальное число строк
    can_delete = True
    show_change_link = True  # иконка-ссылка на отдельную страницу атаки
    fields = ("name", "text")  # порядок и состав полей в строке
    formfield_overrides = {
        models.TextField: {"widget": CompactTextarea(rows=2)},
    }

# StackedInline для длинных описаний пассивных особенностей
class CreaturePassiveInline(admin.StackedInline):
    model = CreaturePassive
    extra = 0
    min_num = 0
    can_delete = True
    show_change_link = True
    fields = ("name", "text")
    formfield_overrides = {
        models.TextField: {"widget": CompactTextarea(rows=2)},
    }

@admin.register(Creature)
class CreatureAdmin(admin.ModelAdmin):
    # Отображение колонок в списке существ
    list_display = (
        "preview_image", "name", "image", "category", "dangerous_level", "attacks_counter", "passives_counter", "is_deleted"
    )
    list_select_related = ("category",) # предотвращение N+1 по CreatureCategory
    search_fields = ("name", "description",)
    list_filter = ("category", "size", "dangerous_level",)
    ordering = ("name",)

    # Удобный выбор категории через поиск (AJAX). Для этого у CreatureCategory должен быть search_fields.
    autocomplete_fields = ("category",)

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основное", {
            "fields": (("name", "slug", "category"), "description", "image"),
        }),
        ("Характеристики", {
            "fields": (("health", "armor_class", "speed", "size"),
                     ("mastery", "saving_throws", "skills"), "dangerous_level", ),
        }),
        ("Статы", {
            "fields": (("strength", "dexterity", "body_condition"),
                       ("intelligence", "wisdom", "charisma")),
        }),
        ("Дополнительно", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at", "is_deleted", "deleted_at"),
        }),
    )

    inlines = [CreatureAttackInline, CreaturePassiveInline]

    save_on_top = True

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:30px;border-radius:8px;" />')
        return "-"
    preview_image.short_description = "Превью"

    # Кверисет для подсчёта связанных объектов без доп. запроса, а также отображения всех объектов, даже is_deleted=True
    def get_queryset(self, request):
        return (self.model.objects.unfiltered().annotate(
            _attacks_count=Count("attacks"),
            _passives_count=Count("passives"),
        ))

    @admin.display(description="Атак")
    def attacks_counter(self, obj):
        # использует аннотацию из get_queryset
        return getattr(obj, "_attacks_count", obj.attacks.count())

    @admin.display(description="Особенностей")
    def passives_counter(self, obj):
        # использует аннотацию из get_queryset
        return getattr(obj, "_passives_count", obj.passives.count())


@admin.register(CreatureAttack)
class CreatureAttackAdmin(admin.ModelAdmin):
    list_display = ("name", "creature", "text")
    list_select_related = ("creature",)
    search_fields = ("name", "text", "creature__name")
    autocomplete_fields = ("creature",)

@admin.register(CreaturePassive)
class CreaturePassiveAdmin(admin.ModelAdmin):
    list_display = ("name", "creature", "text")
    list_select_related = ("creature",)
    search_fields = ("name", "text", "creature__name")
    autocomplete_fields = ("creature",)



# ЗАКЛИНАНИЯ


class SpellEffectInline(admin.TabularInline):
    model = SpellEffectLink
    extra = 0
    min_num = 0
    autocomplete_fields = ("effect",)
    fields = ("effect", "note",)
    can_delete = True
    ordering = ("pk",)


@admin.register(Spell)
class SpellAdmin(admin.ModelAdmin):
    list_display = ("preview_image", "name", "category", "spell_level")
    list_select_related = ("category",)
    search_fields = ("name", "description",)
    list_filter = ("category", "spell_level")

    autocomplete_fields = ("category",)
    save_on_top = True

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Основное", {
            "fields": (("name", "slug"), ("category", "spell_level"), "image", "requirements", "special_components", "description",),
        }),
        ("Дополнительно", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at", "is_deleted", "deleted_at"),
        })
    )

    inlines = [SpellEffectInline]

    def get_queryset(self, request):
        return self.model.objects.unfiltered().select_related("category")

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:30px;border-radius:8px;" />')
        return "-"
    preview_image.short_description = "Превью"


@admin.register(SpellCategory)
class SpellCategoryAdmin(admin.ModelAdmin):
    list_display = ("preview_image", "name",)
    search_fields = ("name",)

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" style="max-height:50px;border-radius:8px;" />')
        return "-"
    preview_image.short_description = "Превью"

@admin.register(SpellEffect)
class SpellEffectAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

