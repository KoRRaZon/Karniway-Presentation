import pytest
from django.db import IntegrityError
from model_bakery import baker

from apps.common.utils import unique_slugify

pytestmark = pytest.mark.django_db # весь файл работает с тестовой БД


def test_str_returns_name(creature_factory):
    c = creature_factory(name="Тролль", slug=None)
    assert str(c) == "Тролль"

def test_creature_slug_create_from_name_when_empty(creature_factory):
    c = creature_factory(name="Alpha-wolf", slug=None)
    assert c.slug == unique_slugify(c.name) # unique_slugify использует uuid из-за чего точный результат нельзя предсказать

def test_save_keeps_slug_if_provided(creature_factory):
    c = creature_factory(name="Alpha-wolf", slug="alpha-wolf")
    assert c.slug.startswith("alpha-wolf")

def test_slug_is_unique_for_same_names(creature_factory):
    c = creature_factory(name="Alpha-wolf", slug=None)
    c2 = creature_factory(name="Alpha-wolf", slug=None)

    assert c.slug != c2.slug
    assert c.slug.startswith("alpha-wolf")
    assert c2.slug.startswith("alpha-wolf")

def test_category_relation_required(baker):
    cat = baker.make("wiki.CreatureCategory")
    c = baker.make("wiki.Creature", category=cat, name="Wolf", slug=None, description="...")
    assert c.category == cat

def test_image_is_optional(creature_factory):
    c = creature_factory(image=None)
    assert c.image.name in (None, "")



# Spell, SpellCategory

