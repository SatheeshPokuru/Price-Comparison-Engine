import requests

from django.shortcuts import render

from .models import Product

import re

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from django.contrib.auth import authenticate, login, logout

from django.shortcuts import redirect

from django.contrib.auth.decorators import login_required

from .models import Wishlist

from .models import PriceHistory

from .models import PriceAlert

from .models import Wishlist

from .models import RecentlyViewed

from rest_framework.response import Response

from rest_framework.decorators import api_view

from .models import Product, Wishlist, PriceHistory, PriceAlert, RecentlyViewed
from .scraper import scrape_books, scrape_flipkart, scrape_croma
from .serializers import (
    ProductSerializer,
    WishlistSerializer,
    PriceAlertSerializer
)

from .serializers import (

    ProductSerializer,

    WishlistSerializer,

    PriceAlertSerializer,

    PriceHistorySerializer

)

from .serializers import ProductSerializer

def normalize_title(title):

    title = title.lower()

    title = re.sub(r'([a-z])([0-9])', r'\1 \2', title)

    title = re.sub(r'([0-9])([a-z])', r'\1 \2', title)

    title = " ".join(title.split())

    return title

def home(request):
    product = request.GET.get("product", "").strip()
    sort = request.GET.get("sort")
    source = request.GET.get("source")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    products = Product.objects.none()
    suggestions = Product.objects.all()[:20]
    lowest_price = None

    if product:

        # -------------------------
        # Search Database First
        # -------------------------
        products = Product.objects.all()

        for word in product.split():
            products = products.filter(title__icontains=word)

        # -------------------------
        # If Not Found → Fetch APIs
        # -------------------------
        if not products.exists():

            search_text = normalize_title(product)

            # FakeStore API
            try:
                response = requests.get(
                    "https://fakestoreapi.com/products",
                    timeout=10
                )

                for item in response.json():

                    if search_text in normalize_title(item["title"]):

                        Product.objects.get_or_create(
                            title=item["title"],
                            source="FakeStore",
                            defaults={
                                "price": item["price"],
                                "category": item["category"],
                                "image": item["image"],
                                "rating": item["rating"]["rate"],
                                "description": item["description"],
                            },
                        )

            except Exception as e:
                print("FakeStore Error:", e)

            # DummyJSON API
            try:
                response = requests.get(
                    "https://dummyjson.com/products",
                    timeout=10
                )

                for item in response.json()["products"]:

                    if search_text in normalize_title(item["title"]):

                        Product.objects.get_or_create(
                            title=item["title"],
                            source="DummyJSON",
                            defaults={
                                "price": item["price"],
                                "category": item["category"],
                                "image": item["thumbnail"],
                                "rating": item["rating"],
                                "description": item["description"],
                            },
                        )

            except Exception as e:
                print("DummyJSON Error:", e)

            # -------------------------
            # Scrape Flipkart
            # -------------------------
            try:
                for item in scrape_flipkart(product):

                    price = (
                        item["price"]
                        .replace("₹", "")
                        .replace(",", "")
                    )

                    Product.objects.get_or_create(
                        title=item["title"],
                        source="Flipkart",
                        defaults={
                            "price": float(price),
                            "category": "Electronics",
                            "image": item["image"],
                            "rating": 0,
                            "description": item["title"],
                            "product_url": item["link"],
                        },
                    )

            except Exception as e:
                print("Flipkart Error:", e)

            # -------------------------
            # Scrape Croma
            # -------------------------
            try:
                for item in scrape_croma(product):

                    price = (
                        item["price"]
                        .replace("₹", "")
                        .replace(",", "")
                        .strip()
                    )

                    Product.objects.get_or_create(
                        title=item["title"],
                        source="Croma",
                        defaults={
                            "price": float(price),
                            "category": "Mobiles",
                            "image": item["image"],
                            "rating": 0,
                            "description": item["title"],
                            "product_url": item["link"],
                        },
                    )

            except Exception as e:
                print("Croma Error:", e)

            # -------------------------
            # Scrape Books
            # -------------------------
            try:
                books = scrape_books(product)

                for item in books:

                    price = float(
                        item["price"].replace("£", "")
                    )

                    obj, created = Product.objects.get_or_create(
                        title=item["title"],
                        source="BooksToScrape",
                        defaults={
                            "price": price,
                            "category": "Books",
                            "image": item["image"],
                            "rating": 0,
                            "description": item["title"],
                            "product_url": item["link"],
                        },
                    )

                    # Price Tracking
                    if not created and obj.price != price:

                        old_price = obj.price

                        PriceHistory.objects.create(
                            product=obj,
                            price=price
                        )

                        if price < old_price:

                            wishlists = Wishlist.objects.filter(
                                product=obj
                            )

                            for wishlist in wishlists:

                                PriceAlert.objects.create(
                                    user=wishlist.user,
                                    product=obj,
                                    old_price=old_price,
                                    new_price=price
                                )

                        obj.price = price
                        obj.save()

            except Exception as e:
                print("Books Error:", e)

            # Refresh Search Results
            products = Product.objects.all()

            for word in product.split():
                products = products.filter(
                    title__icontains=word
                )

        # -------------------------
        # Source Filter
        # -------------------------
        if source:
            products = products.filter(source=source)

        # -------------------------
        # Price Filters
        # -------------------------
        if min_price:
            products = products.filter(
                price__gte=float(min_price)
            )

        if max_price:
            products = products.filter(
                price__lte=float(max_price)
            )

        # -------------------------
        # Sorting
        # -------------------------
        if sort == "low_to_high":
            products = products.order_by("price")

        elif sort == "high_to_low":
            products = products.order_by("-price")

        elif sort == "rating":
            products = products.order_by("-rating")

        # -------------------------
        # Lowest Price
        # -------------------------
        if products.exists():
            lowest_price = min(
                p.price for p in products
            )

    context = {
        "products": products,
        "searched": product,
        "lowest_price": lowest_price,
        "suggestions": suggestions,
    }

    return render(
        request,
        "products/home.html",
        context,
    )

from django.shortcuts import get_object_or_404

def product_detail(request, id):

    product = get_object_or_404(
        Product,
        id=id
    )

    if request.user.is_authenticated:

        recent = RecentlyViewed.objects.filter(
        user=request.user,
        product=product
        )

        if recent.exists():

            recent.delete()

        RecentlyViewed.objects.create(

            user=request.user,

            product=product

        )

    context = {
        "product": product
    }

    return render(
        request,
        "products/detail.html",
        context
    )


def register(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        if User.objects.filter(username=username).exists():

            return render(
                request,
                "products/register.html",
                {"error": "Username already exists"}
            )

        user = User.objects.create_user(
            username=username,
            password=password
        )

        login(request, user)

        return redirect("home")

    return render(
        request,
        "products/register.html"
    )

def user_login(request):

    if request.method == "POST":

        username = request.POST.get("username")

        password = request.POST.get("password")

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user:

            login(request, user)

            return redirect("home")

        return render(
            request,
            "products/login.html",
            {"error": "Invalid credentials"}
        )

    return render(
        request,
        "products/login.html"
    )


def user_logout(request):

    logout(request)

    return redirect("home")


@login_required
def add_to_wishlist(request, id):

    product = Product.objects.get(id=id)

    Wishlist.objects.get_or_create(

        user=request.user,

        product=product

    )

    return redirect(
        "product_detail",
        id=id
    )

@login_required
def wishlist(request):

    wishlist_items = Wishlist.objects.filter(
        user=request.user
    )

    context = {
        "wishlist_items": wishlist_items
    }

    return render(
        request,
        "products/wishlist.html",
        context
    )

@login_required
def remove_from_wishlist(request, id):

    wishlist_item = Wishlist.objects.get(
        id=id,
        user=request.user
    )

    wishlist_item.delete()

    return redirect("wishlist")

def price_history(request, id):

    product = Product.objects.get(id=id)

    history = PriceHistory.objects.filter(
        product=product
    ).order_by("-recorded_at")

    context = {

        "product": product,

        "history": history

    }

    return render(
        request,
        "products/price_history.html",
        context
    )

@login_required
def alerts(request):

    alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")

    return render(
        request,
        "products/alerts.html",
        {
            "alerts": alerts
        }
    )

@login_required
def dashboard(request):

    wishlist_count = Wishlist.objects.filter(
        user=request.user
    ).count()

    alert_count = PriceAlert.objects.filter(
        user=request.user
    ).count()

    recent_alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")[:5]

    recent_products = RecentlyViewed.objects.filter(
    user=request.user
    ).order_by("-viewed_at")[:5]

    history_count = PriceHistory.objects.count()

    context = {

        "wishlist_count": wishlist_count,

        "alert_count": alert_count,

        "history_count": history_count,

        "recent_alerts": recent_alerts,

        "recent_products" : recent_products
    }

    return render(
        request,
        "products/dashboard.html",
        context
    )

@api_view(["GET"])
def product_api(request):

    search = request.GET.get("search")

    source = request.GET.get("source")

    products = Product.objects.all()

    if search:

        products = products.filter(
            title__icontains=search
        )
    
    if source:

        products = products.filter(
        source=source
    )

    serializer = ProductSerializer(
        products,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def product_detail_api(request, id):

    product = Product.objects.get(id=id)

    serializer = ProductSerializer(product)

    return Response(
        serializer.data
    )

@api_view(["GET"])
def wishlist_api(request):

    if not request.user.is_authenticated:

        return Response(
            {
                "error": "Login required"
            },
            status=401
        )

    wishlist = Wishlist.objects.filter(
        user=request.user
    )

    serializer = WishlistSerializer(
        wishlist,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def alerts_api(request):

    if not request.user.is_authenticated:

        return Response(
            {
                "error": "Login required"
            },
            status=401
        )

    alerts = PriceAlert.objects.filter(
        user=request.user
    ).order_by("-created_at")

    serializer = PriceAlertSerializer(
        alerts,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def history_api(request):

    history = PriceHistory.objects.all().order_by(
        "-recorded_at"
    )

    serializer = PriceHistorySerializer(
        history,
        many=True
    )

    return Response(
        serializer.data
    )

@api_view(["GET"])
def product_history_api(request, id):

    product = Product.objects.get(id=id)

    history = PriceHistory.objects.filter(
        product_id=id
    ).order_by("-recorded_at")

    history_serializer = PriceHistorySerializer(
        history,
        many=True
    )

    return Response({

        "product": product.title,

        "current_price": product.price,

        "history": history_serializer.data

    })

