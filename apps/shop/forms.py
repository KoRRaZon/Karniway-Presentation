from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory

from apps.shop.models import Product, ProductImage


class ProductForm(forms.Form):
    class Meta:
        model = Product
        fields = ['name', 'category', 'description', 'quantity', 'price', 'prom_price']


class ProductImageForm(forms.Form):
    class Meta:
        model = Product
        fields = ['product', 'image', 'is_main', 'position']


class BaseProductImageFormset(forms.BaseInlineFormSet):
    MAX_IMAGES = 5

    def clean(self):
        super().clean()
        if any(form.errors for form in self.forms):
            return
        # отбираем активные формы, без пометок на удаление
        active_forms = [f for f in self.forms if not getattr(f, 'cleaned_data', {}).get('DELETE', False) and f.cleaned_data.get('image') or f.instance.pk]

        if len(active_forms) > self.MAX_IMAGES:
            return forms.ValidationError(f'Максимум {self.MAX_IMAGES} изображений на товар')
        # строгая гарантия только одной обложки
        mains = [f for f in active_forms if f.cleaned_data.get('is_main') or (f.instance.pk and f.instance.is_main and not f.cleaned_data.get('is_main') is False)]

        if len(mains) > 1:
            return forms.ValidationError(f'Товар может содержать только одну обложку')

        # если обложка не была отмечена - автоматически делаем первую картинку обложкой
        if len(mains) == 0 and active_forms:
            active_forms[0].cleaned_data['is_main'] = True


ProductImageFormset = inlineformset_factory(
    parent_model = Product,
    model = ProductImage,
    form = ProductImageForm,
    formset = BaseProductImageFormset,
    fields = ['image', 'is_main', 'position'],
    extra = 4,
    can_delete = True,
    max_num = 5,
    validate_max = True,
)






