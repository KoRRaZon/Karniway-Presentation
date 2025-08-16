import pytest
from django.urls import reverse
from model_bakery import baker
from model_bakery.recipe import seq

pytestmark = pytest.mark.django_db


def test_spell_list_renders_template_and_context(client):
    """
    Базовая проверка: страница списка отдается 200,
    рендерит ожидаемый шаблон и кладет объекты в контекст под именем 'spells'.
    """
    # Arrange: создадим несколько заклинаний. bakery сам создаст связанные объекты (категории и т.п.)
    baker.make("apps.wiki.Spell", name=seq("Spell-", start=1), _quantity=3)

    # Act
    url = reverse("wiki:spell_list")
    response = client.get(url)

    assert response.status_code == 200
    assert "wiki/spell_list.html" in [t.name for t in response.templates]
    assert "spells" in response.context
    assert len(response.context["spells"]) == 3
    assert response.context["title"] == 'Заклинания'


def test_spell_list_pagination_first_page_has_6_items(client):
    """
    Вьюха paginate_by = 6. Создаем 8 объектов и проверяем:
    - на первой странице 6 элементов,
    - в контексте есть paginator/page_obj.
    """
    baker.make("wiki.Spell", name=seq("Spell-", start=1), _quantity=8)
    url = reverse("wiki:spell_list")
    response = client.get(url)

    assert response.status_code == 200
    assert "spells" in response.context
    assert len(response.context["spells"]) == 6
    assert "paginator" in response.context
    assert "page_obj" in response.context
    assert response.context["page_obj"].number == 1
    assert response.context["paginator"].num_pages == 2

def test_spell_list_pagination_second_page_has_remaining_items(client):
    baker.make("wiki.Spell", name=seq("Spell-", start=1), _quantity=8)
    url = reverse("wiki:spell_list")
    response = client.get(url, {'page': 2})

    assert response.status_code == 200
    assert len(response.context["spells"]) == 2
    assert response.context['page_obj'].number == 2


