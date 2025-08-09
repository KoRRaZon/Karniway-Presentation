from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView

from apps.wiki.forms import PostEditForm, PostCreateForm
from apps.wiki.models import Post


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
    form_class = PostCreateForm
    template_name = 'wiki/post_create.html'
    context_object_name = 'post'
    extra_context = {'title': 'Создание статьи'}

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)



class PostEditView(UpdateView):
    model = Post
    form_class = PostEditForm
    context_object_name = 'post'
    template_name = 'wiki/post_edit.html'
    extra_context = {'title': 'Редактирование статьи'}

    def get_object(self, **kwargs):
        return Post.objects.get(slug=self.kwargs['slug'])

    def get_success_url(self):
        return reverse_lazy('wiki:post_detail', kwargs={'slug': self.object.slug})