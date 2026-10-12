from rest_framework import serializers

from .models import Product, Order


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "price",
            "rating",
            "reviews",
            "image",
            "product_url",
        ]


class OrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = [
            "id",
            "user",
            "total_amount",
            "address",
            "city",
            "state",
            "pincode",
            "status",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "user",
            "total_amount",
            "status",
            "created_at",
        ]