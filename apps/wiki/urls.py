from django.urls import path

from apps.wiki.views import PostListView, PostDetailView, PostCreateView, PostEditView, \
    CreatureListView, CreatureDetailView, CreatureCreateView, SpellDetailView, SpellListView, SpellCreateView, \
    NewsListView, CreatureDeleteView, SpellDeleteView, PostDeleteView, CreatureUpdateView, SpellUpdateView

app_name = 'wiki'


urlpatterns = [
    path('', NewsListView.as_view(), name='home_page'),

    path('posts/', PostListView.as_view(), name='post_list'),
    path('posts/create/', PostCreateView.as_view(), name='post_create'),
    path('posts/<slug:slug>/', PostDetailView.as_view(), name='post_detail'),
    path('posts/<slug:slug>/edit', PostEditView.as_view(), name='post_edit'),
    path('posts/<slug:slug>/delete', PostDeleteView.as_view(), name='post_delete'),

    path('creatures/', CreatureListView.as_view(), name='creature_list'),
    path('creatures/create/', CreatureCreateView.as_view(), name='creature_create'),
    path('creatures/<slug:slug>/', CreatureDetailView.as_view(), name='creature_detail'),
    path('creatures/<slug:slug>/edit', CreatureUpdateView.as_view(), name='creature_edit'),
    path('creatures/<slug:slug>/delete', CreatureDeleteView.as_view(), name='creature_delete'),

    path('spells/', SpellListView.as_view(), name='spell_list'),
    path('spells/create/', SpellCreateView.as_view(), name='spell_create'),
    path('spells/<slug:slug>/', SpellDetailView.as_view(), name='spell_detail'),
    path('spells/<slug:slug>/edit', SpellUpdateView.as_view(), name='spell_edit'),
    path('spells/<slug:slug>/delete', SpellDeleteView.as_view(), name='spell_delete')
]