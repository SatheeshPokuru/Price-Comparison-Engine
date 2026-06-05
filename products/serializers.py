from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:

        model = Product

        fields = "__all__"

from .models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):

    product_title = serializers.CharField(
        source="product.title"
    )

    product_price = serializers.FloatField(
        source="product.price"
    )

    class Meta:

        model = Wishlist

        fields = [

            "id",

            "product",

            "product_title",

            "product_price"

        ]

from .models import PriceAlert


class PriceAlertSerializer(serializers.ModelSerializer):

    product_title = serializers.CharField(
        source="product.title"
    )

    class Meta:

        model = PriceAlert

        fields = [

            "id",

            "product",

            "product_title",

            "old_price",

            "new_price",

            "created_at"

        ]

from .models import PriceHistory


class PriceHistorySerializer(serializers.ModelSerializer):

    product_title = serializers.CharField(
        source="product.title"
    )

    class Meta:

        model = PriceHistory

        fields = [

            "id",

            "product",

            "product_title",

            "price",

            "recorded_at"

        ]