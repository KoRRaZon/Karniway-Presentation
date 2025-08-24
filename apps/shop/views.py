from django.contrib import messages
from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.shop.forms import ProductForm, ProductImageFormset
from apps.shop.models import Product


class ProductListView(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'shop/product_list.html'
    extra_context = {'title': 'Страница просмотра товаров'}


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product_detail.html'

    def get_object(self, *args, **kwargs):
        return Product.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['can_edit'] = True if user.is_authenticated and (user.is_staff or self.object.user == user) else False
        context['title'] = self.object.name
        return context


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/product_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['images_formset'] = ProductImageFormset(self.request.POST, self.request.FILES)
        else:
            context['images_formset'] = ProductImageFormset()
        context['title'] = 'Создание товара'
        context['mode'] = 'create'
        return context

    @transaction.atomic
    def form_valid(self, form):
        # привязываем пользователя и сохраняем родителя
        form.instance.user = self.request.user
        response = super().form_valid(form)


        images_formset = ProductImageFormset(self.request.POST, self.request.FILES, instance = self.object)

        if images_formset.is_valid():
            images_formset.save()
            messages.success(self.request, 'Товар успешно создан.')
            return response
        else:
            # если дочерний формсет невалидный - откатываем и рендерим форму с ошибками
            transaction.set_rollback(True)
            context = self.get_context_data(form=form)
            context['images_formset'] = images_formset
            return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy('shop:product_detail', kwargs={'slug': self.object.slug})


class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'shop/product_form.html'
    # авто-поиск object по slug
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # редактировать можно только свои товары
        return Product.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['images_formset'] = ProductImageFormset(self.request.POST, self.request.FILES, instance=self.object)
        else:
            context['images_formset'] = ProductImageFormset(instance=self.object)
        context['title'] = 'Изменение товара'
        context['mode'] = 'update'
        return context

    @transaction.atomic
    def form_valid(self, form):
        response = super().form_valid(form)
        images_formset = ProductImageFormset(self.request.POST, self.request.FILES, instance=self.object)

        if images_formset.is_valid():
            images_formset.save()
            messages.success(self.request, 'Изменения успешно сохранены.')
            return response
        else:
            transaction.set_rollback(True)
            context = self.get_context_data(form=form)
            context['images_formset'] = images_formset
            return self.render_to_response(context)

    def get_success_url(self):
        return reverse_lazy('product_detail', kwargs={'slug': self.object.slug})


class ProductDeleteView(DeleteView):
    model = Product
    context_object_name = 'product'
    template_name = 'shop/product_confirm_delete.html'
    extra_context = {'title': 'Удаление товара'}
    success_url = reverse_lazy('shop:product_list')

    def get_object(self, *args, **kwargs):
        return Product.objects.get(slug=self.kwargs['slug'])










