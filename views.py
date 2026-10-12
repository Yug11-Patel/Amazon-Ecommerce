import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Product, Order
from .serializers import ProductSerializer, OrderSerializer


# ---------------------------------------------------------
# SCRAPER PROCESS
# ---------------------------------------------------------

scraper_process = None


def get_scraper_paths():
    backend_dir = Path(__file__).resolve().parent.parent
    project_dir = backend_dir.parent
    scraper_dir = project_dir / "scraper"

    scraper_file = scraper_dir / "scraper.py"

    if os.name == "nt":
        python_file = scraper_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_file = scraper_dir / "venv" / "bin" / "python"

    return scraper_dir, scraper_file, python_file


class AdminScraperStartView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        global scraper_process

        if scraper_process is not None:
            if scraper_process.poll() is None:
                return Response(
                    {
                        "message": "Scraper is already running.",
                        "status": "running",
                    },
                    status=status.HTTP_200_OK,
                )

        scraper_dir, scraper_file, python_file = get_scraper_paths()

        if not scraper_file.exists():
            return Response(
                {
                    "error": f"Scraper file not found: {scraper_file}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        if not python_file.exists():
            return Response(
                {
                    "error": f"Scraper Python environment not found: {python_file}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        try:
            scraper_process = subprocess.Popen(
                [str(python_file), str(scraper_file)],
                cwd=str(scraper_dir),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )

            return Response(
                {
                    "message": "Amazon scraper started successfully.",
                    "status": "running",
                },
                status=status.HTTP_200_OK,
            )

        except Exception as error:
            scraper_process = None

            return Response(
                {
                    "error": f"Unable to start scraper: {str(error)}"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class AdminScraperStatusView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        global scraper_process

        if scraper_process is None:
            return Response(
                {
                    "status": "idle"
                },
                status=status.HTTP_200_OK,
            )

        return_code = scraper_process.poll()

        if return_code is None:
            return Response(
                {
                    "status": "running"
                },
                status=status.HTTP_200_OK,
            )

        if return_code == 0:
            return Response(
                {
                    "status": "completed"
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": "error",
                "return_code": return_code,
            },
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# PRODUCTS
# ---------------------------------------------------------

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]


class AdminProductListView(generics.ListAPIView):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAdminUser]


class AdminProductDeleteView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Product not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        product.delete()

        return Response(
            {"message": "Product deleted successfully."},
            status=status.HTTP_200_OK,
        )


# ---------------------------------------------------------
# ORDERS
# ---------------------------------------------------------

class OrderCreateView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        address = request.data.get("address")
        city = request.data.get("city")
        state = request.data.get("state")
        pincode = request.data.get("pincode")
        cart_items = request.data.get("cart_items", [])

        if not address or not city or not state or not pincode:
            return Response(
                {"error": "All delivery details are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not cart_items:
            return Response(
                {"error": "Cart is empty."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        total_amount = Decimal("0.00")

        for item in cart_items:
            price_text = str(item.get("price", ""))

            price_text = (
                price_text
                .replace("₹", "")
                .replace(",", "")
                .strip()
            )

            try:
                price = Decimal(price_text)
            except Exception:
                price = Decimal("0.00")

            try:
                quantity = int(item.get("quantity", 1))
            except Exception:
                quantity = 1

            total_amount += price * quantity

        order = Order.objects.create(
            user=request.user,
            total_amount=total_amount,
            address=address,
            city=city,
            state=state,
            pincode=pincode,
        )

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED,
        )


class OrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).order_by("-created_at")


class AdminOrderListView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAdminUser]
    queryset = Order.objects.all().order_by("-created_at")


class AdminOrderStatusUpdateView(APIView):
    permission_classes = [IsAdminUser]

    def patch(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        new_status = request.data.get("status")

        valid_statuses = [
            "Pending",
            "Confirmed",
            "Shipped",
            "Delivered",
            "Cancelled",
        ]

        if new_status not in valid_statuses:
            return Response(
                {"error": "Invalid order status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        order.status = new_status
        order.save()

        serializer = OrderSerializer(order)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )