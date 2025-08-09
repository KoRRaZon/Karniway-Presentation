from uuid import uuid4
from pytils.translit import slugify

def unique_slugify(instance, slug, slug_field):
    """
    Создает слаг объекта, гарантируя уникальность и читаемость

    """
    model = instance.__class__
    base_slug = slugify(slug_field if slug_field else slug)
    unique_slug = base_slug

    while model.objects.filter(slug=unique_slug).exists():
        unique_slug = f'{base_slug}-{uuid4().hex[:4]}'
    return unique_slug




