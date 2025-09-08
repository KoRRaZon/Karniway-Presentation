from django.db import transaction
from django.db.models import F
from apps.shop.models import Product, Cart, CartItem

class CartService:
    def __init__(self, request):
        self.request = request
        self.user = request.user if request.user.is_authenticated else None

    def get_or_create_cart(self):
        cart = Cart.objects.filter(user=self.user).first() if self.user else None
        if not cart:
            cart = Cart.objects.create(user=self.user)
        return cart

    @transaction.atomic
    def add(self, product: Product, quantity: int = 1):
        cart = self.get_or_create_cart()
        # валидация остатков
        if product.quantity < quantity:
            raise ValueError("Недостаточно товара на складе")

        item, created = CartItem.objects.select_for_update().get_or_create(
            cart=cart, product=product,
            defaults={'quantity': quantity, 'unit_price': product.price, 'unit_prom_price': product.prom_price}
        )
        if not created:
            item.quantity = F('quantity') + quantity
            item.save()
            item.refresh_from_db()
        return cart