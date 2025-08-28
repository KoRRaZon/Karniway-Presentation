import json

from django.contrib import messages
from django.core.paginator import Paginator
from django.db import transaction, IntegrityError
from django.db.models import F
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from apps.shop.forms import ProductForm, ProductImageFormset, ProductReviewForm
from apps.shop.models import Product, ProductRating, ProductVote, ProductReview


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

        # гарантируем наличие связного объекта рейтинга
        ProductRating.objects.get_or_create(product=self.object)

        # первая страница отзывов
        queryset = (ProductReview.objects
                    .filter(product=self.object)
                    .select_related('user')
                    .only('id', 'text', 'created_at', 'user', 'user__id'))
        page = Paginator(queryset, 10).get_page(self.request.GET.get('page', 1))

        context.update({
            'can_edit': bool(user.is_authenticated and (user.is_staff or self.object.user == user)),
            'title': self.object.name,
            'reviews_page': page,
            'review_form': ProductReviewForm(),
        })
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


class ProductVoteView(View):
    """
    POST /shop/products/<slug>/vote/
    Принимает value = 1 или -1 и:
      - создаёт/меняет/снимает голос пользователя,
      - атомарно обновляет агрегаты ProductRating,
      - возвращает либо HTML-фрагмент (_rating.html) для HTMX,
        либо JSON, либо редирект на product_detail (PRG).
    """
    http_method_names = ['post']

    def post(self, request, slug):
        # 1) авторизация
        user = request.user
        if not user.is_authenticated:
            # для HTMX — 401 (в шаблоне у нас перехват и редирект на логин)
            if request.headers.get('HX-Request'):
                return JsonResponse({'detail': 'Требуется авторизация'}, status=401)
            return redirect('/accounts/login/?next=' + request.path)

        # 2) валидация value
        try:
            new_value = int(request.POST.get('value'))
        except (TypeError, ValueError):
            return JsonResponse({'detail': 'Bad value'}, status=400)
        if new_value not in (1, -1):
            return JsonResponse({'detail': 'Bad value'}, status=400)

        product = Product.objects.get(slug=slug)

        # 3) меняем голос + пересчитываем рейтинг
        with transaction.atomic():
            # гарантируем наличие агрегатов и лочим строку до конца транзакции
            rating_obj, _ = ProductRating.objects.select_for_update().get_or_create(product=product)

            # Пытаемся получить голос; если его нет — создаём, но безопасно обрабатываем гонку
            vote = ProductVote.objects.select_for_update().filter(product=product, user=user).first()

            if vote is None:
                try:
                    ProductVote.objects.create(product=product, user=user, value=new_value)
                except IntegrityError:
                    # Между проверкой и create другой запрос успел создать запись
                    vote = ProductVote.objects.select_for_update().get(product=product, user=user)
                else:
                    if new_value == 1:
                        ProductRating.objects.filter(pk=rating_obj.pk).update(up_count = F('up_count') + 1)
                    else:
                        ProductRating.objects.filter(pk=rating_obj.pk).update(down_count = F('down_count') + 1)
                rating_obj.refresh_from_db(fields=['up_count', 'down_count'])
                rating_obj.recompute(save=True)

            if vote is not None:
                if vote.value == new_value:
                    # повторное нажатие — снимаем голос
                    vote.delete()
                    rating_obj.refresh_from_db(fields=['up_count', 'down_count'])
                    if new_value == 1 and rating_obj.up_count > 0:
                        ProductRating.objects.filter(pk=rating_obj.pk).update(up_count = F('up_count') - 1)
                    elif new_value == -1 and rating_obj.down_count > 0:
                        rating_obj.refresh_from_db(fields=['down_count'])
                        ProductRating.objects.filter(product=product).update(down_count = F('down_count') - 1)

                else:
                    # переключение +1 <-> -1
                    old_value = vote.value
                    vote.value = new_value
                    vote.save(update_fields=['value'])
                    if old_value == 1 and new_value == -1:
                        ProductRating.objects.filter(pk=rating_obj.pk).update(
                            up_count = F('up_count') - 1,
                            down_count = F('down_count') + 1
                        )
                    elif old_value == -1 and new_value == 1:
                        ProductRating.objects.filter(pk=rating_obj.pk).update(
                            up_count=F('up_count') + 1,
                            down_count=F('down_count') - 1
                        )
                rating_obj.refresh_from_db(fields=['up_count', 'down_count'])
                rating_obj.recompute(save=True)

        # 4) ответ: HTML (HTMX) / JSON / PGR
        user_vote_value = ProductVote.objects.filter(product=product, user=user).values_list('value', flat=True).first()

        # HTMX - возвращаем фрагмент блока рейтинга
        if request.headers.get('HX-Request'):
            return render(request, 'shop/partials/_rating.html', {'p': product, 'user_vote_value': user_vote_value})

        # JSON (если нужно)
        if 'application/json' in request.headers.get('Accept', ''):
            return JsonResponse({
                'rating': str(rating_obj.rating),
                'up': rating_obj.up_count,
                'down': rating_obj.down_count,
                'user_vote': int(user_vote_value) if user_vote_value is not None else 0,
            })

        # Обычный редирект назад на товар с обновлением страницы
        return redirect(product.get_absolute_url())

@method_decorator(require_POST, name='dispatch')
class ProductReviewCreateView(CreateView):
    def post(self, request, slug):
        # проверка авторизации
        if not request.user.is_authenticated:
            if request.headers.get('HX-Request'):
                return JsonResponse({'detail': 'Требуется авторизация'}, status=401)
            return redirect('/accounts/login/?next=' + request.path)

        product = Product.objects.get(slug=slug)
        form = ProductReviewForm(request.POST)

        if not form.is_valid():
            # HTMX: отдать форму с ошибками (маленький фрагмент)
            if request.headers.get('HX-Request'):
                response = render(request, 'shop/partials/_review_form.html', {'p': product, 'form': form}, status=400)
                response['HX-Retarget'] = '#reviews-form'
                response['HX-Reswap'] = 'outerHTML'
                return response

            # return redirect(product.get_absolute_url() + '#reviews')

        review = form.save(commit=False)
        review.product = product
        review.user = request.user
        review.save()

        # HTMX: вернуть готовую карточку отзыва + всплывающее сообщение
        if request.headers.get('HX-Request'):
            response = render(request, 'shop/partials/_review_item.html', {'review': review, 'can_delete': True})
            response['HX-Trigger'] = json.dumps({'toast': 'Отзыв добавлен.'})
            return response

        messages.success(request, 'Отзыв добавлен.')
        return redirect(product.get_absolute_url() + '#reviews')


class ProductReviewListView(ListView):
    def get(self, request, slug):
        product = Product.objects.get(slug=slug)
        page_num = request.GET.get('page', 1)

        queryset = (ProductReview.objects
                    .filter(product=product)
                    .select_related('user')
                    .only('pk', 'text', 'created_at', 'user', 'user__pk'))

        paginator = Paginator(queryset, 10)
        page = paginator.get_page(page_num)

        # Возвращаем только элементы + “кнопку ещё” как OOB-фрагмент
        return render(request, 'shop/partials/_review_items.html', {
            'page': page,
            'product': product,
        })

@method_decorator(require_POST, name='dispatch')
class ProductReviewDeleteView(View):
    def post(self, request, slug, pk):
        product = Product.objects.get(slug=slug)
        review = ProductReview.objects.get(pk=pk, product=product)

        if not (request.user.is_staff or (review.user_id == request.user.id)):
            return JsonResponse({'detail': 'Forbidden.'}, status=403)

        review.delete()

        if request.headers.get('HX-Request'):
            # 204 + событие для тоста. Элемент удаляем на клиенте hx-swap="outerHTML"
            response = HttpResponse(status=204)
            response['HX-Trigger'] = json.dumps({'toast': 'Отзыв удален.'})
            return response

        messages.success(request, 'Отзыв удален.')
        return redirect(product.get_absolute_url() + '#reviews')










