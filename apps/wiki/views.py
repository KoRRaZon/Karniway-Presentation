from django.db import transaction
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView

from apps.wiki.forms import CreatureForm, CreatureAttackFormSet, \
    CreaturePassiveFormSet, SpellEffectFormSet, SpellForm, PostForm
from apps.wiki.models import Post, Creature, Spell, SpellEffectLink, News


class NewsListView(ListView):
    model = News
    context_object_name = 'news'
    template_name = 'home_page.html'
    extra_context = {'title': 'Главная страница'}


# POST: List, Detail, Create, Edit views

class PostListView(ListView):
    model = Post
    template_name = 'wiki/posts_list.html'
    context_object_name = 'posts'
    extra_context = {'title': 'Статьи'}


class PostDetailView(DetailView):
    model = Post
    template_name = 'wiki/post_detail.html'
    context_object_name = 'post'

    def get_object(self):
        return Post.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.title}'
        return context


class PostCreateView(CreateView):
    model = Post
    form_class = PostForm
    template_name = 'wiki/post_create.html'
    context_object_name = 'post'
    extra_context = {'title': 'Создание статьи'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class PostEditView(UpdateView):
    model = Post
    form_class = PostForm
    context_object_name = 'post'
    template_name = 'wiki/post_create.html'
    extra_context = {'title': 'Редактирование статьи'}

    def get_object(self, **kwargs):
        return Post.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy('wiki:post_detail', kwargs={'slug': self.object.slug})


class PostDeleteView(DeleteView):
    model = Post
    context_object_name = 'post'
    template_name = 'wiki/post_delete.html'
    extra_context = {'title': 'Удаление статьи'}
    success_url = reverse_lazy('wiki:post_list')


# Существа. Просмотр списком/детально, создание, редактирование и удаление.

class CreatureListView(ListView):
    model = Creature
    template_name = 'wiki/creature_list.html'
    context_object_name = 'creatures'
    extra_context = {'title': 'Бестиарий'}
    paginate_by = 6


class CreatureDetailView(DetailView):
    model = Creature
    template_name = 'wiki/creature_detail.html'
    context_object_name = 'creature'

    def get_object(self, **kwargs):
        return Creature.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name}'
        return context


class CreatureCreateView(CreateView):
    model = Creature
    form_class = CreatureForm
    template_name = 'wiki/creature_create.html'
    extra_context = {'title': 'Создание существа'}
    success_url = reverse_lazy('wiki:creature_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['attack_formset'] = CreatureAttackFormSet(self.request.POST, prefix="attack")
            context['passive_formset'] = CreaturePassiveFormSet(self.request.POST, prefix="passive")
        else:
            context['attack_formset'] = CreatureAttackFormSet(prefix="attack")
            context['passive_formset'] = CreaturePassiveFormSet(prefix="passive")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        attack_formset = context['attack_formset']
        passive_formset = context['passive_formset']

        if not attack_formset.is_valid() or not passive_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            attack_formset.instance = self.object
            passive_formset.instance = self.object
            attack_formset.save()
            passive_formset.save()

        return super().form_valid(form)


class CreatureUpdateView(UpdateView):
    model = Creature
    form_class = CreatureForm
    template_name = 'wiki/creature_create.html'
    extra_context = {'title': 'Редактирование существа'}
    success_url = reverse_lazy('wiki:creature_list')

    def get_object(self, **kwargs):
        return Creature.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        creature = self.object

        if self.request.method == 'POST':
            context['attack_formset'] = CreatureAttackFormSet(self.request.POST, instance=creature, prefix="attack")
            context['passive-formset'] = CreaturePassiveFormSet(self.request.POST, instance=creature, prefix="passive")
        else:
            context['attack_formset'] = CreatureAttackFormSet(instance=creature, prefix="attack")
            context['passive_formset'] = CreaturePassiveFormSet(instance=creature, prefix="passive")

        return context

    def form_valid(self, form):
        context = self.get_context_data()
        attack_formset = context['attack_formset']
        passive_formset = context['passive_formset']

        if not attack_formset.is_valid() or not passive_formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            attack_formset.instance = self.object
            passive_formset.instance = self.object
            attack_formset.save()
            passive_formset.save()

        return super().form_valid(form)


class CreatureDeleteView(DeleteView):
    model = Creature
    template_name = 'wiki/creature_delete.html'
    context_object_name = 'creature'
    success_url = reverse_lazy('wiki:creature_list')


# ЗАКЛИНАНИЯ
class SpellListView(ListView):
    model = Spell
    template_name = 'wiki/spell_list.html'
    context_object_name = 'spells'
    extra_context = {'title': 'Заклинания'}
    paginate_by = 6


class SpellDetailView(DetailView):
    model = Spell
    template_name = 'wiki/spell_detail.html'
    context_object_name = 'spell'

    def get_queryset(self):
        return Spell.objects.select_related('category').prefetch_related('effects')

    def get_object(self, **kwargs):
        return Spell.objects.get(slug=self.kwargs['slug'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'{self.object.name}'
        context['effect_links'] = (SpellEffectLink.objects
                                   .select_related('effect')
                                   .filter(spell=self.object)
                                   .order_by('pk'))

        return context

class SpellCreateView(CreateView):
    model = Spell
    form_class = SpellForm
    template_name = 'wiki/spell_create.html'
    extra_context = {'title': 'Создание заклинания'}


    def get_success_url(self):
        return reverse('wiki:spell_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['effect_formset'] = SpellEffectFormSet(self.request.POST, prefix="eff")
        else:
            context['effect_formset'] = SpellEffectFormSet(prefix="eff")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['effect_formset']

        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()

        return super().form_valid(form)


class SpellUpdateView(UpdateView):
    model = Spell
    form_class = SpellForm
    template_name = 'wiki/spell_create.html'
    extra_context = {'title': 'Редактирование заклинания'}

    def get_success_url(self):
        return reverse('wiki:spell_detail', kwargs={'slug': self.object.slug})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            context['effect_formset'] = SpellEffectFormSet(self.request.POST, instance=self.object, prefix="eff")
        else:
            context['effect_formset'] = SpellEffectFormSet(instance=self.object, prefix="eff")
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        formset = context['effect_formset']

        if not formset.is_valid():
            return self.form_invalid(form)

        with transaction.atomic():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
        return super().form_valid(form)


class SpellDeleteView(DeleteView):
    model = Spell
    template_name = 'wiki/spell_delete.html'
    context_object_name = 'spell'
    extra_context = {'title': 'Удаление заклинания'}
    success_url = reverse_lazy('wiki:spell_list')







