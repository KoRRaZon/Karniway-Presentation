from django.test import TestCase
from django.urls import reverse

from apps.wiki.models import Spell, SpellCategory, SpellEffect

class WikiURLTests(TestCase):
    def setUp(self):
        print("")
        print("Пробуем")

    def tearDown(self):

        print("Завершено")

    def test_spell_list(self):
        response = self.client.get(reverse('wiki:spell_list'))
        self.assertEqual(response.status_code, 200)


# apps/wiki/tests/test_spell_list_basic.py
from django.test import TestCase
from django.urls import reverse

from apps.wiki.models import Spell, SpellCategory


# (необязательно) модульные хуки. Django обычно глушит вывод,
# но оставлю как пример: они вызываются один раз на модуль.
def setUpModule():
    print("== Начало тестов SpellListView ==")

def tearDownModule():
    print("== Конец тестов SpellListView ==")


class TestSpellViews(TestCase):
    """
    Базовые (smoke) тесты для списка заклинаний без фильтров и сложной логики.
    Используем TestCase — Django создаёт тестовую БД, каждый тест изолирован.
    """

    def setUp(self):
        print("")
        print("Пробуем")

    def tearDown(self):

        print("Завершено")

    @classmethod
    def setUpTestData(cls):
        """
        setUpTestData() выполняется ОДИН раз на класс.
        Всё, что создадим здесь через ORM, доступно во всех тестах,
        а изменения каждого теста откатываются транзакцией.

        ВАЖНО: используем cls.<attr>, т.к. это атрибуты КЛАССА.
        В самих тестах будем обращаться как self.<attr> — Python найдёт на классе.
        """
        # 1) Базовые данные: категория
        cls.category = SpellCategory.objects.create(name='Магия')

        # 2) Два заклинания. Нам не нужна реальная картинка для списка,
        # поэтому image можно не задавать (или задать строкой-путём, если шаблон проверяет .url).
        cls.spell1 = Spell.objects.create(
            name='Проверочное заклинание',
            # slug можно не задавать — модель сама сгенерит в save(), но зададим для прозрачности
            slug='proverochnoe-zaklinanie',
            category=cls.category,
            description='Описание',
            spell_level='заговор',
            requirements='отсутствуют',
            special_components='отсутствуют',
            # image=None по умолчанию — в шаблоне должна быть ветка {% if spell.image %} ... {% else %} ...
        )

        cls.spell2 = Spell.objects.create(
            name='Искра',
            slug='iskra',
            category=cls.category,
            description='Другое описание',
            spell_level='1',
            requirements='отсутствуют',
            special_components='отсутствуют',
        )

    def test_spell_list_renders_and_contains(self):
        """
        Проверяем три вещи:
        1) View открывается (HTTP 200) и использует правильный шаблон.
        2) Пагинация правильно определена (у нас всего 2 объекта, paginate_by=6 -> is_paginated=False).
        3) В контексте лежат ИМЕННО наши объекты (по pk), причём в том месте, где их ожидает ListView.
        """
        # --- Act: идём на URL списка по имени маршрута
        url = reverse('wiki:spell_list')
        response = self.client.get(url)

        # --- Assert: код ответа и шаблон
        self.assertEqual(response.status_code, 200, "ListView должен отдавать 200 OK")
        self.assertTemplateUsed(response, 'wiki/spell_list.html')

        # --- Assert: признак пагинации
        # ListView с paginate_by добавляет в контекст:
        #   - is_paginated (bool)
        #   - paginator (Paginator)
        #   - page_obj (Page)
        #   - context_object_name (у нас 'spells') -> список объектов текущей страницы
        self.assertIn('is_paginated', response.context)
        self.assertFalse(
            response.context['is_paginated'],
            "При 2 объектах и paginate_by=6 пагинация не должна включаться"
        )

        # --- Важно: 'page_obj' — ЭТО Page; у него есть .object_list (список/QuerySet текущей страницы).
        page = response.context['page_obj']
        objects_on_page = list(page.object_list)  # приводим к списку ради явности

        self.assertEqual(
            len(objects_on_page), 2,
            "На странице должно быть 2 объекта (мы создали 2 и пагинация не порежет)"
        )

        # Сравниваем состав по pk (это надёжнее, чем сравнивать объекты напрямую)
        ids_on_page = {obj.pk for obj in objects_on_page}
        self.assertSetEqual(
            ids_on_page, {self.spell1.pk, self.spell2.pk},
            "В списке должны быть именно наши созданные объекты"
        )

        # --- Дополнительно: context_object_name ('spells') должен указывать на тот же набор, что и page_obj.object_list.
        # В Django ListView 'spells' — это не Page, а сам object_list для текущей страницы.
        spells_ctx = list(response.context['spells'])  # приводим к списку — так универсальнее
        self.assertListEqual(
            spells_ctx, objects_on_page,
            "'spells' в контексте должен соответствовать page_obj.object_list"
        )

    def test_html_contains_spell_names(self):
        """
        Простейшая проверка HTML: на отрендеренной странице действительно есть имена наших заклинаний.
        Это smoke-проверка, что шаблон выводит поля объектов (названия не «теряются» условиями).
        """
        response = self.client.get(reverse('wiki:spell_list'))
        self.assertContains(response, self.spell1.name)
        self.assertContains(response, self.spell2.name)

