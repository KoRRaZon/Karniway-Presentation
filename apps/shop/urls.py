from django.urls import path

from apps.shop.views import ProductDetailView, ProductUpdateView, ProductCreateView, ProductDeleteView, ProductListView
from apps.wiki.views import PostListView, PostCreateView, PostEditView, PostDeleteView

app_name = 'shop'

urlpatterns = [
    path('product_list', ProductListView.as_view(), name='product_list'),

    path('products/create', ProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('products/<slug:slug>/edit', ProductUpdateView.as_view(), name='product_edit'),
    path('products/<slug:slug>/delete', ProductDeleteView.as_view(), name='product_delete'),

]