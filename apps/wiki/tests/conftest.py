import pytest
from model_bakery import baker

@pytest.fixture
def category():
    """
        Быстро создаёт категорию для Creature.
        model_bakery автоматически заполнит обязательные поля.
    """
    return baker.make("wiki.CreatureCategory")

@pytest.fixture
def creature_factory(category):
    """
    Фабрика для создания Creature с дефолтными валидными данными.
    Можно передавать оверрайды: creature_factory(name="Imp")
    """
    def _make(**kwargs):
        base = {
            "name": "Goblin",
            "slug": None,  # пусть save() сам сгенерит
            "description": "Small but vicious.",
            "image": None,
            "category": category,
            "health": 7,
            "armor_class": 13,
            "mastery": 2,  # в твоих choices это int 1..10, ок
            "speed": 30,
            "size": ("tiny", "Tiny"),
            "saving_throws": "",
            "skills": "",
            "dangerous_level": 1,  # ВНИМАНИЕ: 1..20 — валидно
            "strength": 10, "dexterity": 12, "body_condition": 10,
            "intelligence": 8, "wisdom": 8, "charisma": 8,
        }
        base.update(kwargs)
        return baker.make("wiki.Creature", **base)
    return _make