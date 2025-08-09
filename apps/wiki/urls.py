from django.urls import path

from apps.wiki.views import PostListView, PostDetailView, PostCreateView, PostEditView

app_name = 'wiki'


urlpatterns = [
    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<slug:slug>/edit', PostEditView.as_view(), name='post_edit'),
]