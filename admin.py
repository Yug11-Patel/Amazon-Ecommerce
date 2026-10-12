from django.contrib import admin

from .models import Product, Order


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "price",
        "rating",
        "reviews",
    )

    search_fields = (
        "name",
    )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "user",
        "total_amount",
        "status",
        "city",
        "state",
        "created_at",
    )

    list_filter = (
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "city",
        "state",
        "pincode",
    )

    ordering = (
        "-created_at",
    )

    fields = (
        "user",
        "total_amount",
        "address",
        "city",
        "state",
        "pincode",
        "status",
        "created_at",
    )

    readonly_fields = (
        "user",
        "total_amount",
        "created_at",
    )