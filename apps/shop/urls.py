from django.urls import path

from apps.shop.views import ProductDetailView, ProductUpdateView, ProductCreateView, ProductDeleteView, ProductListView, \
    ProductVoteView, ProductReviewDeleteView, ProductReviewListView, ProductReviewCreateView

app_name = 'shop'

urlpatterns = [
    path('product_list', ProductListView.as_view(), name='product_list'),

    path('products/create', ProductCreateView.as_view(), name='product_create'),
    path('products/<slug:slug>', ProductDetailView.as_view(), name='product_detail'),
    path('products/<slug:slug>/vote/', ProductVoteView.as_view(), name='product_vote'),
    path('products/<slug:slug>/edit', ProductUpdateView.as_view(), name='product_edit'),
    path('products/<slug:slug>/delete', ProductDeleteView.as_view(), name='product_delete'),

    path('products/<slug:slug>/reviews/create', ProductReviewCreateView.as_view(), name='product_review_create'),
    path('products/<slug:slug>/reviews/list', ProductReviewListView.as_view(), name='product_review_list'),
    path('products/<slug:slug>/reviews/<uuid:pk>/delete/', ProductReviewDeleteView.as_view(), name='product_review_delete'),
]